# Deployment Guide for Render

## Prerequisites
- GitHub repository with your code
- Render account (https://render.com)
- All required API keys

## Step 1: Database Setup on Render

1. Go to Render Dashboard
2. Click "New +" and select "PostgreSQL"
3. Configure:
   - **Name**: `mypage-db` (or your preferred name)
   - **Database**: `mypage`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
4. Click "Create Database"
5. Copy the **Internal Database URL** for later use

## Step 2: Web Service Setup on Render

1. Click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `mypage` (or your preferred name)
   - **Region**: Same as database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn mypage.wsgi:application --log-file -`
   - **Plan**: Free (or paid for production)

## Step 3: Environment Variables

Add these environment variables in Render Dashboard → Your Web Service → Environment:

### Required Variables
```
SECRET_KEY=<generate-a-long-random-string>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
CSRF_TRUSTED_ORIGINS=https://<your-app-name>.onrender.com
DATABASE_URL=<paste-internal-database-url-from-step-1>
```

### API Keys (from your .env file)
```
GEMINI_API_KEY=<your-gemini-api-key>
OPENWEATHER_API_KEY=<your-openweather-api-key>
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
TWILIO_PHONE_NUMBER=<your-twilio-phone>
```

### Python Version (Optional but Recommended)
```
PYTHON_VERSION=3.12.0
```

## Step 4: Deploy

1. Click "Create Web Service"
2. Render will:
   - Install dependencies from `requirements.txt`
   - Run `build.sh` (collectstatic & migrate)
   - Start your application with gunicorn
3. Monitor the deploy logs for any errors

## Step 5: Post-Deployment

### Create Superuser
1. In Render Dashboard, go to your web service
2. Click "Shell" tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin account

### Test Your Application
1. Visit `https://<your-app-name>.onrender.com`
2. Test key features:
   - User registration/login
   - Crop dictionary
   - Image uploads
   - API integrations

### Access Admin Panel
Visit `https://<your-app-name>.onrender.com/admin`

## Important Notes

### Static Files
- WhiteNoise is configured to serve static files
- Static files are collected during build via `collectstatic`
- No additional CDN needed for basic setup

### Media Files
- User-uploaded files (images) will be stored on the server's disk
- **Warning**: Render's free tier uses ephemeral storage (files lost on restart)
- For production, consider using:
  - AWS S3
  - Cloudinary
  - Other cloud storage services

### Database Backups
- Free PostgreSQL tier on Render doesn't include automatic backups
- For production, upgrade to paid plan with backups

### Monitoring
- Check logs in Render Dashboard → Your Service → Logs
- Set up error monitoring (e.g., Sentry) for production

## Troubleshooting

### Build Failures
- Check build logs for missing dependencies
- Verify `requirements.txt` is up to date
- Ensure `build.sh` has correct permissions (executable)

### Database Connection Errors
- Verify `DATABASE_URL` is set correctly
- Check database is in same region as web service
- Use **Internal Database URL**, not External

### Static Files Not Loading
- Verify `STATIC_ROOT` and `STATICFILES_STORAGE` in settings.py
- Check WhiteNoise is in `MIDDLEWARE`
- Ensure `collectstatic` runs successfully in build logs

### 502 Bad Gateway
- Check if gunicorn is starting correctly
- Verify `ALLOWED_HOSTS` includes `.onrender.com`
- Check application logs for startup errors

## Updating Your App

1. Push changes to GitHub
2. Render will auto-deploy (if enabled)
3. Or manually trigger deploy from Render Dashboard

## Security Checklist

- [x] `DEBUG=False` in production
- [x] Strong `SECRET_KEY` (use random generator)
- [x] `ALLOWED_HOSTS` configured
- [x] `CSRF_TRUSTED_ORIGINS` set
- [x] Secure cookies enabled (HTTPS)
- [x] `.env` file in `.gitignore`
- [ ] Set up custom domain (optional)
- [ ] Configure HTTPS (automatic on Render)

## Cost Estimate

**Free Tier:**
- Web Service: Free for 750 hours/month
- PostgreSQL: Free (90 days, then upgrade required)
- Note: Free services spin down after 15 minutes of inactivity

**Recommended Paid Tier (for production):**
- Web Service: $7/month (always-on)
- PostgreSQL: $7/month (with backups)
