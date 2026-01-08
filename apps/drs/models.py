from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DailyRevenueSheet(models.Model):
    # Update STATUS_CHOICES to include the full flow
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
    ]
    
    account_manager = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    campaign_name = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    end_date = models.DateField(null=True, blank=True)
    
    # Revenue fields
    advertiser_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    publisher_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Advertiser section
    advertiser = models.ForeignKey('advertisers.Advertiser', on_delete=models.CASCADE)
    geo = models.CharField(max_length=100)
    mmp = models.CharField(max_length=100, blank=True, null=True)
    campaign_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advertiser_conversions = models.IntegerField(default=0)
    
    # Publisher section
    publisher = models.ForeignKey('publishers.Publisher', on_delete=models.CASCADE)
    pid = models.CharField(max_length=100, blank=True, null=True)
    af_prt = models.CharField(max_length=100, blank=True, null=True, verbose_name="AF/PRT")
    payable_event_name = models.CharField(max_length=255, blank=True, null=True)
    publisher_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    publisher_conversions = models.IntegerField(default=0)
    conversions_postbacks = models.IntegerField(default=0)
    
    # Auto-calculated fields
    revenue = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payout = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Validation tracking fields
    validation_required = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='validated_drs')
    
    # Invoice tracking fields
    invoice = models.ForeignKey('invoicing.Invoice', null=True, blank=True, on_delete=models.SET_NULL, related_name='drs_invoices')
    invoiced_at = models.DateTimeField(null=True, blank=True)
    
    # Payment tracking fields
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='paid_drs')
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate revenue
        if self.advertiser_revenue > 0:
            self.revenue = self.advertiser_revenue
        else:
            self.revenue = (self.advertiser_conversions or 0) * (self.campaign_revenue or 0)
        
        # Calculate payout
        if self.publisher_revenue > 0:
            self.payout = self.publisher_revenue
        else:
            self.payout = (self.publisher_conversions or 0) * (self.publisher_payout or 0)
        
        # Calculate profit
        self.profit = (self.revenue or 0) - (self.payout or 0)
        
        # Auto-set validation_required when status is paused or completed
        if self.status in ['paused', 'completed']:
            self.validation_required = True
        else:
            self.validation_required = False
        
        # Auto-set validated_at when status changes to validated
        if self.status == 'validated' and not self.validated_at:
            self.validated_at = models.DateTimeField(auto_now=True)
        
        # Auto-set invoiced_at when status changes to invoiced
        if self.status == 'invoiced' and not self.invoiced_at:
            self.invoiced_at = models.DateTimeField(auto_now=True)
        
        # Auto-set paid_at when status changes to paid
        if self.status == 'paid' and not self.paid_at:
            self.paid_at = models.DateTimeField(auto_now=True)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campaign_name} - {self.advertiser}"

    class Meta:
        verbose_name = "Daily Revenue Sheet"
        verbose_name_plural = "Daily Revenue Sheets"
        ordering = ['-created_at']
        permissions = [
            ("can_validate_drs", "Can validate DRS"),
            ("can_create_invoice", "Can create invoice from DRS"),
            ("can_approve_invoice", "Can approve invoice"),
            ("can_mark_paid", "Can mark invoice as paid"),
        ]
    
    # Helper methods for status flow
    def can_be_validated(self):
        """Check if DRS can be validated"""
        return self.status in ['paused', 'completed']
    
    def can_be_invoiced(self):
        """Check if DRS can be invoiced"""
        return self.status == 'validated'
    
    def can_be_approved(self):
        """Check if DRS can be approved"""
        return self.status == 'invoiced'
    
    def can_be_paid(self):
        """Check if DRS can be marked as paid"""
        return self.status == 'approved'
    
    def get_status_display_class(self):
        """Get Bootstrap class for status badge"""
        status_classes = {
            'active': 'success',
            'paused': 'warning',
            'completed': 'info',
            'paid': 'success',
        }
        return status_classes.get(self.status, 'secondary')
    
    def get_validation_status(self):
        """Get validation status for this DRS"""
        try:
            from apps.validation.models import Validation
            validation = Validation.objects.filter(drs=self).first()
            if validation:
                return {
                    'exists': True,
                    'status': validation.status,
                    'approve_payout': validation.approve_payout,
                    'created_at': validation.created_at,
                }
        except:
            pass
        return {'exists': False}
    
    def get_invoice_status(self):
        """Get invoice status for this DRS"""
        if self.invoice:
            return {
                'exists': True,
                'invoice_number': self.invoice.invoice_number,
                'status': self.invoice.status,
                'amount': self.invoice.amount,
                'total_amount': self.invoice.total_amount,
            }
        return {'exists': False}

    @property
    def is_validated(self):
        """Check if DRS has been validated"""
        return self.status == 'validated'