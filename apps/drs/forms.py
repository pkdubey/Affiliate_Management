from django import forms
from .models import DailyRevenueSheet

class DailyRevenueSheetForm(forms.ModelForm):
    class Meta:
        model = DailyRevenueSheet
        fields = [
            'advertiser', 'campaign_name', 'affiliate', 'start_date', 'end_date',
            'advertiser_conversions', 'publisher_conversions', 'campaign_revenue', 'publisher_payout',
            'pid', 'af_prt', 'account_manager'
        ]  # REMOVE revenue, payout, profit from manual input
