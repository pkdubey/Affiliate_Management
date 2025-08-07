from django.db import models

class DailyRevenueSheet(models.Model):
    advertiser = models.ForeignKey('advertisers.Advertiser', on_delete=models.CASCADE)
    campaign_name = models.CharField(max_length=255)
    affiliate = models.ForeignKey('publishers.Publisher', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    advertiser_conversions = models.IntegerField()
    publisher_conversions = models.IntegerField()
    campaign_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    publisher_payout = models.DecimalField(max_digits=12, decimal_places=2)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payout = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    pid = models.CharField(max_length=100)
    af_prt = models.CharField(max_length=100)
    account_manager = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)  # For timeline of updates

    def save(self, *args, **kwargs):
        # Auto-calculate fields:
        self.revenue = (self.advertiser_conversions or 0) * (self.campaign_revenue or 0)
        self.payout = (self.publisher_conversions or 0) * (self.publisher_payout or 0)
        self.profit = (self.revenue or 0) - (self.payout or 0)
        super().save(*args, **kwargs)
