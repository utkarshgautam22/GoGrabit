#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Seed products if needed (optional - comment out if you want to preserve existing data)
# python manage.py seed_products
