from django import forms
from .models import DailyRevenueSheet
from django.contrib.auth import get_user_model

User = get_user_model()

class DailyRevenueSheetForm(forms.ModelForm):
    class Meta:
        model = DailyRevenueSheet
        fields = [
            # Account Manager & Campaign Info
            'account_manager', 'start_date', 'campaign_name',
            # Status
            'status', 'end_date',
            # Remove 'advertiser_revenue' and 'publisher_revenue' from here
            # Advertiser Section
            'advertiser', 'geo', 'mmp', 'campaign_revenue', 'advertiser_conversions',
            # Publisher Section
            'publisher', 'pid', 'af_prt', 'payable_event_name', 'publisher_payout', 
            'publisher_conversions',
            # Remove 'conversions_postbacks' if not needed
        ]
        
        widgets = {
            # Remove widgets for the fields you removed
            'account_manager': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'campaign_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Campaign Name'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'advertiser': forms.Select(attrs={'class': 'form-select'}),
            'geo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., US, IN, UK'}),
            'mmp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Measurement Partner'}),
            'campaign_revenue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'advertiser_conversions': forms.NumberInput(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
            'pid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Publisher ID'}),
            'af_prt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AF/PRT'}),
            'payable_event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Name for Payout'}),
            'publisher_payout': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'publisher_conversions': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'campaign_revenue': 'Campaign Revenue ($)',
            'publisher_payout': 'Campaign Payout ($)',
        }