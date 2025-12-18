# apps/advertisers/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Advertiser

class AdvertiserForm(forms.ModelForm):
    class Meta:
        model = Advertiser
        fields = ['company_name', 'contact_person', 'email', 'teams_id', 'telegram_id', 'is_active']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'teams_id': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_id': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            return email  # Allow empty email
        
        email = email.lower().strip()  # Normalize email
        
        # Check if email exists in Publisher model
        from apps.publishers.models import Publisher
        
        # Query for publishers with this email
        publishers = Publisher.objects.filter(email__iexact=email)
        
        # If updating an existing advertiser, exclude current instance
        if self.instance and self.instance.pk:
            # Check if the email is being changed
            if self.instance.email and self.instance.email.lower() == email:
                # Email hasn't changed, no need to check publishers
                return email
            else:
                # Email is being changed, check publishers
                if publishers.exists():
                    raise ValidationError('This email is already in use by a publisher.')
        else:
            # Creating new advertiser, check publishers
            if publishers.exists():
                raise ValidationError('This email is already in use by a publisher.')
        
        return email