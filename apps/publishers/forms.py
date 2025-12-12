from django import forms
from .models import Publisher

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['company_name', 'contact_person', 'email', 'teams_id', 'telegram_id', 'is_active']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'teams_id': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_id': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
