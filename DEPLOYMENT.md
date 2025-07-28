# 🚀 Railway Deployment Guide

Your Canvas Course Extractor is now ready for Railway hosting!

## ✅ Files Created for Railway

- `Procfile` - Tells Railway how to start your app
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Python dependencies (moved to root)
- `railway.json` - Railway configuration
- `.railwayignore` - Files to exclude from deployment
- `Procfile.dev` - Backup development configuration

## 🚀 How to Deploy on Railway

### Step 1: Sign Up
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended)

### Step 2: Deploy Your App
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose this repository
4. Railway will auto-detect Python and deploy!

### Step 3: Configure (if needed)
- Railway should automatically detect the `Procfile`
- If not, set start command to: `cd backend && gunicorn --bind 0.0.0.0:$PORT app:app`

### Step 4: Get Your URL
- Railway will provide a public URL like: `https://your-app-name.up.railway.app`
- Your app will be live and ready to use!

## 🔧 Configuration Options

### Environment Variables (Optional)
You can set these in Railway's dashboard:
- `DEBUG=false` (for production)
- `PORT` (automatically set by Railway)

### Custom Domain (Optional)
- Go to your Railway project settings
- Add your custom domain
- Railway provides free HTTPS

## 🛠️ Troubleshooting

### If deployment fails:
1. Check Railway logs in the dashboard
2. Verify all files are committed to your repository
3. Try the backup Procfile: `mv Procfile.dev Procfile`

### Common issues:
- **Build fails**: Check `requirements.txt` format
- **App won't start**: Check the logs for Python errors
- **404 errors**: Verify the static files are in the right location

## 🎉 Success!

Once deployed, your Canvas Course Extractor will be available worldwide at your Railway URL!

## 📱 Alternative: One-Click Deploy

You can also use this button for instant deployment:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

(You'll need to create a Railway template first)
