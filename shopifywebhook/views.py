import json
import hmac
import hashlib
import base64
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ShopifyWebhookOrder

def index(request):
    """
    View to display all orders in a nice HTML interface
    """
    # Get all orders
    orders = ShopifyWebhookOrder.objects.all().order_by('-created_at')
    
    # Get the webhook URL from request
    webhook_url = f"https://{request.get_host()}/webhooks/shopify/order/create/"
    
    context = {
        'orders': orders,
        'webhook_url': webhook_url,
    }
    
    return render(request, 'shopifywebhook/orders.html', context)

@csrf_exempt
def webhook_order_created(request):
    if request.method == 'GET':
        return JsonResponse({
            "status": "ok",
            "message": "Webhook endpoint is live (GET request)"
        })

    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    print("Received webhook request")
    print(f"Request headers: {dict(request.headers)}")
    
    # Verify Shopify webhook
    hmac_header = request.META.get('HTTP_X_SHOPIFY_HMAC_SHA256', '')
    webhook_secret = settings.SHOPIFY_WEBHOOK_SECRET
    
    print(f"Verifying webhook with HMAC: {hmac_header}")
    
    if not verify_webhook(request.body, hmac_header, webhook_secret):
        print("Webhook verification failed!")
        return HttpResponse("Invalid webhook signature", status=401)

    try:
        # Parse webhook data
        data = json.loads(request.body)
        print(f"Received order data: {json.dumps(data, indent=2)}")
        
        # Try to get existing order or create new one
        order, created = ShopifyWebhookOrder.objects.update_or_create(
            order_id=data['id'],
            defaults={
                'order_number': data['order_number'],
                'email': data.get('email'),
                'total_price': data['total_price'],
                'raw_data': data
            }
        )
        
        if created:
            print(f"Successfully created new order: {order}")
        else:
            print(f"Successfully updated existing order: {order}")
        
        return HttpResponse("Order processed successfully", status=200)
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw request body: {request.body}")
        return HttpResponse("Invalid JSON data", status=400)
    except KeyError as e:
        print(f"Missing required field: {e}")
        return HttpResponse(f"Missing required field: {e}", status=400)
    except Exception as e:
        print(f"Unexpected error processing webhook: {e}")
        return HttpResponse("Internal server error", status=500)

def verify_webhook(data, hmac_header, webhook_secret):
    digest = hmac.new(
        webhook_secret.encode('utf-8'),
        data,
        hashlib.sha256
    ).digest()
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed_hmac, hmac_header)
