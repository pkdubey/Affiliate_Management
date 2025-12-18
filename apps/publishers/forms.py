# apps/publishers/forms.py
from django import forms
from django.core.exceptions import ValidationError
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add error classes to fields that have errors
        for field_name, field in self.fields.items():
            if field_name in self.errors:
                # Add Bootstrap error class
                attrs = field.widget.attrs
                if 'class' in attrs:
                    attrs['class'] += ' is-invalid'
                else:
                    attrs['class'] = 'form-control is-invalid'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            return email  # Allow empty email
        
        email = email.lower().strip()  # Normalize email
        
        # 1. Check within Publisher model
        publishers = Publisher.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            publishers = publishers.exclude(pk=self.instance.pk)
        
        if publishers.exists():
            raise ValidationError('This email is already in use by another publisher.')
        
        # 2. Check in Advertiser model
        from apps.advertisers.models import Advertiser
        
        advertisers = Advertiser.objects.filter(email__iexact=email)
        if advertisers.exists():
            raise ValidationError('This email is already in use by an advertiser.')
        
        return email