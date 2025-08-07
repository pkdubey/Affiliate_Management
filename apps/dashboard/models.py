from django.db import models

class DashboardSnapshot(models.Model):
    date = models.DateField(unique=True)

    # Total counts
    total_advertisers = models.PositiveIntegerField(default=0)
    total_publishers = models.PositiveIntegerField(default=0)
    total_offers = models.PositiveIntegerField(default=0)
    total_invoices = models.PositiveIntegerField(default=0)

    # Revenue
    revenue_today = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue_week = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue_month = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # JSON fields to store chart data
    daily_revenue_data = models.JSONField(default=list)  # e.g. [{"date": "2025-07-14", "revenue": 1200.50}]
    daily_profit_data = models.JSONField(default=list)   # optional: if profit is calculable
    invoice_status_summary = models.JSONField(default=dict)  # e.g. {"pending": 1000.0, "paid": 2500.0}

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Dashboard Snapshot"
        verbose_name_plural = "Dashboard Snapshots"

    def __str__(self):
        return f"Snapshot on {self.date}"
