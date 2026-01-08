# apps/publishers/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Publisher(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    teams_id = models.CharField(max_length=255, blank=True, null=True)
    telegram_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name
    
    @property
    def name(self):
        """Alias for contact_person for compatibility with templates"""
        return self.contact_person or self.company_name

    def clean(self):
        """Validate email uniqueness across both Publisher and Advertiser"""
        super().clean()
        
        if self.email:
            email = self.email.lower().strip()
            
            # Check for duplicate email within Publisher model
            publishers = Publisher.objects.filter(email__iexact=email)
            if self.pk:
                publishers = publishers.exclude(pk=self.pk)
            
            if publishers.exists():
                raise ValidationError({
                    'email': _('This email is already in use by another publisher.')
                })
            
            # Check for duplicate email in Advertiser model
            from apps.advertisers.models import Advertiser
            
            advertisers = Advertiser.objects.filter(email__iexact=email)
            if advertisers.exists():
                raise ValidationError({
                    'email': _('This email is already in use by an advertiser.')
                })

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()  # This calls clean() and validates all fields
        super().save(*args, **kwargs)

    def wishlist_count(self):
        return self.wishlists.count()


class Wishlist(models.Model):
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, related_name='wishlists')
    desired_campaign = models.CharField(max_length=255)
    geo = models.CharField(max_length=100)
    payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)