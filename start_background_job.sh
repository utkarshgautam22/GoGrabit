#!/bin/bash

# Background Job Script for Order Expiration

echo "⏰ Starting Order Expiration Background Job..."
echo "Checking for expired orders every 5 minutes (300 seconds)"
echo "Press Ctrl+C to stop"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run background job
python manage.py process_expired_orders --interval 300
