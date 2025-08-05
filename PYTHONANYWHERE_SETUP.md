# Python Anywhere Deployment Steps

## 1. Initial Setup
1. Log in to PythonAnywhere
2. Open a Bash console
3. Clone your repository:
```bash
cd ~
git clone https://github.com/masif-coder/shopify-webhook-django.git
cd shopify-webhook-django
```

## 2. Virtual Environment Setup
```bash
mkvirtualenv --python=/usr/bin/python3.10 shopify-webhook-env
workon shopify-webhook-env
pip install -r requirements.txt
```

## 3. Environment Variables
Create `.env` file in the project root:
```bash
cd ~/shopify-webhook-django
nano .env
```

Add these variables (replace with your actual values):
```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
ALLOWED_HOSTS=your-username.pythonanywhere.com
```

## 4. Database Setup
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## 5. Web App Configuration
1. Go to Web tab in PythonAnywhere
2. Click "Add a new web app"
3. Choose "Manual Configuration"
4. Select Python 3.10

### Configure Virtual Environment
- Set virtualenv path: `/home/Asifjjj/.virtualenvs/shopify-webhook-env`

### Configure WSGI File
- Click on the WSGI configuration file link
- Replace content with wsgi_pythonanywhere.py content

### Static Files
Add in the Static Files section:
- URL: /static/
- Directory: /home/Asifjjj/shopify-webhook-django/staticfiles

## 6. Update Shopify Webhook URL
1. Go to your Shopify admin
2. Update webhook URL to: `https://Asifjjj.pythonanywhere.com/webhooks/shopify/order/create/`

## 7. Final Steps
1. Go to the Web tab
2. Click "Reload" button
3. Visit your site: `https://Asifjjj.pythonanywhere.com`

## Troubleshooting
- Check the error logs in the Web tab
- Ensure all environment variables are set correctly
- Make sure the virtualenv is activated when installing packages
- Verify the webhook URL in Shopify admin
