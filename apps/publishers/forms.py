from django import forms
from .models import Publisher

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'company_name', 'contact_person', 'email', 'teams_id', 'telegram_id', 'is_active']
