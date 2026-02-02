#!/bin/bash

# GoGrabit Startup Script

echo "🚀 Starting GoGrabit Backend..."

# Activate virtual environment
source venv/bin/activate

# Check if database exists
if [ ! -f "db.sqlite3" ]; then
    echo "📦 Setting up database..."
    python manage.py migrate
    python manage.py seed_products
    echo "✅ Database setup complete!"
fi

# Start Django server
echo "🌐 Starting Django server on http://localhost:8000"
echo "📱 Customer Interface: http://localhost:8000/"
echo "⚙️  Admin Panel: http://localhost:8000/admin.html"
echo "🔑 Default Admin PIN: 1234"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver 0.0.0.0:8000
