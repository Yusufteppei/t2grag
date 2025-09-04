from django.shortcuts import render
from .forms import PDFUploadForm
from .models import PDFUpload, Chat, Annotation
from .methods import get_answer, store_embeddings_in_pinecone, upload_to_label_studio, get_annotations
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .checks import check_messages
from rest_framework import status
from rest_framework.response import Response
from .serializers import PDFUploadSerializer
import logging
from datetime import datetime
logging.basicConfig(filename="chat.log")

@api_view(['POST'])
def upload_pdf_api(request):
    if request.method == 'POST':
        if 'pdf' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['pdf']
        
        # Create the PDFUpload object and save it to the database
        pdf_upload = PDFUpload(pdf_file=file)
        pdf_upload.save()

        # Serialize the PDFUpload instance
        serializer = PDFUploadSerializer(pdf_upload)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#   INSECURE TO EXPOSE
def store_embeddings_in_pinecone(request):
    id = request.POST['id']
    pdf_path = PDFUpload.objects.get(id=id).pdf_file.name
    store_embeddings_in_pinecone(pdf_path)
    

def index(request):

    context = {

    }

    return render(request, template_name='chat/index.html', context=context)


def upload_pdf(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the uploaded PDF to the database
            return render(request, 'chat/upload_success.html', {'form': form})
    else:
        form = PDFUploadForm()
    
    return render(request, 'chat/upload_pdf.html', {'form': form})


##################################,##
@api_view(['GET'])
def create_chat(request):
    
    c = Chat.objects.create(user=request.user)
    chat_id = c.id

    return JsonResponse({
        'status': 200,
        'chat_id': chat_id
    })

@api_view(['GET'])
def get_chat(request):
    """
        Get most recent chat for the user (for simplicity in the frontend)

        To be changed later to get specific chat by ID
    """
     
    # Get user's last chat for simplicity

    if Chat.objects.filter(user=request.user).count() > 0:
        chat = Chat.objects.filter(user=request.user).last()
        print("found", chat)
    else:
        chat = Chat.objects.create(user=request.user)
    
    #chat_id = request.GET['chat_id']
    #chat = Chat.objects.get(id=chat_id)

    return JsonResponse({
        'status': 200,
        'created_on': f'{chat.created_on.year}/{chat.created_on.month}/{chat.created_on.day}-{chat.created_on.hour}/{chat.created_on.minute}',
        'chat_id': chat.id,
        'messages': chat.get_decoded_messages()
    })



@api_view(['POST'])
def answer_query(request):
    query = request.data['query']
    chat_id = request.data['chat_id']
    chat = Chat.objects.get(id=chat_id)

    #   ADD USER QUERY TO THE CHAT IN DB
    chat.add_user_query(query)

    #print(request.data)

    messages = request.data['messages']
    
    messages.append( { 'role': 'user', 'content': query } )

    #   CHECK THAT DB MESSAGES MATCHES FRONTEND MESSAGES
#    if not check_messages(chat, messages):
#        logging.warning("Message Synchronization error")

    #   GET ANSWER FROM AI MODEL
    
    answer = get_answer(request, messages).choices[0].message.content

    upload_to_label_studio(query, answer, 1)
    # INCLUDE ANSWER TO THE CHAT IN DB
    chat.add_assistant_response(answer)

    return JsonResponse(
        {
            'status': 200,
            'answer': answer
        }
    )


###         ANALYTICS ENDPOINTS         ###

@api_view(['GET', 'POST'])
def annotations(request):
   if request.method == 'GET':
        annotations = get_annotations()
        return JsonResponse(
           { 
               "id": 1,
               "annotations": [ annotation.result for annotation in annotations ] 
           }
        )
   #elif request.method == 'POST':
   #    completeness = request.data['result']['completeness']
   #    comprehensiveness = request.data['result']['comprehensiveness']
   #    
   #    Annotation.objects.create(
   #     completeness=        
   #            )
   

@api_view(['GET'])
def latency(request):
    pass
