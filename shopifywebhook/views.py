import json
import hmac
import hashlib
import base64
from decimal import Decimal
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import ShopifyWebhookOrder

def validate_order_data(data):
    """
    Validate and clean order data from Shopify webhook.
    
    Args:
        data (dict): Raw order data from Shopify webhook
        
    Returns:
        dict: Cleaned and validated order data
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary, got {type(data)}")

    required_fields = ['id', 'order_number', 'total_price']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
    try:
        # Clean and validate order ID
        try:
            order_id = str(data['id']).strip()
            if not order_id:
                raise ValueError("Order ID cannot be empty")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid order ID: {str(e)}")
            
        # Clean and validate order number
        try:
            order_number = str(data['order_number']).strip()
            if not order_number:
                raise ValueError("Order number cannot be empty")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid order number: {str(e)}")
            
        # Clean and validate total price
        try:
            total_price = Decimal(str(data['total_price']))
            if total_price < 0:
                raise ValueError("Total price cannot be negative")
        except (TypeError, ValueError, DecimalException) as e:
            raise ValueError(f"Invalid total price: {str(e)}")
            
        # Clean and validate email (optional)
        email = data.get('email')
        if email:
            email = str(email).strip()
            if not '@' in email:
                raise ValueError("Invalid email format")
                
        order_data = {
            'order_id': order_id,
            'order_number': order_number,
            'email': email or None,
            'total_price': total_price,
            'raw_data': data
        }
        
        print("\n=== Validated Order Data ===")
        for key, value in order_data.items():
            if key != 'raw_data':  # Skip printing raw data
                print(f"{key}: {value}")
        print("==========================")
        
        return order_data
        
    except Exception as e:
        print(f"\nValidation Error: {str(e)}")
        print(f"Input data: {json.dumps(data, indent=2)}")
        raise ValueError(f"Data validation failed: {str(e)}")

def index(request):
    """
    View to display all orders in a nice HTML interface
    """
    try:
        print("\n=== Dashboard Request ===")
        print(f"Request Method: {request.method}")
        print(f"Host: {request.get_host()}")
        print(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
        
        # Get all orders with debug logging
        try:
            orders = ShopifyWebhookOrder.objects.all().order_by('-created_at')
            order_count = orders.count()
            print(f"Found {order_count} orders in database")
        except Exception as e:
            print(f"Error fetching orders: {str(e)}")
            orders = []
            order_count = 0
        
        # Get the latest order if any exists
        try:
            latest_order = orders.first() if orders.exists() else None
            if latest_order:
                print(f"Latest order: {latest_order.order_number} - {latest_order.email} - {latest_order.created_at}")
        except Exception as e:
            print(f"Error getting latest order: {str(e)}")
            latest_order = None
        
        # Get the webhook URL from request
        try:
            webhook_url = f"https://{request.get_host()}/webhooks/shopify/order/create/"
            print(f"Webhook URL: {webhook_url}")
        except Exception as e:
            print(f"Error constructing webhook URL: {str(e)}")
            webhook_url = "Error generating webhook URL"
        
        # Build context for template
        context = {
            'orders': orders,
            'latest_order': latest_order,
            'webhook_url': webhook_url,
            'order_count': order_count,
            'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return render(request, 'shopifywebhook/orders.html', context)
        
    except Exception as e:
        print(f"Unexpected error in dashboard view: {str(e)}")
        error_context = {
            'error_message': "An error occurred while loading the dashboard.",
            'webhook_url': f"https://{request.get_host()}/webhooks/shopify/order/create/",
            'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        return render(request, 'shopifywebhook/orders.html', error_context, status=500)

@csrf_exempt
def webhook_order_created(request):
    print("\n=== Webhook Request Received ===")
    print(f"Method: {request.method}")
    print(f"Content Type: {request.content_type}")
    print(f"Request Path: {request.path}")
    print(f"Query String: {request.META.get('QUERY_STRING', '')}")
    print("Headers:")
    for key, value in request.headers.items():
        print(f"  {key}: {value}")
    
    if request.method == 'GET':
        return JsonResponse({
            "status": "ok",
            "message": "Webhook endpoint is live (GET request)",
            "timestamp": datetime.now().isoformat()
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
        # Log raw request body for debugging
        print("\n=== Raw Request Body ===")
        try:
            print(request.body.decode('utf-8'))
        except UnicodeDecodeError:
            print("(Could not decode request body as UTF-8)")
        print("=====================")

        # Parse webhook data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")
            print(f"Request Body (first 1000 chars): {request.body[:1000]}")
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON data",
                "details": str(e)
            }, status=400)

        # Log parsed data
        print("\n=== Parsed Order Data ===")
        print(json.dumps(data, indent=2))
        print("=====================")
        
        # Extract and validate important fields
        print("\n=== Order Details ===")
        for field in ['id', 'order_number', 'email', 'total_price']:
            value = data.get(field)
            print(f"{field}: {value} (type: {type(value)})")
        print("=====================")
        
        # Validate and process the order
        try:
            # Clean and validate the data
            order_data = validate_order_data(data)
            
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
                    "total_price": str(order.total_price),
                    "created_at": order.created_at.isoformat()
                }
            }, status=200)
            
        except ValueError as e:
            print(f"Data validation error: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": "Invalid data format",
                "details": str(e)
            }, status=400)
        except Exception as e:
            print(f"Error processing order: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": "Internal server error",
                "details": str(e)
            }, status=500)
        
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
