from django.db import models
from .methods import store_embeddings_in_pinecone
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class PDFUpload(models.Model):
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='pdfs')  # Save the PDF in the 'pdfs/' folder

    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        super(PDFUpload, self).save(*args, **kwargs)
        print("\n\n\nSaved File\n\n\n", self.pdf_file.url)
        store_embeddings_in_pinecone(self.pdf_file.name)


class Chat(models.Model):
    """
        Model to store chat sessions and their messages.
    """
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats') # CHANGE TO USER FOREIGNKEY
    context = models.TextField(max_length=8192)
    content = models.TextField(max_length=20480)    # {user}===={assistant}++++{user}===={assistant}++++

    def decode(self):
        if self.content == '':
            return []

        chat_pairs = self.content.split("++++")
        
        full_decode = []

        for i in chat_pairs:

            chat_pair = i.split("====")
            if len(chat_pair) >= 2:
                full_decode += [
                    { 'role': 'user', 'content': chat_pair[0]}, 
                    {'role': 'assistant', 'content': chat_pair[1]}
                ]

        return full_decode

    def encode(self, texts: list):
        # Should always start with the user

        val = ""
        print("TEXTS",  texts)
        for i in texts:
            if i.role == "user":
                val+= i.content + "===="
            elif i.role == "assistant":
                val += i.content + "++++"

        return val

    def add_chat_pair(self, chat_pair: list): # Text must must contain both the user entry and assistant response
        self.content += self.encode(chat_pair)
        self.save()

    def add_user_query(self, query: str):
        self.content += query + "===="
        self.save()

    def add_assistant_response(self, answer: str):
        self.content += answer + "++++"
        self.save()

    def get_decoded_messages(self):
        return self.decode()

    def save(self, *args, **kwargs) -> None:
        return super().save(*args, **kwargs)



class Annotation(models.Model):
    created_at = models.DateTimeField()
    import_id = models.BigIntegerField()
    project = models.IntegerField()
    comprehensiveness = models.IntegerField()
    completeness = models.IntegerField()
    task = models.IntegerField()
    was_cancelled = models.BooleanField()

