from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)      # New
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    teams_id = models.CharField(max_length=255, blank=True, null=True)  # New
    telegram_id = models.CharField(max_length=255, blank=True, null=True)  # New
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.company_name

    def wishlist_count(self):
        return self.wishlists.count()
    # Add more fields as needed

class Wishlist(models.Model):
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, related_name='wishlists')
    desired_campaign = models.CharField(max_length=255)
    geo = models.CharField(max_length=100)
    payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # New
    payable_event = models.CharField(max_length=255, blank=True, null=True)               # New
    model = models.CharField(max_length=255, blank=True, null=True)                      # New
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add more fields as needed
