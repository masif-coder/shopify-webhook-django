<<<<<<< HEAD
# Shopify Webhook Django Application

A Django application that handles Shopify webhooks for order creation and displays order information.

## Features

- Receives Shopify webhooks for order creation
- Stores order information in a database
- Displays orders in a web interface
- Secure webhook validation

## Setup

1. Clone the repository:
```bash
git clone https://github.com/masif-coder/shopify-webhook-django.git
cd shopify-webhook-django
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy .env.example to .env and fill in your values):
```bash
cp .env.example .env
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file with the following variables:
```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
```

## Deployment

This application is configured for deployment on Railway:

1. Connect your GitHub repository to Railway
2. Set up the environment variables in Railway's dashboard
3. Railway will automatically deploy your application

## Webhook URL

After deployment, your webhook URL will be:
```
https://your-domain.railway.app/webhooks/orders/create/
```

## Security

- The application validates Shopify webhook signatures
- Environment variables are used for sensitive information
- HTTPS is required for webhook endpoints
=======
# shopify-webhook-django
>>>>>>> 3dee018ecf7f8c86f08d981b4660f495a6c5177d
