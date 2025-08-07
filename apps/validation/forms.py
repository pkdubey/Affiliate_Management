from django import forms
from .models import Validation

class ValidationForm(forms.ModelForm):
    class Meta:
        model = Validation
        fields = [
            'drs', 'publisher', 'month', 'conversions', 'payout', 'approve_payout', 'status'
        ]

