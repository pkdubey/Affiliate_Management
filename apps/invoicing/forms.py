from .models import Invoice
from django import forms

class InvoiceForm(forms.ModelForm):
    party_type = forms.ChoiceField(
        choices=Invoice.PARTY_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Invoice Type"
    )

    class Meta:
        model = Invoice
        fields = ['party_type', 'publisher', 'advertiser', 'drs', 'currency', 'amount', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].widget.attrs['class'] = 'form-select'
        self.fields['advertiser'].widget.attrs['class'] = 'form-select'
        self.fields['drs'].widget.attrs['class'] = 'form-select'
        self.fields['currency'].widget.attrs['class'] = 'form-select'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        

