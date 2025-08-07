from django.db import models

class Validation(models.Model):
    drs = models.ForeignKey('drs.DailyRevenueSheet', on_delete=models.CASCADE)
    publisher = models.ForeignKey('publishers.Publisher', on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    conversions = models.IntegerField(default=0)
    payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approve_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Validation: {self.drs.campaign_name} ({self.publisher}) [{self.month}]"
