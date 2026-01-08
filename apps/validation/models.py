from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Validation(models.Model):
    # Update status choices to match the flow
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Invoiced', 'Invoiced'),
        ('Paid', 'Paid'),
    ]
    
    drs = models.ForeignKey('drs.DailyRevenueSheet', on_delete=models.CASCADE, related_name='validations')
    publisher = models.ForeignKey('publishers.Publisher', on_delete=models.CASCADE, related_name='validations')
    
    month = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    
    conversions = models.IntegerField(default=0)
    payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approve_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Invoice link
    invoice = models.ForeignKey('invoicing.Invoice', null=True, blank=True, on_delete=models.SET_NULL, related_name='validation_invoices')
    
    # Tracking fields
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='submitted_validations')
    
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_validations')
    
    invoiced_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Validation: {self.drs.campaign_name} ({self.publisher}) [{self.month}]"
    
    def save(self, *args, **kwargs):
        # Auto-set timestamps based on status changes
        is_new = self.pk is None
        
        if not is_new:
            try:
                old_instance = Validation.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Validation.DoesNotExist:
                old_status = None
        else:
            old_status = None
        
        # Import timezone here to avoid circular imports
        from django.utils import timezone
        
        # Update timestamps based on status
        if self.status == 'Pending' and not self.submitted_at:
            self.submitted_at = timezone.now()
            if not self.submitted_by and hasattr(self, '_request_user'):
                self.submitted_by = self._request_user
        
        if self.status == 'Approved' and old_status != 'Approved':
            self.approved_at = timezone.now()
            if not self.approved_by and hasattr(self, '_request_user'):
                self.approved_by = self._request_user
        
        if self.status == 'Invoiced' and old_status != 'Invoiced':
            self.invoiced_at = timezone.now()
        
        if self.status == 'Paid' and old_status != 'Paid':
            self.paid_at = timezone.now()
        
        # Don't update DRS status here - let the view handle it
        # This avoids circular save issues
        
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Validation"
        verbose_name_plural = "Validations"
    
    def can_be_approved(self):
        """Check if validation can be approved"""
        return self.status == 'Pending'
    
    def can_be_invoiced(self):
        """Check if validation can be invoiced"""
        return self.status == 'Approved' and not self.invoice
    
    def can_be_paid(self):
        """Check if validation can be marked as paid"""
        return self.status == 'Invoiced' and self.invoice
    
    def get_status_display_class(self):
        """Get Bootstrap class for status badge"""
        status_classes = {
            'Pending': 'warning',
            'Approved': 'success',
            'Rejected': 'danger',
            'Invoiced': 'info',
            'Paid': 'success',
        }
        return status_classes.get(self.status, 'secondary')
    
    def calculate_totals(self):
        """Calculate and update totals from DRS"""
        if self.drs:
            self.conversions = self.drs.publisher_conversions or 0
            self.payout = self.drs.payout or 0
            if not self.approve_payout:
                self.approve_payout = self.drs.payout or 0
            self.save()

    @property
    def has_invoice(self):
        """Check if validation has an invoice"""
        return self.invoice is not None