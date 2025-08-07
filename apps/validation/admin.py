from django.contrib import admin

from django.contrib import admin
from .models import Validation

@admin.register(Validation)
class ValidationAdmin(admin.ModelAdmin):
    list_display = ('id', 'drs', 'publisher', 'month', 'conversions', 'payout', 'approve_payout', 'status')
    list_filter = ('status', 'month', 'publisher')
    search_fields = ('drs__campaign_name', 'publisher__company_name')

# Register your models here.
