from django.db import models
from apps.advertisers.models import Advertiser    
from apps.publishers.models import Wishlist       

class Offer(models.Model):
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, related_name='offers')
    campaign_name = models.CharField(max_length=255)
    geo = models.CharField(max_length=100, help_text="Comma-separated country codes like IN,US,UK")
    mmp = models.CharField(max_length=128, blank=True, null=True)
    payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payable_event = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.campaign_name or self.title

class MatchHistory(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="offer_matches")
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="wishlist_matches")
    matched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('offer', 'wishlist')

    def __str__(self):
        return f"Match: {self.offer} <-> {self.wishlist} at {self.matched_at}"
