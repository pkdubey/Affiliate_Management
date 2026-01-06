from django import forms
from .models import Validation

class ValidationForm(forms.ModelForm):
    class Meta:
        model = Validation
        fields = [
            'drs', 'publisher', 'month', 'conversions', 'payout', 'approve_payout', 'status'
        ]
        widgets = {
            'month': forms.DateInput(attrs={'type': 'month'}),
            'conversions': forms.NumberInput(attrs={'class': 'form-control'}),
            'payout': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approve_payout': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }