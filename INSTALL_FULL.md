# PSU Job Alert System — Complete Installation Guide

## Overview

Two deployment options:
- **Option A: Local PC (Windows)** — Runs on your computer while it's on
- **Option B: Render (Free Cloud)** — Runs 24/7 on Render free tier with Mailjet API

---

# Option A: Local Installation (Windows)

## Prerequisites

- **Python 3.10+** installed ([python.org](https://www.python.org/downloads/))
  - During install, check **"Add Python to PATH"**
  - Verify: open PowerShell → `python --version`
- **Gmail account** with App Password (for sending email alerts)

## Step 1: Extract the Project

Extract `psu-job-alert-system-v1.0.zip` to a folder of your choice, e.g.:

```
C:\psu-job-alert
```

## Step 2: Open PowerShell in Project Folder

```powershell
cd C:\psu-job-alert
```

## Step 3: Create & Activate Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

You will see `(venv)` at the start of the prompt.

## Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 5: Generate Gmail App Password

You cannot use your regular Gmail password. Create an App Password:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Search for **"App Passwords"** in Google Account settings
4. Select: App = **Mail**, Device = **Other**, name it **"PSU Job Alert"**
5. Click **Generate**
6. Copy the **16-character password** (e.g. `abcd efgh ijkl mnop`)
7. **Save it temporarily** — you'll paste it in the Setup page

## Step 6: Run the Application

```powershell
python main.py
```

Output:
```
* Serving Flask app 'main'
* Running on http://127.0.0.1:5000
```

## Step 7: Open Dashboard & Configure

1. Open browser → **http://localhost:5000**
2. Click **Setup** (top menu)
3. Fill in:
   - **Your Email Address** — where you want job alerts delivered
   - **Email Provider** — select **SMTP (Gmail / Outlook / any email)**
   - **SMTP Server** — `smtp.gmail.com`
   - **SMTP Port** — `587`
   - **SMTP Username** — your full Gmail address
   - **SMTP Password** — paste the 16-character App Password from Step 5
   - **Scan Interval** — `120` (minutes) for production, `1` for testing
4. Click **"Save Configuration & Start Monitoring"**

## Step 8: Run Your First Scan

1. Go to **Dashboard**
2. Click **"Scan Now"**
3. The system will scrape PSU career pages, filter jobs, and email you
4. Check your Gmail inbox (and Spam folder)
5. Check the **History** page to see notification status

## Keeping It Running

- Keep the PowerShell window open and your PC on
- The scheduler runs automatically at the interval you configured
- Close the window to stop the app

---

# Option B: Deploy on Render (Free Cloud) + Mailjet API

Render free tier gives you a 24/7 web service with a public URL. **SMTP is blocked** on Render free tier, so we use **Mailjet API** (sends email over HTTPS).

## Step 1: Create Mailjet Account

1. Go to https://mailjet.com → Sign up (free, 200 emails/day)
2. Verify your email address
3. Go to **Account Settings** → **Sender Addresses**
4. Click **"Add a Sender"** → enter your Gmail address
5. Check your Gmail inbox → click the **verification link**
6. Wait for the sender to show a **green checkmark** (verified)
7. Go to **Account Settings** → **API Keys** (or **REST API**)
8. Copy the **API Key** and **Secret Key**

> **Important:** Emails will NOT be delivered until the sender address is verified in Mailjet!

## Step 2: Push Code to GitHub

Create a GitHub repository and push the project files:

```powershell
# In your project folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/psu-job-alert.git
git push -u origin main
```

## Step 3: Create Render Account

1. Go to https://render.com → Sign up (free, no credit card needed)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your `psu-job-alert` repository

## Step 4: Configure Web Service

| Setting | Value |
|---------|-------|
| **Name** | `psu-job-alert` |
| **Environment** | Python |
| **Region** | Choose the closest |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 wsgi:application` |
| **Plan** | Free |

## Step 5: Add Environment Variables

In the Render dashboard, go to **Environment** and add:

| Key | Value |
|-----|-------|
| `EMAIL_PROVIDER` | `mailjet` |
| `MAILJET_API_KEY` | *(your Mailjet API Key)* |
| `MAILJET_SECRET_KEY` | *(your Mailjet Secret Key)* |
| `SMTP_EMAIL` | *(your Gmail address)* |
| `CHECK_INTERVAL` | `120` |

## Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for the build to complete
3. Your app will be at: `https://psu-job-alert.onrender.com`

## Step 7: Complete Setup

1. Open `https://psu-job-alert.onrender.com/setup`
2. You'll see **Mailjet API** pre-selected (with keys from env vars)
3. Enter your email address in **"Your Email Address"**
4. Click **"Save Configuration & Start Monitoring"**

## Step 8: Trigger First Scan

1. Go to Dashboard → click **"Scan Now"**
2. Check your Gmail inbox (and Spam)
3. Check the History page

## Preventing Render Sleep (Free Tier)

Render free tier sleeps after 15 minutes of inactivity. Use **cron-job.org** (free) to ping your app every 10 minutes:

1. Go to https://cron-job.org → Sign up
2. Create a cron job:
   - **URL:** `https://psu-job-alert.onrender.com/api/health`
   - **Interval:** Every 10 minutes
   - Click **Create**
3. Your app will stay awake 24/7

---

# Troubleshooting

## "Email not sending" with SMTP (Local)
- You MUST use a **Gmail App Password**, not your regular password
- Generate at: https://myaccount.google.com/apppasswords
- Verify 2-Step Verification is enabled first

## "Email not sending" with Mailjet (Render)
- **Check Mailjet sender verification** — Mailjet dashboard → Account Settings → Sender Addresses → must show green checkmark
- Check Render logs for Mailjet API errors
- Verify `MAILJET_API_KEY` and `MAILJET_SECRET_KEY` env vars are correct

## "No jobs found"
- Click **"Scan Now"** manually
- Seed data (31 pre-loaded jobs) is used as fallback when scraping fails
- Some PSU websites may block scraping — this is expected

## "App not responding"
- Render free tier sleeps after 15 minutes — wait 30-60 seconds for cold start
- Set up **cron-job.org** to prevent sleep (see Option B, Step 8)

## Viewing Logs
- **Local:** Check the PowerShell terminal output
- **Render:** Dashboard → your service → **Logs** tab

---

# Project Files Reference

| File | Purpose |
|------|---------|
| `main.py` | Flask web app with all routes |
| `config.py` | Configuration loader (file + env vars) |
| `database.py` | SQLite database layer |
| `scraper.py` | Multi-threaded PSU career page scraper |
| `psu_data.py` | Database of all 115+ PSUs with career URLs |
| `filter.py` | Filters: CSE/IT, Non-GATE, fresher batch |
| `seed_data.py` | 31 pre-loaded job entries (fallback) |
| `notifier.py` | Email sender (SMTP or Mailjet API) |
| `scheduler.py` | Auto-scan scheduler (APScheduler) |
| `wsgi.py` | WSGI entry point for gunicorn |
| `Procfile` | Render start command |
| `requirements.txt` | Python dependencies |
| `templates/` | Bootstrap 5 HTML templates |
