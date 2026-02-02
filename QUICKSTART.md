# GoGrabit - Quick Start Guide

## 🚀 Getting Started (5 minutes)

### 1. Start the Server

```bash
cd /home/ug/Desktop/shopy/dj
./start.sh
```

The server will start at **http://localhost:8000**

### 2. Access the Application

- **Customer Interface**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin.html (PIN: 1234)
- **Django Admin**: http://localhost:8000/admin/

### 3. Start Background Job (Optional - In New Terminal)

```bash
cd /home/ug/Desktop/shopy/dj
./start_background_job.sh
```

This monitors and auto-cancels expired orders every 5 minutes.

---

## 📱 How to Use

### Customer Flow

1. **Browse Products**
   - Open http://localhost:8000/
   - Search and filter by category
   - Add items to cart

2. **Create Profile** (First Time)
   - Click profile icon (👤)
   - Enter name, phone, room number
   - Save profile

3. **Place Order**
   - Click "Cart" button
   - Review items
   - Click "Confirm Reserve"
   - Order is created with 15-minute expiration

4. **Track Order**
   - View order status in banner
   - See countdown timer
   - Cancel if needed

### Admin Flow

1. **Login to Admin Panel**
   - Go to http://localhost:8000/admin.html
   - Enter PIN: **1234**

2. **View Dashboard**
   - See today's revenue and orders
   - Monitor low stock alerts
   - View active orders

3. **Process Orders**
   - See new order notifications
   - Click "Mark as Picked" on order
   - Prepare items
   - Collect payment
   - Mark as "Completed"

4. **Manage Products**
   - Add new products
   - Update stock levels
   - Edit prices
   - Deactivate products

5. **Export Data**
   - Export products as CSV
   - Export orders as CSV
   - Download for analysis

---

## 🔧 Configuration

### Change Admin PIN

**Option 1: Environment Variable**
```bash
export ADMIN_PIN="your_new_pin"
./start.sh
```

**Option 2: Settings File**
Edit `backend/settings.py`:
```python
ADMIN_PIN = os.environ.get('ADMIN_PIN', 'your_new_pin')
```

### Enable Telegram Notifications

1. **Create Bot**
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Follow instructions
   - Copy bot token

2. **Get Chat ID**
   - Add bot to group or use personal chat
   - Send message to bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Find `chat.id` in response

3. **Configure**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ./start.sh
   ```

4. **Set Webhook** (for inline buttons)
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://yourdomain.com/api/telegram/webhook"
   ```

---

## 🧪 Testing the API

### Get All Products
```bash
curl http://localhost:8000/api/products
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"productId": 1, "name": "Lays Classic", "price": 20, "qty": 2}
    ],
    "customerName": "Test User",
    "phoneNumber": "9876543210",
    "roomNumber": "A-101"
  }'
```

### Get Admin Stats (with PIN)
```bash
curl -H "X-Admin-Pin: 1234" http://localhost:8000/api/admin/stats
```

### Mark Order as Picked
```bash
curl -X POST http://localhost:8000/api/admin/orders/<ORDER_ID>/pick \
  -H "Content-Type: application/json" \
  -H "X-Admin-Pin: 1234"
```

---

## 📊 Database Management

### Reset Everything
```bash
rm db.sqlite3
rm -rf api/migrations
python manage.py makemigrations api
python manage.py migrate
python manage.py seed_products
```

### Add More Products
Edit `api/management/commands/seed_products.py` and run:
```bash
python manage.py seed_products
```

### Backup Database
```bash
python manage.py dumpdata > backup.json
```

### Restore Database
```bash
python manage.py loaddata backup.json
```

---

## 🐛 Troubleshooting

### Port 8000 Already in Use
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 8001
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Reset Admin PIN
If you forgot the PIN, edit `backend/settings.py`:
```python
ADMIN_PIN = '1234'  # Reset to default
```

### Database Locked Error
```bash
# Close all terminals running Django
# Delete database and recreate
rm db.sqlite3
python manage.py migrate
python manage.py seed_products
```

### Module Not Found Error
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📈 Production Deployment Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Change `SECRET_KEY`
- [ ] Set strong `ADMIN_PIN`
- [ ] Use PostgreSQL/MySQL
- [ ] Set up Gunicorn/uWSGI
- [ ] Configure Nginx
- [ ] Enable SSL (HTTPS)
- [ ] Set up Telegram webhook
- [ ] Use supervisor/systemd for background job
- [ ] Configure proper CORS origins
- [ ] Set up logging
- [ ] Enable database backups
- [ ] Set up monitoring

---

## 🔑 Default Credentials

- **Admin PIN**: `1234`
- **Django Admin**: Create with `python manage.py createsuperuser`

---

## 📞 API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/products` | GET | No | List products |
| `/api/orders` | POST | No | Create order |
| `/api/orders/<id>` | GET | No | Get order |
| `/api/orders/<id>/cancel` | POST | No | Cancel order |
| `/api/admin/stats` | GET | PIN | Dashboard stats |
| `/api/admin/products` | GET/POST | PIN | Manage products |
| `/api/admin/orders/<id>/pick` | POST | PIN | Mark picked |
| `/api/admin/orders/<id>/complete` | POST | PIN | Mark completed |
| `/api/admin/export?type=products` | GET | PIN | Export CSV |

---

## ✨ Features at a Glance

✅ 15-minute order expiration with auto-cancellation  
✅ Automatic stock management  
✅ Real-time Telegram notifications  
✅ Inline action buttons in Telegram  
✅ Customer order tracking  
✅ Admin dashboard with analytics  
✅ Low stock alerts  
✅ CSV export  
✅ Order history by phone  
✅ Background job for cleanup  
✅ Mobile-responsive UI  
✅ Dark mode support  

---

## 🎯 Next Steps

1. Customize products in `seed_products.py`
2. Set up Telegram integration
3. Configure admin PIN
4. Test order flow end-to-end
5. Set up background job as system service
6. Plan production deployment

---

**Need Help?** Check `README.md` for detailed documentation.
