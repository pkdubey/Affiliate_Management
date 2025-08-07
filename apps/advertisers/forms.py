from django import forms
from .models import Advertiser

class AdvertiserForm(forms.ModelForm):
    class Meta:
        model = Advertiser
        fields = ['name', 'company_name', 'contact_person', 'email', 'teams_id', 'telegram_id', 'is_active']
