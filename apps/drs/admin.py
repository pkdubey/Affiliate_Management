from django.contrib import admin
from .models import DailyRevenueSheet

@admin.register(DailyRevenueSheet)
class DailyRevenueSheetAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'advertiser', 'campaign_name', 'publisher', 'start_date', 'end_date',
        'advertiser_conversions', 'publisher_conversions', 'campaign_revenue', 'publisher_payout',
        'revenue', 'payout', 'profit', 'account_manager', 'pid', 'updated_at', 'status'
    )
    list_filter = ('advertiser', 'publisher', 'account_manager', 'status', 'start_date', 'end_date')
    search_fields = ('campaign_name', 'pid', 'payable_event_name', 'account_manager', 'geo')
    list_editable = ('status',)
    
    # REMOVE or fix this method - account_manager is a CharField, not ForeignKey
    def get_queryset(self, request):
        # Only select related on actual ForeignKey fields
        return super().get_queryset(request).select_related('advertiser', 'publisher')
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('account_manager', 'start_date', 'end_date', 'campaign_name', 'status')
        }),
        ('Revels', {
            'fields': ('advertiser_revenue', 'publisher_revenue')
        }),
        ('Advertiser Details', {
            'fields': ('advertiser', 'geo', 'mmp', 'campaign_revenue', 'advertiser_conversions')
        }),
        ('Publisher Details', {
            'fields': ('publisher', 'pid', 'payable_event_name', 'publisher_payout', 
                      'publisher_conversions', 'conversions_postbacks')
        }),
        ('Calculated Fields', {
            'fields': ('revenue', 'payout', 'profit'),
            'classes': ('collapse',)
        }),
    )