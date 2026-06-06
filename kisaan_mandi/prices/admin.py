from django.contrib import admin
from .models import MarketPrice

@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'mandi_name', 'state', 'modal_price', 'unit', 'date', 'trend']
    list_filter = ['state', 'trend']
    search_fields = ['crop_name', 'mandi_name']
