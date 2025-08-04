from django.urls import path
from . import views

app_name = 'shopifywebhook'

urlpatterns = [
    path('', views.index, name='index'),
    path('webhooks/shopify/order/create/', views.webhook_order_created, name='webhook_order_created'),
]
