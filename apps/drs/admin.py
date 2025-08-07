from django.contrib import admin

# Register your models here.
from .models import DailyRevenueSheet

@admin.register(DailyRevenueSheet)
class DailyRevenueSheetAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'advertiser', 'campaign_name', 'affiliate', 'start_date', 'end_date',
        'advertiser_conversions', 'publisher_conversions', 'campaign_revenue', 'publisher_payout',
        'revenue', 'payout', 'profit', 'account_manager', 'pid', 'af_prt', 'updated_at'
    )
    list_filter = ('advertiser', 'affiliate', 'account_manager', 'start_date', 'end_date')
    search_fields = ('campaign_name', 'pid', 'af_prt', 'account_manager')