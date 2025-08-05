import os
import sys

# Add the project directory to Python's path
path = '/home/Asifjammu/webhook'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'webhooktest.settings'

# Import and create the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
