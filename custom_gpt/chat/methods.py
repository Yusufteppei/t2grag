import dotenv
dotenv.load_dotenv()
import os
import logging
import openai
import pinecone
import time
from django.conf import settings
from custom_gpt.decorators import measure_latency_and_tokens
import fitz  # PyMuPDF
import pdfplumber
import requests

from label_studio_sdk.client import LabelStudio

LABEL_STUDIO_API_KEY = settings.LABEL_STUDIO_API_KEY
LABEL_STUDIO_URL = settings.LABEL_STUDIO_URL



ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_embeddings_cheap(text_chunk, model):
    """
    I have chosen to keep the OpenAI API due to its inbuilt optimization
    """
    pass

def create_embeddings_batch(text_chunk):
    """Create embedding for a text chunk"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Add retry logic for API calls
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    input=text_chunk,
                    model="text-embedding-ada-002"
                )
                # Return single embedding
                return response.data[0].embedding
            except openai.APIConnectionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"OpenAI connection error, retrying in {retry_delay}s: {e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
    except Exception as e:
        logger.error(f"Embedding creation error: {e}")
        raise


def pdf_to_text(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"An error occurred: {e}")
    return text


def chunk_text(text, chunk_size=250, overlap=50):
    """
    Chunk text into parts with overlap.
    """
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        print(start, end)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        
        # Shift the start position by chunk_size - overlap for the next chunk
        start = end - overlap
        if end == len(words):
            break
    logger.info("Chunking complete")
    return chunks

def store_embeddings_in_pinecone(pdf_path):
    """
    PDF path should start with pdfs/ and not /media/ so it should use name attribute not path: 

    Read a PDF, chunk it, generate embeddings, and store them in Pinecone.
    """

    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'custom-gpt')
        
    # Create Pinecone client
    pc = pinecone.Pinecone(api_key=pinecone_api_key)
        
    # Get the index
    index = pc.Index(pinecone_index_name)

    text = pdf_to_text(settings.MEDIA_ROOT / pdf_path )
    chunks = chunk_text(text)
    
    # Prepare the Pinecone data
    ids = []  # To store ids for each chunk
    embeddings = []  # To store the embeddings for each chunk
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        embedding = create_embeddings_batch(chunk)
        ids.append(f"chunk-{i}")
        embeddings.append(embedding)
        metadatas.append({'text': chunk})
    
    # Insert the embeddings into Pinecone
    index.upsert(vectors=zip(ids, embeddings, metadatas))
    print(f"Stored {len(chunks)} chunks in Pinecone.")

    return ( embeddings, )


def get_context(query):
    try:
        openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'custom-gpt')
        
        # Create Pinecone client
        pc = pinecone.Pinecone(api_key=pinecone_api_key)
        
        # Get the index
        index = pc.Index(pinecone_index_name)

        # Convert query to embeddings
        res = openai_client.embeddings.create(
            input=[query], 
            model="text-embedding-ada-002"
        )
        embedding = res.data[0].embedding

        # Search for matching Vectors
        results = index.query(
            vector=embedding,
            top_k=1,
            include_metadata=True
        )

        # Filter out metadata from search result
        context = [match["metadata"]["text"] for match in results["matches"]][0]

        return context

    except Exception as e:
        raise ValueError("Something is wrong", e)

def upload_to_label_studio(question, answer, project_id):
    """
    Upload a question and answer pair to Label Studio for annotation.
    """

    
    data = {
            "question": question,
            "answer": answer
    }
    
    response = ls.tasks.create(project=project_id, data=data)
    if response:
        logger.info(f"Task created in Label Studio with ID: {response}")
    else:
        logger.error("Failed to create task in Label Studio")
    
    return response


def get_annotations():
    annotations = ls.annotations.list(id=1)
    print("ANnnotations : ", annotations)
    return annotations

@measure_latency_and_tokens
def get_answer(request, messages):
    """
        Send a query and return an answer based on generated context
    """
    # Set your OpenAI API key
    openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
   
    query = messages[-1]['content']
    # Define the context and query
    context = get_context(query)

    # Create a prompt using context and query
    prompt = f"Context: {context}\n\nQuery: {query}\nResponse:"
    
    # Chat history
    #
    system_prompt = [
            {"role": "developer", "content": """
                    You are a lead customer service assistant working for talents2germany. 
                    Do not mention that you are an AI model and do not mention the context in your response, speak like a human.
                    If the user asks something, do not tell anything that is not in context. Even if you fail to get context,
                    do not use training data to answer, just say you don't have the information."""},
            {"role": "user", "content": prompt}
    ] 
    try:
        messages = system_prompt + messages[-20:]
    except IndexError:
        messages = system_prompt + messages
    #print(messages)

    # Make the API call to get the response from ChatGPT
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",  # You can replace this with 'gpt-3.5-turbo' or any other model you're using
        messages = messages,
        max_completion_tokens=200,  # Adjust the length of the response
        #temperature=0.7,  # Controls randomness, higher is more random
    )

    # Output the response
    print("Chatgpt Response:", response)

    
    return response


"""
# Usage
pdf_path = 'pdfs/full_program_and_patronship_for_gpt.pdf'  # Path to the PDF file
store_embeddings_in_pinecone(pdf_path)

x= get_answer([{"role": "user", "content": "How long is the program expected to take before a candidate gets a job?"}])
print(x)

"""
