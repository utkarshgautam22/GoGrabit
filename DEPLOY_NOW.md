# 🚀 Render Deployment - Quick Reference

## Your App is Ready for Render! ✅

All files have been configured for production deployment.

---

## 📋 Deployment Checklist

### Files Created/Modified:
- ✅ `build.sh` - Render build script
- ✅ `Procfile` - Process configuration
- ✅ `runtime.txt` - Python 3.11.9
- ✅ `requirements.txt` - Updated with production dependencies
- ✅ `backend/settings.py` - Production-ready configuration
- ✅ `RENDER_DEPLOYMENT.md` - Complete deployment guide
- ✅ `README_PRODUCTION.md` - Production documentation

### Dependencies Added:
- ✅ `gunicorn` - WSGI server
- ✅ `whitenoise` - Static file serving
- ✅ `dj-database-url` - Database configuration
- ✅ `psycopg2-binary` - PostgreSQL adapter

---

## 🎯 Next Steps

### 1. Push to GitHub
```bash
cd /home/ug/Desktop/shopy/dj

# Initialize git (if not already done)
git init
git add .
git commit -m "Ready for Render deployment"

# Add remote and push
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Create Render Account
Go to: https://render.com (free tier available)

### 3. Create PostgreSQL Database
1. Dashboard → **New +** → **PostgreSQL**
2. Name: `gograbit-db`
3. Database: `gograbit`
4. Region: Choose closest to you
5. Plan: **Free**
6. **Copy Internal Database URL** 📋

### 4. Create Web Service
1. Dashboard → **New +** → **Web Service**
2. Connect GitHub repository
3. Configure:
   - **Name**: `gograbit` (or your preferred name)
   - **Region**: Same as database
   - **Branch**: `main`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn backend.wsgi:application`
   - **Plan**: Free

### 5. Set Environment Variables

Click **Environment** tab and add:

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db  # From step 3
SECRET_KEY=your-50-char-random-string  # Generate below
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
CORS_ALLOWED_ORIGINS=https://your-app-name.onrender.com
PYTHON_VERSION=3.11.9

# Optional
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
ADMIN_PIN=1234
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 6. Deploy! 🚀
Click **Create Web Service** and wait 5-10 minutes.

---

## 📱 After Deployment

### Get Your App URL
`https://your-app-name.onrender.com`

### Update Environment Variables
Go back and update:
- `ALLOWED_HOSTS` → your actual Render URL
- `CSRF_TRUSTED_ORIGINS` → `https://your-app-name.onrender.com`
- `CORS_ALLOWED_ORIGINS` → `https://your-app-name.onrender.com`

### Create Admin User
In Render Dashboard → Shell:
```bash
python manage.py createsuperuser
```

### Seed Products (Optional)
```bash
python manage.py seed_products
```

### Access Points
- **Customer UI**: `https://your-app-name.onrender.com/`
- **Admin Panel**: `https://your-app-name.onrender.com/admin/`
- **API Docs**: `https://your-app-name.onrender.com/api/`

---

## ⏰ Background Job (Order Expiration)

### Setup Cron Job on Render:
1. Dashboard → **New +** → **Cron Job**
2. Connect same GitHub repo
3. Configure:
   - **Command**: `python manage.py process_expired_orders`
   - **Schedule**: `*/5 * * * *` (every 5 minutes)
4. Add same environment variables

---

## 🔍 Testing

### Test Locally First:
```bash
# Set environment variables
export DEBUG=False
export SECRET_KEY=test-key-12345678901234567890123456789012345678901234567890

# Run with Gunicorn
gunicorn backend.wsgi:application

# Visit: http://localhost:8000
```

### Test on Render:
1. Visit your Render URL
2. Create a test order
3. Check admin panel
4. Verify order expiration (wait 15 min or adjust in code)

---

## 🐛 Common Issues

### Build Fails
```bash
# Check logs in Render dashboard
# Ensure build.sh is executable
chmod +x build.sh
git add build.sh
git commit -m "Make build.sh executable"
git push
```

### Static Files Missing
```bash
python manage.py collectstatic --no-input
```

### Database Error
- Verify DATABASE_URL is correct
- Check database and web service are in same region
- Ensure database is not asleep (free tier limitation)

### CSRF/CORS Error
- Add HTTPS scheme: `https://your-app.onrender.com`
- No trailing slash
- Restart web service after changing env vars

---

## 💰 Render Free Tier

**Limits:**
- Web service sleeps after 15 min inactivity
- 750 hours/month
- PostgreSQL: 1GB storage, 90-day expiry
- 100GB bandwidth/month

**Upgrade for:**
- Always-on service
- More storage
- Custom domains
- Better performance

---

## 📚 Documentation

- **Full Guide**: `RENDER_DEPLOYMENT.md`
- **Project README**: `README_PRODUCTION.md`
- **Local Setup**: `QUICKSTART.md`
- **API Docs**: See `README.md`

---

## ✅ Production Checklist

Before going live:
- [ ] Pushed code to GitHub
- [ ] Created PostgreSQL database on Render
- [ ] Created web service on Render
- [ ] Set all environment variables
- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] `CSRF_TRUSTED_ORIGINS` set
- [ ] Database migrated
- [ ] Admin user created
- [ ] Products seeded
- [ ] Background job configured
- [ ] Tested complete order flow
- [ ] Verified static files load
- [ ] Checked logs for errors

---

## 🎉 You're Ready!

Your GoGrabit app is fully configured for Render deployment.

**Need help?** Check `RENDER_DEPLOYMENT.md` for detailed instructions.

---

Generated: February 2, 2026
