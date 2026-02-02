# GoGrabit - Django Backend

A complete Django-based backend for the GoGrabit order management system with Telegram integration.

## Features

- ✅ Product management (CRUD operations)
- ✅ Order lifecycle management (Reserved → Picked → Completed)
- ✅ Automatic stock deduction/restoration
- ✅ 15-minute order expiration with auto-cancellation
- ✅ Telegram bot integration with inline action buttons
- ✅ Admin dashboard with analytics
- ✅ CSV data export
- ✅ Low stock alerts
- ✅ Background job for order cleanup
- ✅ RESTful API with Django REST Framework
- ✅ CORS-enabled for frontend integration

## Project Structure

```
dj/
├── api/                          # Main API app
│   ├── management/
│   │   └── commands/
│   │       ├── process_expired_orders.py  # Background job
│   │       └── seed_products.py           # Sample data seeder
│   ├── models.py                 # Product, Order, AdminSettings models
│   ├── serializers.py            # REST API serializers
│   ├── views.py                  # API endpoints
│   ├── urls.py                   # API URL routing
│   ├── admin.py                  # Django admin config
│   └── telegram_bot.py           # Telegram integration
├── backend/                      # Django project settings
│   ├── settings.py              # Main settings
│   └── urls.py                  # Root URL config
├── frontend/                     # Frontend HTML/CSS/JS
│   ├── index.html               # Customer interface
│   ├── admin.html               # Admin panel
│   ├── script.js                # Frontend logic
│   └── styles.css               # Styling
├── manage.py                    # Django management script
└── requirements.txt             # Python dependencies
```

## Installation

### 1. Clone/Navigate to project
```bash
cd /home/ug/Desktop/shopy/dj
```

### 2. Create virtual environment (already done)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations (already done)
```bash
python manage.py migrate
```

### 5. Seed sample products (optional)
```bash
python manage.py seed_products
```

### 6. Create admin user (optional)
```bash
python manage.py createsuperuser
```

## Configuration

### Environment Variables

Set these in your environment or `.env` file:

```bash
# Telegram Bot Configuration (optional)
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# Admin PIN (default: 1234)
export ADMIN_PIN="your_secure_pin"
```

### Getting Telegram Credentials

1. **Bot Token**: 
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Chat ID**:
   - Add your bot to a group or use your personal chat
   - Send a message to the bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Find `chat.id` in the response

3. **Set Webhook** (for button callbacks):
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://yourdomain.com/api/telegram/webhook"
   ```

## Running the Application

### Start Django Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### Start Background Job (in separate terminal)
```bash
source venv/bin/activate
python manage.py process_expired_orders --interval 300
```

The background job checks for expired orders every 5 minutes (300 seconds).

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | Get all active products |
| GET | `/api/orders` | Get all orders |
| GET | `/api/orders/<order_id>` | Get specific order |
| POST | `/api/orders` | Create new order |
| POST | `/api/orders/<order_id>/cancel` | Cancel order |

### Admin Endpoints (require PIN)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/admin/products` | List/create products |
| PUT/DELETE | `/api/admin/products/<id>` | Update/delete product |
| POST | `/api/admin/products/bulk` | Bulk update products |
| POST | `/api/admin/orders/<id>/pick` | Mark order as picked |
| POST | `/api/admin/orders/<id>/complete` | Mark order as completed |
| GET | `/api/admin/stats` | Get dashboard stats |
| GET | `/api/admin/low-stock` | Get low stock products |
| GET | `/api/admin/active-orders` | Get active orders |
| POST | `/api/admin/verify-pin` | Verify admin PIN |
| GET | `/api/admin/export?type=products` | Export products CSV |
| GET | `/api/admin/export?type=orders` | Export orders CSV |
| POST | `/api/admin/clear-database` | Clear all data |

### Admin Authentication

Include PIN in request header:
```
X-Admin-Pin: 1234
```

Or in request body/query:
```json
{"pin": "1234"}
```

## Order Lifecycle

```
1. Customer creates order
   ↓
2. Stock deducted immediately
   ↓
3. Status: RESERVED (15 min timer)
   ↓
4. Telegram notification sent
   ↓
5. Admin marks PICKED (via button or panel)
   ↓
6. Admin collects payment
   ↓
7. Status: COMPLETED
```

**Alternative flows:**
- Customer cancels → Stock restored → CANCELLED
- Timer expires → Auto-cancel → Stock restored → CANCELLED

## Frontend Access

- **Customer Interface**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin.html
- **Django Admin**: http://localhost:8000/admin/

## Default Admin PIN

The default admin PIN is `1234`. Change it by:
1. Setting `ADMIN_PIN` environment variable, OR
2. Editing `ADMIN_PIN` in `backend/settings.py`

## Sample Order Request

```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"productId": 1, "name": "Lays Classic", "price": 20, "qty": 2},
      {"productId": 5, "name": "Coca Cola", "price": 40, "qty": 1}
    ],
    "customerName": "John Doe",
    "phoneNumber": "9876543210",
    "roomNumber": "A-101",
    "notes": ""
  }'
```

## Troubleshooting

### Port already in use
```bash
# Find process
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)
```

### Telegram not working
- Check if `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Verify bot token is valid
- Ensure bot is added to the chat/group
- Check webhook is set correctly

### Static files not loading
```bash
python manage.py collectstatic
```

## Production Deployment

1. Set `DEBUG = False` in settings
2. Configure `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up proper CORS origins
5. Use PostgreSQL/MySQL instead of SQLite
6. Set up Gunicorn/uWSGI
7. Configure Nginx as reverse proxy
8. Set up SSL certificate
9. Use supervisor/systemd for background job

## Database Management

### Reset database
```bash
rm db.sqlite3
rm -rf api/migrations
python manage.py makemigrations api
python manage.py migrate
python manage.py seed_products
```

### Backup database
```bash
python manage.py dumpdata > backup.json
```

### Restore database
```bash
python manage.py loaddata backup.json
```

## License

This project is for educational/commercial use.

## Support

For issues or questions, check the system flow documentation or contact the development team.
