#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate
python manage.py populate_products

echo "Creating superuser..."
python manage.py createsuperuser

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Creating cache table..."
python manage.py createcachetable

echo "Build completed successfully!"