from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('subadmin', 'Sub-admin'),
        ('publisher', 'Publisher'),
        ('dashboard', 'Dashboard Team Member'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='publisher')
    
    # Add relationship to Publisher model
    publisher = models.OneToOneField(
        'publishers.Publisher',  # Make sure this matches your Publisher model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_account'
    )