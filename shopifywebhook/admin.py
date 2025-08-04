from django.contrib import admin
from .models import ShopifyWebhookOrder

@admin.register(ShopifyWebhookOrder)
class ShopifyWebhookOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'email', 'total_price', 'created_at']
    search_fields = ['order_number', 'email']
    readonly_fields = ['order_id', 'order_number', 'email', 'total_price', 'raw_data', 'created_at']
    ordering = ['-created_at']
