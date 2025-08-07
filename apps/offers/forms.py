from django import forms
from .models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = [
            'advertiser', 'campaign_name', 'geo', 'category',
            'mmp', 'payout', 'payable_event', 'model',
            'title', 'description', 'is_active'
        ]
