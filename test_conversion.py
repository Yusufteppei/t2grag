import json
import os
import logging
import io
import openai
import pinecone
from PyPDF2 import PdfReader
import docx
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_file(file_content, mime_type):
    """Extract text from different file types with improved text extraction"""
    try:
        if mime_type == 'application/pdf':
            pdf_reader = PdfReader(io.BytesIO(file_content))
            text_chunks = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                # Clean the text while preserving paragraph breaks
                cleaned_text = '\n'.join(
                    line.strip() 
                    for line in text.split('\n') 
                    if line.strip()
                )
                if cleaned_text:
                    text_chunks.append(cleaned_text)
            
            return '\n\n'.join(text_chunks)
            
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = docx.Document(io.BytesIO(file_content))
            text_chunks = []
            for paragraph in doc.paragraphs:
                para_text = paragraph.text.strip()
                if para_text and len(para_text.split()) >= 10:
                    text_chunks.append(para_text)
            return '\n\n'.join(text_chunks)
        
        else:
            return file_content.decode('utf-8')
            
    except Exception as e:
        logger.error(f"Text extraction error for {mime_type}: {e}")
        return ""
    
def chunk_text(text, chunk_size=8000, overlap=100):
    """
    Split text into overlapping chunks with better semantic preservation
    """
    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        paragraph_size = len(paragraph.split())
        
        if current_size + paragraph_size <= chunk_size:
            current_chunk.append(paragraph)
            current_size += paragraph_size
        else:
            # Save current chunk if it's not empty
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            
            # Start new chunk with overlap
            if chunks and overlap > 0:
                # Take last few paragraphs from previous chunk for overlap
                overlap_text = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk[-1:]
                current_chunk = overlap_text + [paragraph]
                current_size = sum(len(p.split()) for p in current_chunk)
            else:
                current_chunk = [paragraph]
                current_size = paragraph_size
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def create_embeddings_batch(text_chunk):
    """Create embedding for a text chunk"""
    try:
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
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

def store_in_pinecone(file_id, embedding, text_content, file_info):
    """Store embedding in Pinecone with metadata"""
    try:
        pinecone_api_key = os.environ.get('PINECONE_API_KEY')
        pinecone_index_name = os.environ.get('PINECONE_INDEX_NAME')
        
        # Create Pinecone client
        pc = pinecone.Pinecone(api_key=pinecone_api_key)
        
        # Get the index
        index = pc.Index(pinecone_index_name)
        
        # Prepare metadata
        metadata = {
            # 'file_id': file_id,
            # 'mime_type': file_info.get('mimeType', ''),
            # 'file_name': file_info.get('name', ''),
            # 'text_length': len(text_content),
            'text': text_content[:500]  # First 500 characters as preview
        }
        
        # Upsert the vector with metadata
        index.upsert(
            vectors=[(
                file_id,  # Vector ID
                embedding,  # Embedding vector
                metadata  # Metadata dictionary
            )]
        )
        
        return True
    except Exception as e:
        logger.error(f"Pinecone storage error: {e}")
        raise

