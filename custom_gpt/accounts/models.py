from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

User = get_user_model()


class Usage(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    latency = models.DecimalField(decimal_places=2, max_digits=6)
    prompt_tokens = models.IntegerField()
    completion_tokens = models.IntegerField()
