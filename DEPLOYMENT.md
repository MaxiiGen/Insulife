# Deployment Guide: Insulife on Vercel + Render

This guide covers deploying the Insulife Diabetes Risk Classifier to production using Vercel (frontend) and Render (backend API).

## Architecture

- **Frontend**: Next.js React app on Vercel
- **Backend**: FastAPI Python server on Render
- **Model**: XGBoost classifier (`model.pkl`)

## Prerequisites

1. GitHub account with the Insulife repository pushed
2. Vercel account (free tier available)
3. Render account (free tier available)

## Part 1: Deploy Backend to Render

### Step 1: Prepare the Backend

1. Ensure `backend/main.py`, `backend/requirements.txt`, and `model.pkl` are in your repo
2. Push to GitHub if not already done

### Step 2: Create Render Service

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click **New +** → **Web Service**
3. Select your Insulife repository
4. Fill in the form:
   - **Name**: `insulife-api`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt` (in backend dir)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
5. Under **Environment**, add:
   - **KEY**: `MODEL_PATH`
   - **VALUE**: `model.pkl`
6. Click **Create Web Service**

### Step 3: Copy Backend URL

Once deployed, Render will give you a URL like `https://insulife-api.onrender.com`. Copy this for Step 3.

## Part 2: Deploy Frontend to Vercel

### Step 1: Configure Environment Variable

In your Vercel dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add:
   - **NAME**: `NEXT_PUBLIC_API_URL`
   - **VALUE**: `https://insulife-api.onrender.com` (replace with your Render URL)
   - **ENVIRONMENTS**: Production

### Step 2: Deploy

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **Add New** → **Project**
3. Select the Insulife repository
4. Vercel will auto-detect it's a Next.js project
5. Under **Environment Variables**, add the same `NEXT_PUBLIC_API_URL` variable
6. Click **Deploy**

### Step 3: Wait for Build

Vercel will automatically build and deploy. Once complete, you'll get a URL like `https://insulife.vercel.app`.

## Testing

1. Open your Vercel app URL
2. Enter patient data and click **Classify Risk**
3. You should see a prediction result

If you get errors:
- Check that the Render backend is running (visit `/health` endpoint)
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check browser console for network errors

## Updating the Model

To use a new trained `model.pkl`:

1. Replace `model.pkl` in the repository root
2. Push to GitHub
3. Render will auto-redeploy on push (if enabled)

## Troubleshooting

### "Failed to fetch" errors

- Ensure Render backend is running: visit `https://<your-render-url>/health`
- Check `NEXT_PUBLIC_API_URL` in Vercel environment variables

### Cold start delays

- First request to Render may take 30-60 seconds (free tier spins down after inactivity)
- Upgrade to paid tier for faster response times

### Model not found

- Ensure `model.pkl` is in the repository root and committed to Git
- Render will pull it during deployment
