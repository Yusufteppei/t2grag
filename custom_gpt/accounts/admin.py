from django.contrib import admin
from .models import *


#admin.site.register(Usage)

@admin.register(Usage)
class UsageModelAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'completion_tokens', 'prompt_tokens', 'latency' ]
