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
    # Get all orders with debug logging
    orders = ShopifyWebhookOrder.objects.all().order_by('-created_at')
    print(f"Found {orders.count()} orders in database")
    
    # Get the latest order if any exists
    latest_order = orders.first() if orders.exists() else None
    if latest_order:
        print(f"Latest order: {latest_order.order_number} - {latest_order.email} - {latest_order.created_at}")
    
    # Get the webhook URL from request
    webhook_url = f"https://{request.get_host()}/webhooks/shopify/order/create/"
    print(f"Webhook URL: {webhook_url}")
    
    context = {
        'orders': orders,
        'latest_order': latest_order,
        'webhook_url': webhook_url,
    }
    
    return render(request, 'shopifywebhook/orders.html', context)

@csrf_exempt
def webhook_order_created(request):
    print("\n=== Webhook Request Received ===")
    print(f"Method: {request.method}")
    print(f"Content Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
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
    print(f"Webhook Secret from settings: {webhook_secret}")
    
    print(f"Verifying webhook with HMAC: {hmac_header}")
    
    if not webhook_secret:
        print("Warning: SHOPIFY_WEBHOOK_SECRET is not set!")
        return HttpResponse("Webhook secret not configured", status=500)
    
    if not verify_webhook(request.body, hmac_header, webhook_secret):
        print("Webhook verification failed!")
        return HttpResponse("Invalid webhook signature", status=401)

    try:
        # Parse webhook data
        data = json.loads(request.body)
        print(f"Received order data: {json.dumps(data, indent=2)}")
        
        # Print received data for debugging
        print("Processing order data:")
        print(f"Order ID: {data.get('id')}")
        print(f"Order Number: {data.get('order_number')}")
        print(f"Email: {data.get('email')}")
        print(f"Total Price: {data.get('total_price')}")
        
        # Log important fields
        print("=== Order Data ===")
        print(f"Order ID: {data.get('id')}")
        print(f"Order Number: {data.get('order_number')}")
        print(f"Email: {data.get('email')}")
        print(f"Total Price: {data.get('total_price')}")
        print("==================")
        
        # Try to get existing order or create new one
        try:
            order, created = ShopifyWebhookOrder.objects.update_or_create(
                order_id=str(data['id']),  # Convert to string to ensure compatibility
                defaults={
                    'order_number': str(data['order_number']),
                    'email': data.get('email') or None,  # Handle empty email
                    'total_price': float(data['total_price']),  # Convert to float
                    'raw_data': data
                }
            )
            
            # Verify the order was saved
            saved_order = ShopifyWebhookOrder.objects.get(order_id=str(data['id']))
            print(f"Verified saved order: {saved_order}")
            print(f"Order details - Number: {saved_order.order_number}, Email: {saved_order.email}, Price: {saved_order.total_price}")
            
            if created:
                print(f"Successfully created new order: {order}")
            else:
                print(f"Successfully updated existing order: {order}")
            
            return HttpResponse("Order processed successfully", status=200)
        except Exception as e:
            print(f"Error saving order: {str(e)}")
            raise
        
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
