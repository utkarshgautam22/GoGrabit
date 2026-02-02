# GoGrabit - Order Management System

A modern Django-based order management system for campus stores with real-time inventory, 15-minute reservations, and Telegram notifications.

## 🚀 Quick Start (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Seed sample products
python manage.py seed_products

# Start server
python manage.py runserver

# Start background job (in another terminal)
./start_background_job.sh
```

Visit http://localhost:8000

## 📦 Features

- **Product Management**: Real-time stock tracking with low-stock alerts
- **Smart Reservations**: 15-minute hold system with auto-expiration
- **Order Lifecycle**: Reserved → Picked → Completed workflow
- **Telegram Integration**: Instant order notifications with inline actions
- **Mobile-First UI**: Responsive design optimized for mobile devices
- **Admin Dashboard**: Complete analytics and management tools
- **One-Order-Per-User**: Prevents multiple simultaneous orders
- **Auto-Profile Save**: Customer details saved automatically

## 🌐 Deploy to Render

See detailed guide: [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)

### Quick Steps:
1. Push code to GitHub
2. Create PostgreSQL database on Render
3. Create Web Service on Render
4. Set environment variables
5. Deploy!

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection URL | Production |
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `ALLOWED_HOSTS` | Comma-separated hostnames | Yes |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated URLs | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Optional |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | Optional |
| `ADMIN_PIN` | Admin panel PIN | Optional |

## 📁 Project Structure

```
dj/
├── api/                    # Django app
│   ├── models.py          # Product, Order, AdminSettings
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API endpoints
│   ├── telegram_bot.py    # Telegram integration
│   └── management/
│       └── commands/
│           ├── seed_products.py
│           └── process_expired_orders.py
├── backend/               # Django project settings
├── frontend/              # HTML/CSS/JS frontend
│   ├── index.html        # Customer UI
│   ├── admin.html        # Admin UI
│   ├── script.js         # Customer logic
│   └── styles.css        # Styling
├── build.sh              # Render build script
├── Procfile              # Render process file
├── runtime.txt           # Python version
├── requirements.txt      # Dependencies
└── manage.py             # Django CLI
```

## 🔌 API Endpoints

### Products
- `GET /api/products` - List all active products
- `POST /api/products` - Create product (admin)
- `PATCH /api/products/{id}` - Update product (admin)
- `DELETE /api/products/{id}` - Delete product (admin)

### Orders
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create order
- `GET /api/orders/{id}` - Get order details
- `POST /api/orders/{id}/cancel` - Cancel order
- `POST /api/orders/{id}/mark-picked` - Mark as picked (admin)
- `POST /api/orders/{id}/mark-completed` - Mark as completed (admin)

### Analytics
- `GET /api/analytics` - Get sales analytics (admin)

## 🎨 Tech Stack

- **Backend**: Django 6.0.1, Django REST Framework 3.16.1
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Vanilla JavaScript, CSS3
- **Deployment**: Render, Gunicorn, WhiteNoise
- **Notifications**: python-telegram-bot 22.6

## 🔐 Security Features

- CSRF protection
- CORS configuration
- Secure cookies in production
- Environment-based configuration
- PIN-based admin access
- Phone number validation

## 📱 Browser Support

- Chrome/Edge 90+
- Safari 14+
- Firefox 88+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🐛 Troubleshooting

### Build fails on Render
- Check Python version in `runtime.txt`
- Verify all dependencies in `requirements.txt`
- Review build logs in Render dashboard

### Static files not loading
```bash
python manage.py collectstatic --no-input
```

### Database connection errors
- Verify `DATABASE_URL` is correct
- Ensure database and web service are in same region

### CSRF/CORS errors
- Add your domain to `CSRF_TRUSTED_ORIGINS`
- Add your domain to `CORS_ALLOWED_ORIGINS`

## 📄 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📞 Support

For issues and questions:
- Check [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
- Review [QUICKSTART.md](./QUICKSTART.md)
- Open an issue on GitHub

---

**Built with ❤️ for campus stores**

Last Updated: February 2, 2026
