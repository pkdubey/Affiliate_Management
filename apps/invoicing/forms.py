from .models import Invoice
from django import forms

class InvoiceForm(forms.ModelForm):
    party_type = forms.ChoiceField(
        choices=Invoice.PARTY_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Invoice Type"
    )

    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label="Date")
    invoice_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Invoice #")
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label="Due Date")

    class Meta:
        model = Invoice
        fields = ['date', 'invoice_number', 'due_date', 'party_type', 'publisher', 'advertiser', 'drs', 'currency', 'amount', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publisher'].widget.attrs['class'] = 'form-select'
        self.fields['advertiser'].widget.attrs['class'] = 'form-select'
        self.fields['drs'].widget.attrs['class'] = 'form-select'
        self.fields['currency'].widget.attrs['class'] = 'form-select'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        

