from django import forms
from decimal import Decimal, ROUND_HALF_UP
from .models import Invoice
from apps.drs.models import DailyRevenueSheet

class InvoiceForm(forms.ModelForm):
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Invoice
        exclude = ['created_at', 'updated_at']
        widgets = {
            'gst_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Always optional
        optional = [
            'drs', 'gst_amount', 'total_amount',
            'bill_from_details', 'bill_to_details',
            'bank_details', 'terms', 'signature',
        ]
        for f in optional:
            if f in self.fields:
                self.fields[f].required = False

        party = self.data.get('party_type') or self.instance.party_type or 'advertiser'
        # Publisher requires publisher FK but file optional
        if party == 'publisher':
            self.fields['publisher'].required = True
            self.fields['advertiser'].required = False
            self.fields['pdf'].required = False    # optional upload
        # Advertiser requires advertiser FK, no PDF
        else:
            self.fields['advertiser'].required = True
            self.fields['publisher'].required = False
            self.fields['pdf'].required = False

    def clean(self):
        cleaned = super().clean()
        party = cleaned.get('party_type')

        if party == 'publisher':
            if not cleaned.get('publisher'):
                raise forms.ValidationError('Publisher must be selected.')
            # pdf truly optional: no validation here
        else:
            if not cleaned.get('advertiser'):
                raise forms.ValidationError('Advertiser must be selected.')

            # compute gst_amount and total_amount here if left blank
            amt = cleaned.get('amount') or Decimal('0')
            currency = cleaned.get('currency')
            if currency == 'INR':
                gst = (amt * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                gst = Decimal('0.00')
            cleaned['gst_amount'] = gst
            cleaned['total_amount'] = (amt + gst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return cleaned
