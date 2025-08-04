from django.db import models

class ShopifyWebhookOrder(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    order_number = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    raw_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.email or 'No email'}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Shopify Webhook Order"
        verbose_name_plural = "Shopify Webhook Orders"
