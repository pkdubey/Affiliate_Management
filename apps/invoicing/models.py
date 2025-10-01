from django.db import models
from decimal import Decimal, ROUND_HALF_UP

class Invoice(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('INR', 'INR'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
        ('Overdue', 'Overdue'),
    ]
    PARTY_TYPE_CHOICES = [
        ('publisher', 'Publisher'),
        ('advertiser', 'Advertiser'),
    ]

    date = models.DateField(default='2025-08-27')
    invoice_number = models.CharField(max_length=100, default='INV-0001')
    due_date = models.DateField()
    party_type = models.CharField(max_length=16, choices=PARTY_TYPE_CHOICES, default='publisher')
    publisher = models.ForeignKey('publishers.Publisher', on_delete=models.CASCADE, blank=True, null=True)
    advertiser = models.ForeignKey('advertisers.Advertiser', on_delete=models.CASCADE, blank=True, null=True)
    drs = models.ForeignKey('drs.DailyRevenueSheet', on_delete=models.CASCADE)

    # Add these fields
    bill_from_details = models.TextField(blank=True, null=True)
    bill_to_details = models.TextField(blank=True, null=True)
    bank_details = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True, default="Thanks for your business.")
    signature = models.ImageField(upload_to="invoices/signatures/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pdf = models.FileField(upload_to='invoices/pdf/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_gst(self):
        if self.currency == 'INR':
            gst = self.amount * Decimal('0.18')
            return gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0')

    def save(self, *args, **kwargs):
        self.gst_amount = self.calculate_gst()
        self.total_amount = self.amount + self.gst_amount
        # Clear the opposite party to ensure only one is set
        if self.party_type == 'publisher':
            self.advertiser = None
        elif self.party_type == 'advertiser':
            self.publisher = None
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     self.gst_amount = self.calculate_gst()
    #     self.total_amount = self.amount + self.gst_amount
    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"Invoice #{self.id} - {self.publisher} ({self.currency} {self.total_amount})"

class CurrencyRate(models.Model):
    currency = models.CharField(max_length=3, unique=True)  # e.g. 'USD'
    rate_to_inr = models.DecimalField(max_digits=12, decimal_places=6)  # 1 INR = how much USD/EUR/etc
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"1 INR = {self.rate_to_inr} {self.currency} (as of {self.last_updated})"