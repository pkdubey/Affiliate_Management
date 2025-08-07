
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('subadmin', 'Sub-admin'),
        ('publisher', 'Publisher'),
        ('dashboard', 'Dashboard Team Member'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Add more fields as needed
