#!/bin/bash

echo "Starting PythonAnywhere setup..."

# Navigate to home directory
cd ~

# Clone repository if it doesn't exist
if [ ! -d "shopify-webhook-django" ]; then
    echo "Cloning repository..."
    git clone https://github.com/masif-coder/shopify-webhook-django.git
fi

# Navigate to project directory
cd shopify-webhook-django

# Pull latest changes
echo "Updating repository..."
git pull origin main

# Create virtual environment if it doesn't exist
if [ ! -d "$WORKON_HOME/shopify-webhook-env" ]; then
    echo "Creating virtual environment..."
    mkvirtualenv --python=/usr/bin/python3.10 shopify-webhook-env
fi

# Activate virtual environment
echo "Activating virtual environment..."
workon shopify-webhook-env

# Install/upgrade pip and requirements
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
ALLOWED_HOSTS=your-username.pythonanywhere.com
EOL
    echo "Please update the .env file with your actual values"
fi

echo "Setup complete! Next steps:"
echo "1. Update the .env file with your actual values"
echo "2. Configure your web app in the PythonAnywhere dashboard"
echo "3. Reload your web app"
