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
            try:
                # Clean and validate the data
                order_data = {
                    'order_id': str(data['id']),
                    'order_number': str(data['order_number']),
                    'email': data.get('email') or None,
                    'total_price': float(data['total_price']),
                    'raw_data': data
                }
                
                # Create or update the order
                order, created = ShopifyWebhookOrder.objects.update_or_create(
                    order_id=order_data['order_id'],
                    defaults={
                        'order_number': order_data['order_number'],
                        'email': order_data['email'],
                        'total_price': order_data['total_price'],
                        'raw_data': order_data['raw_data']
                    }
                )
                
                # Log success
                action = "created" if created else "updated"
                print(f"Successfully {action} order {order.order_number}")
                print(f"Order details - ID: {order.order_id}, Number: {order.order_number}, "
                      f"Email: {order.email}, Price: {order.total_price}")
                
                # Return success response with order details
                return JsonResponse({
                    "status": "success",
                    "message": f"Order {action} successfully",
                    "order": {
                        "id": order.order_id,
                        "number": order.order_number,
                        "email": order.email,
                        "total_price": str(order.total_price)
                    }
                }, status=200)
                
            except (ValueError, TypeError) as e:
                print(f"Data validation error: {str(e)}")
                return HttpResponse("Invalid data format", status=400)
            except Exception as e:
                print(f"Unexpected error saving order: {str(e)}")
                return HttpResponse("Error saving order", status=500)
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
    """
    Verify that the webhook request came from Shopify using HMAC-SHA256.
    
    Args:
        data: The raw request body
        hmac_header: The X-Shopify-Hmac-SHA256 header value
        webhook_secret: The webhook secret key from Shopify
    
    Returns:
        bool: True if verification passes, False otherwise
    """
    try:
        if not webhook_secret or not hmac_header:
            print("Missing webhook secret or HMAC header")
            return False
            
        digest = hmac.new(
            webhook_secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).digest()
        computed_hmac = base64.b64encode(digest).decode('utf-8')
        
        # Use hmac.compare_digest for timing-attack safe comparison
        is_valid = hmac.compare_digest(computed_hmac, hmac_header)
        
        if not is_valid:
            print("HMAC verification failed - signatures don't match")
        
        return is_valid
        
    except Exception as e:
        print(f"Error verifying webhook: {str(e)}")
        return False
