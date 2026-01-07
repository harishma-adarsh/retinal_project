---
description: Guide to deploying the Retinal Image Project to Render.com (Free Tier)
---

This guide will help you deploy your Django application to the web using Render.com, which offers a free tier for web services.

## Prerequisites
- A [GitHub](https://github.com/) account.
- A [Render](https://render.com/) account.
- Git installed on your computer.

## Step 1: Push Code to GitHub
1. Create a new repository on GitHub (e.g., `retinal-ai-project`).
2. Initialize and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   # Replace the URL below with your new repository URL
   git remote add origin https://github.com/YOUR_USERNAME/retinal-ai-project.git
   git push -u origin main
   ```

## Step 2: Configure Render
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **"New +"** and select **"Web Service"**.
3. Connect your GitHub account and select the repository you just created.
4. Render will auto-detect some settings, but ensure the following are correct:
   - **Name**: `retinal-ai` (or any name you like)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn retinal_project.wsgi`
5. Select the **Free** instance type.
6. Click **"Create Web Service"**.

## Step 3: Deployment
Render will now build your application. This might take a few minutes.
- Watch the logs in the Render dashboard.
- Once finished, you will see a green "Live" badge.
- Your URL will be something like `https://retinal-ai.onrender.com`.

## Troubleshooting
- If you see "DisallowedHost" errors, ensure `ALLOWED_HOSTS = ['*']` is set in `settings.py` (we handled this).
- If static files (CSS/Images) are missing, check the `collectstatic` command logs.

## Note on Database
This setup uses the default SQLite database. Warning: On Render's free tier, the SQLite database file is ephemeral (it resets every time you redeploy). For persistent data, you should add a Postgres database (also available on Render).
