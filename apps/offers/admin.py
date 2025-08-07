from django.contrib import admin
from .models import Offer, MatchHistory

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'advertiser', 'campaign_name', 'geo', 'category', 'mmp', 'payout',
        'payable_event', 'model', 'title', 'is_active', 'created_at'
    )
    list_filter = ('advertiser', 'geo', 'category', 'is_active',)
    search_fields = ('campaign_name', 'title', 'category')

@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer', 'wishlist', 'matched_at')
    search_fields = ('offer__campaign_name', 'wishlist__desired_campaign')
    list_filter = ('matched_at',)
