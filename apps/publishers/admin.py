from django.contrib import admin

# Register your models here.
from .models import Publisher, Wishlist

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'name', 'teams_id', 'telegram_id', 'contact_person', 'email', 'is_active')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'publisher', 'desired_campaign', 'geo', 'category')

# Register your models here.
