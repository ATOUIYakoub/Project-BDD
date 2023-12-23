from typing import Any
from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    image_file = models.ImageField(
        upload_to='uploads/', null=True, blank=True, default='uploads/image.png')
    is_authenticated = models.BooleanField(default=False)

    def __str__(self):
        return self.username
