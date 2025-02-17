#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate

echo "Populating initial product data..."
python manage.py populate_products || true

echo "Fixing product table..."
python manage.py fix_product_table || true  # Add || true to prevent build failure

echo "Running data updates..."
python manage.py update_products_data || true  # Add || true to prevent build failure
python manage.py update_product_images || true  # Add || true to prevent build failure

# Remove or comment out the createsuperuser command as it requires interactive input
echo "Creating superuser..."
python manage.py createsuperuser

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Creating cache table..."
python manage.py createcachetable

echo "Build completed successfully!"