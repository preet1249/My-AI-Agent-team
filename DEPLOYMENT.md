# Deployment Guide

This guide will help you deploy the AI Agent Team to production.

## Architecture

- **Frontend (Web)**: Deploy to Vercel
- **Backend (API)**: Deploy to Render
- **Mobile App**: Build with EAS and distribute via App Stores
- **Database**: Supabase (managed)
- **Queue**: Upstash Redis (managed)

## Prerequisites

1. GitHub account
2. Vercel account
3. Render account
4. Supabase project
5. Upstash Redis instance
6. OpenRouter API key

## Step 1: Set up Supabase

1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Run the database migrations (from `Prompt.md`)
4. Get your:
   - Supabase URL
   - Anon/Public key
   - Service role key

## Step 2: Set up Upstash Redis

1. Go to [Upstash](https://upstash.com)
2. Create a new Redis database
3. Get your Redis URL

## Step 3: Deploy Backend to Render

1. Push code to GitHub
2. Go to [Render](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Root Directory**: `apps/backend`
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11

6. Add environment variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_service_role_key
   REDIS_URL=your_redis_url
   OPENROUTER_API_KEY=your_openrouter_key
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   WEBHOOK_SECRET=generate_random_string
   INTERNAL_SIGNING_KEY=generate_random_string
   ```

7. Click "Create Web Service"
8. Copy your backend URL (e.g., `https://your-app.onrender.com`)

## Step 4: Deploy Frontend to Vercel

1. Go to [Vercel](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web`
   - **Build Command**: `cd ../.. && pnpm install && cd apps/web && pnpm build`
   - **Install Command**: `pnpm install`

5. Add environment variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
   ```

6. Click "Deploy"
7. Your frontend will be live at `https://your-app.vercel.app`

## Step 5: Build Mobile App

### For Android (APK):

```bash
cd apps/mobile

# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure EAS
eas build:configure

# Build APK
eas build --platform android --profile preview

# Download and install on device
```

### For iOS:

```bash
# Build for iOS
eas build --platform ios --profile preview
```

## Step 6: Configure Webhooks

Update your backend URL in:
- Gmail API webhook settings
- Supabase webhooks (if using)
- Any external services

## Post-Deployment Checklist

- [ ] Frontend is accessible
- [ ] Backend health check works (`/health`)
- [ ] Database connection is working
- [ ] Redis queue is connected
- [ ] Agent endpoints respond
- [ ] Mobile app can connect to backend
- [ ] Webhooks are configured
- [ ] Environment variables are set
- [ ] SSL/HTTPS is working

## Monitoring

1. **Render**: Check logs in Render dashboard
2. **Vercel**: Check deployment logs and analytics
3. **Supabase**: Monitor database usage
4. **Upstash**: Monitor Redis queue

## Troubleshooting

### Backend not starting

- Check Python version (must be 3.11)
- Verify all environment variables are set
- Check Render logs for errors

### Frontend build fails

- Ensure all dependencies are in `package.json`
- Check Node version compatibility
- Verify environment variables

### Mobile app can't connect

- Check API_URL is correct
- Verify CORS settings in backend
- Test backend endpoint directly

## Scaling

### Free Tier Limits

- **Render Free**: 750 hours/month, sleeps after 15 min inactivity
- **Vercel Free**: 100 GB bandwidth, unlimited deployments
- **Supabase Free**: 500 MB database, 1 GB file storage
- **Upstash Free**: 10,000 commands/day

### Upgrading

When you hit limits:
1. Upgrade Render to paid plan ($7/mo)
2. Upgrade Vercel Pro ($20/mo)
3. Upgrade Supabase Pro ($25/mo)
4. Upgrade Upstash as needed

## Cost Estimate

**Minimum viable (free tier)**: $0/month + LLM API costs

**Production ready**:
- Render: $7-25/month
- Vercel: $20/month
- Supabase: $25/month
- Upstash: $10-20/month
- **Total**: ~$60-90/month + LLM API costs

## Support

For deployment issues:
- Check Render docs: https://render.com/docs
- Check Vercel docs: https://vercel.com/docs
- Check this repo's Issues tab
