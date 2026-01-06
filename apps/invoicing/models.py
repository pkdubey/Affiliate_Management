from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta, timezone

def default_due_date():
    return date.today() + timedelta(days=30)

class Invoice(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD'), ('EUR', 'EUR'), ('INR', 'INR'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'), ('Paid', 'Paid'), ('Cancelled', 'Cancelled'), ('Overdue', 'Overdue'),
    ]
    PARTY_TYPE_CHOICES = [
        ('publisher', 'Publisher'), ('advertiser', 'Advertiser'),
    ]

    date = models.DateField(auto_now_add=True)
    invoice_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    due_date = models.DateField(default=default_due_date, blank=True, null=True)
    party_type = models.CharField(max_length=16, choices=PARTY_TYPE_CHOICES, default='publisher')

    publisher = models.ForeignKey('publishers.Publisher', on_delete=models.CASCADE, blank=True, null=True)
    advertiser = models.ForeignKey('advertisers.Advertiser', on_delete=models.CASCADE, blank=True, null=True)
    drs = models.ForeignKey(
        'drs.DailyRevenueSheet', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='invoice_drs'  # Add this line
    )

    bill_from_details = models.TextField(blank=True, null=True)
    bill_to_details = models.TextField(blank=True, null=True)
    bank_details = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True, default="Thanks for your business.")
    signature = models.ImageField(upload_to="invoices/signatures/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    pdf = models.FileField(upload_to='invoices/pdf/', blank=True, null=True)
    validation = models.ForeignKey('validation.Validation', null=True, blank=True, on_delete=models.SET_NULL, related_name='validation_invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    bill_from_company = models.CharField(max_length=200, default="Traccify", blank=True)
    bill_from_address_line1 = models.TextField(default="Trademark Sechura Thakurdwara Road, Bazar", blank=True)
    bill_from_address_line2 = models.TextField(default="Krishn, Bijnor, Uttar Pradesh, India, 246746", blank=True)
    bill_from_registration_new = models.CharField(max_length=100, default="Company Registration No: 09AMFPV3992D1ZL", blank=True)
    bill_from_msme_new = models.CharField(max_length=100, default="MSME: UP/YAM-UP-17-0028662", blank=True)
    bill_from_email = models.EmailField(default="finance@traccify.ai", blank=True)
    bill_from_gstin = models.CharField(max_length=50, default="09AMFPV3992D1ZL", blank=True)
    
    bill_to_company_new = models.CharField(max_length=200, default="Rohan Technology", blank=True)
    bill_to_email_new = models.EmailField(default="rohan@gmail.com", blank=True)
    bill_to_address_new = models.TextField(blank=True, null=True)
    bill_to_gstin = models.CharField(max_length=50, blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True, null=True)

    terms_days = models.CharField(max_length=10, default="30", blank=True)
    net_terms = models.CharField(max_length=50, default="Net 30", blank=True)

    bank_name = models.CharField(max_length=100, default="HDFC Bank", blank=True)
    bank_account_name = models.CharField(max_length=100, default="traccify.ai", blank=True)
    bank_account_number = models.CharField(max_length=50, default="50200094727751", blank=True)
    bank_ifsc_code = models.CharField(max_length=20, default="HDFC0007070", blank=True)
    bank_swift_code = models.CharField(max_length=20, default="HDFCINBB", blank=True)
    bank_branch_address = models.TextField(default="Ward No 12, Gr Flr, Muslim Chowdhirian, Dhampur, Hayatnagar Seohara Bijnor - 246746", blank=True)

    def calculate_gst(self):
        if self.currency == 'INR':
            base = self.subtotal or self.amount or Decimal('0')
            gst = base * Decimal('0.18')
            cgst = base * Decimal('0.09')
            sgst = base * Decimal('0.09')
            return {
                'total_gst': gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'cgst': cgst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'sgst': sgst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            }
        return {'total_gst': Decimal('0'), 'cgst': Decimal('0'), 'sgst': Decimal('0')}

    def calculate_totals(self):
        if hasattr(self, 'lines') and hasattr(self.lines, 'exists') and self.lines.exists():
            self.subtotal = sum(line.amount for line in self.lines.all())
        else:
            self.subtotal = self.subtotal or self.amount or Decimal('0')
        gst_data = self.calculate_gst()
        self.gst_amount = gst_data['total_gst']
        self.cgst_amount = gst_data['cgst']
        self.sgst_amount = gst_data['sgst']
        self.total_amount = self.subtotal + self.gst_amount

    def save(self, *args, **kwargs):
        # Auto-generate invoice_number if blank
        if not self.invoice_number:
            count = Invoice.objects.filter(party_type=self.party_type).count() + 1
            prefix = 'PUB' if self.party_type == 'publisher' else 'INV'
            self.invoice_number = f'{prefix}-{count:06d}'

        # Calculate totals BEFORE first save (works without pk now)
        if hasattr(self, 'lines') and hasattr(self.lines, 'exists'):
            try:
                if self.lines.exists():
                    self.subtotal = sum(line.amount for line in self.lines.all())
            except:
                pass  # lines might not exist yet
        
        if not self.subtotal:
            self.subtotal = self.amount or Decimal('0')
        
        gst_data = self.calculate_gst()
        self.gst_amount = gst_data['total_gst']
        self.cgst_amount = gst_data['cgst']
        self.sgst_amount = gst_data['sgst']
        self.total_amount = self.subtotal + self.gst_amount

        # For publisher + non-INR, override GST
        if self.party_type == 'publisher' and self.currency != 'INR':
            self.gst_amount = 0
            self.cgst_amount = 0
            self.sgst_amount = 0
            self.total_amount = self.subtotal or self.amount or Decimal('0')

        # Fill default text fields if empty
        if not self.bill_from_details:
            self.bill_from_details = (
                f"{self.bill_from_company}\n"
                f"{self.bill_from_address_line1}\n"
                f"{self.bill_from_address_line2}\n"
                f"{self.bill_from_registration_new}"
            )
        if not self.bill_to_details:
            self.bill_to_details = f"{self.bill_to_company_new}\n{self.bill_to_email_new}"
        if not self.bank_details:
            self.bank_details = (
                f"Bank: {self.bank_name}\n"
                f"Name: {self.bank_account_name}\n"
                f"A/C No: {self.bank_account_number}\n"
                f"IFSC: {self.bank_ifsc_code}\n"
                f"SWIFT: {self.bank_swift_code}"
            )
        if not self.terms:
            self.terms = "Thanks for your business."

        # Clear the opposite party
        if self.party_type == 'publisher':
            self.advertiser = None
        else:
            self.publisher = None

        # Single save - all calculations done before this
        super().save(*args, **kwargs)

    def get_display_company_name(self):
        if self.party_type == 'publisher' and self.publisher:
            return str(self.publisher)
        elif self.party_type == 'advertiser' and self.advertiser:
            return str(self.advertiser)
        return self.bill_to_company_new or "Client"
    
    def link_validation(self, validation):
        """Link this invoice to a validation"""
        self.validation = validation
        self.save()
        # Update validation status
        if validation:
            validation.status = 'Invoiced'
            validation.invoice = self
            validation.invoiced_at = timezone.now()
            validation.save()

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.get_party_type_display()}"


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    item_description = models.CharField(max_length=200, default="Service")
    hsn_sac = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=9.00)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=9.00)
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    sort_order = models.IntegerField(default=1)
    
    def calculate_amounts(self):
        self.amount = self.quantity * self.rate
        
        if self.invoice and self.invoice.currency == 'INR':
            self.cgst_amount = (self.amount * self.cgst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.sgst_amount = (self.amount * self.sgst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.cgst_amount = Decimal('0')
            self.sgst_amount = Decimal('0')
    
    def save(self, *args, **kwargs):
        self.calculate_amounts()
        super().save(*args, **kwargs)
        
        if self.invoice:
            self.invoice.calculate_totals()
            self.invoice.save()
    
    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        if invoice:
            invoice.calculate_totals()
            invoice.save()
    
    class Meta:
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        return f"{self.item_description} - {self.amount}"


class CurrencyRate(models.Model):
    currency = models.CharField(max_length=3, unique=True)
    rate_to_inr = models.DecimalField(max_digits=12, decimal_places=6)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"1 INR = {self.rate_to_inr} {self.currency} (as of {self.last_updated})"
