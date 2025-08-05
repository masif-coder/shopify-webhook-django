import os
import sys

# Add your project directory to the sys.path
project_home = '/home/Asifjammu/webhook'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'webhooktest.settings'

# Import and initialize Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()