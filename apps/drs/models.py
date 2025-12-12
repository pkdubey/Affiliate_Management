from django.db import models

class DailyRevenueSheet(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    account_manager = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    campaign_name = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    end_date = models.DateField(null=True, blank=True)
    
    # Revels (Revenue fields)
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
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate revenue: advertiser_revenue is total, or use advertiser_conversions * campaign_revenue
        if self.advertiser_revenue > 0:
            self.revenue = self.advertiser_revenue
        else:
            self.revenue = (self.advertiser_conversions or 0) * (self.campaign_revenue or 0)
        
        # Calculate payout: publisher_revenue is total, or use publisher_conversions * publisher_payout
        if self.publisher_revenue > 0:
            self.payout = self.publisher_revenue
        else:
            self.payout = (self.publisher_conversions or 0) * (self.publisher_payout or 0)
        
        self.profit = (self.revenue or 0) - (self.payout or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campaign_name} - {self.advertiser}"

    class Meta:
        verbose_name = "Daily Revenue Sheet"
        verbose_name_plural = "Daily Revenue Sheets"