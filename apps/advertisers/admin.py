from django.contrib import admin
from .models import Advertiser

@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'contact_person', 'email', 'is_active')

# Register your models here.
