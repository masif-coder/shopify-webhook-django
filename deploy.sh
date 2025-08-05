#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting deployment process...${NC}"

# 1. Create and update virtual environment
echo -e "${GREEN}Setting up virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
python manage.py migrate

# 3. Collect static files
echo -e "${GREEN}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# 4. Test the application
echo -e "${GREEN}Running tests...${NC}"
python manage.py test

# 5. Create or update .env file
if [ ! -f .env ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cat > .env << EOL
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
ALLOWED_HOSTS=Asifjjj.pythonanywhere.com
EOL
    echo -e "${RED}Please update the .env file with your actual values${NC}"
fi

echo -e "${GREEN}Deployment preparation complete!${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo "1. Update your .env file with actual values"
echo "2. Configure your Python Anywhere web app"
echo "3. Update your WSGI file on Python Anywhere"
echo "4. Reload your Python Anywhere web app"
