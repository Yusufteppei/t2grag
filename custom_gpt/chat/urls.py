from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index),
    path('upload', views.upload_pdf, name='upload_pdf'),
    path('upload_api', views.upload_pdf_api, name='upload_pdf_api'),
    path('answer', views.answer_query, name='answer_query'),
    path('get_chat', views.get_chat, name='get_chat'),
    path('create_chat', views.create_chat, name='create_chat'),
    path('annotations', views.annotations, name='get_annotations')
]



# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
