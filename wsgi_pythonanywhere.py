import os
import sys

# Add the project directory to the sys.path
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/shopify-webhook-django'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'webhooktest.settings'

# Import the Django WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
