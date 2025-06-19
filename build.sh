#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate

echo "Populating initial product data..."
python manage.py populate_products --clear || true

#echo "Fixing product table..."
#python manage.py fix_product_table || true  # Add || true to prevent build failure

#echo "Running data updates..."
#python manage.py update_products_data || true  # Add || true to prevent build failure
#python manage.py update_product_images || true  # Add || true to prevent build failure

# Add product variations sync command
#echo "Syncing product variations..."
#python manage.py sync_product_variations || true  # Add || true to prevent build failure

# Create superuser
echo "Creating superuser..."
python manage.py ensure_superuser
echo "Superuser creation completed"

echo "Populating ordertable..."
python manage.py create_dummy_orders --email danieludechukwu117@gmail.com --count 5 || true
echo "Order Population completed"

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Creating cache table..."
python manage.py createcachetable

echo "Build completed successfully!"
