from django.contrib import admin

# Register your models here.
from .models import Chat, PDFUpload

admin.site.register([Chat, PDFUpload])
admin.site.site_header="T2GERM RAG"
