from django.db import models

class Advertiser(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    teams_id = models.CharField(max_length=255, blank=True, null=True)    
    telegram_id = models.CharField(max_length=255, blank=True, null=True) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name
