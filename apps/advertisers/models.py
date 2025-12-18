# apps/advertisers/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Advertiser(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    teams_id = models.CharField(max_length=255, blank=True, null=True)    
    telegram_id = models.CharField(max_length=255, blank=True, null=True) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name

    def clean(self):
        """Validate email uniqueness across both Advertiser and Publisher"""
        super().clean()
        
        if self.email:
            email = self.email.lower().strip()
            
            # Check for duplicate email within Advertiser model
            advertisers = Advertiser.objects.filter(email__iexact=email)
            if self.pk:
                advertisers = advertisers.exclude(pk=self.pk)
            
            if advertisers.exists():
                raise ValidationError({
                    'email': _('This email is already in use by another advertiser.')
                })
            
            # Check for duplicate email in Publisher model
            from apps.publishers.models import Publisher
            
            publishers = Publisher.objects.filter(email__iexact=email)
            if publishers.exists():
                raise ValidationError({
                    'email': _('This email is already in use by a publisher.')
                })

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()  # This calls clean() and validates all fields
        super().save(*args, **kwargs)