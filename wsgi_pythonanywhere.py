import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
project_home = '/home/Asifjjj/shopify-webhook-django'
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Add your project directory to the sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webhooktest.settings')

# Import and initialize Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()