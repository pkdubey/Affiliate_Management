from django.contrib import admin

# Register your models here.
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'publisher', 'drs', 'status', 'created_at')

# Register your models here.
