# Deploy PSU Job Alert System on Railway (Free Tier)

Complete step-by-step guide to deploy on Railway's free tier.

## Important: Railway Blocks SMTP

Railway's free/Hobby plans **block outbound SMTP ports** (25, 465, 587). You cannot send email directly via Gmail/Outlook SMTP.

**Solution:** The app supports **Mailjet API** which sends email over HTTPS (port 443) — works perfectly on Railway.

---

## Prerequisites

- A **GitHub account** (free — https://github.com)
- Your project already on GitHub as `swapansanjayk-personal/job-alert-psu`
- A **Mailjet account** (free — 200 emails/day, https://mailjet.com)

---

## Step 1: Get Mailjet API Credentials

1. Go to **https://mailjet.com** and sign in
2. Go to **Account Settings** → **API Keys** (or **REST API**)
3. Copy the **API Key** and **Secret Key** — you'll need both for Railway

---

## Step 3: Create a Railway Account

1. Go to **https://railway.com**
2. Click **"Start a New Project"** or **"Sign in with GitHub"**
3. Authorize Railway to access your GitHub account
4. Complete any onboarding steps

---

## Step 4: Deploy from GitHub

### 4a. Create new project

1. On the Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. If prompted, install the Railway GitHub app and grant access to `job-alert-psu`
4. Select your repo: **`swapansanjayk-personal/job-alert-psu`**

### 4b. Wait for initial deploy

Railway will automatically:
- Detect Python via Railpack
- Install `requirements.txt`
- Build the app (takes 1-2 minutes)

### 4c. Set the Start Command

1. Click on your service (the box with your repo name) to open its dashboard
2. Go to the **Settings** tab
3. Scroll to **"Deploy"** section → **"Start Command"**
4. Enter:

   ```
   gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 wsgi:application
   ```

5. Click **"Update"**

### 4d. Set environment variables

1. Go to the **Variables** tab
2. Click **"New Variable"** and add these one by one:

| Variable | Value |
|----------|-------|
| `EMAIL_PROVIDER` | `mailjet` |
| `MAILJET_API_KEY` | *(your Mailjet API Key)* |
| `MAILJET_SECRET_KEY` | *(your Mailjet Secret Key)* |
| `SMTP_EMAIL` | `swapansanjayk@gmail.com` |
| `CHECK_INTERVAL` | `120` |

### 4e. Generate a public URL

1. Go to the **Settings** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Copy the URL (e.g. `https://job-alert-psu.up.railway.app`)

### 4f. Redeploy

1. Click **"Deploy"** button (top-right) or **"Redeploy"** to apply the start command and env vars
2. Wait for the build to finish (2-3 minutes)

---

## Step 5: First-Time Setup

1. Open your app URL: `https://job-alert-psu.up.railway.app`
2. Wait **5-10 seconds** for the scheduler to start
3. Go to the **Setup** page
4. You'll see "Mailjet API" pre-selected (from env vars)
5. Verify the Mailjet API Key and Secret Key are present
6. Click **"Save Configuration & Start Monitoring"**
7. Go to **Dashboard** and click **"Scan Now"**

---

## Step 6: Verify Email Delivery

1. Check your Gmail inbox (and **Spam** folder)
2. You should receive: `📢 Job Alert: X New Non-GATE PSU Opportunity/ies Found`
3. Check **History** page to see notification status
4. If no email:
   - Go to Railway dashboard → your service → **Logs**
   - Look for `notifier: SendGrid email sent to ...` or `SendGrid API error ...`

---

## Important: Railway Free Tier Limitations

| Resource | Free Limit | Notes |
|----------|-----------|-------|
| Credit | **$5 free trial** | No credit card required to start |
| RAM | 512 MB (shared) | Enough for this app |
| CPU | Shared | Sufficient |
| Disk | Ephemeral | Wiped on redeploy |
| **SMTP Ports** | **BLOCKED** | Ports 25, 465, 587 blocked on free/Hobby |
| HTTPS (port 443) | Allowed | SendGrid API works here |
| Idle | Never spins down | Runs 24/7 on free tier |
| Bandwidth | Included | Within $5 credit |

> **Free trial credit:** Railway gives $5 free when you sign up. This app costs roughly **$0.50-1/month** to run, so the free credit lasts **5-10 months**. You never need to enter a credit card for the free tier.

---

## Viewing Logs

1. In Railway dashboard, click on your service
2. Click the **"Logs"** tab (bottom panel)
3. Look for:
   - `INFO scheduler: Auto-scan triggered at ...`
   - `INFO scraper: Scraped 102 PSU career pages`
   - `INFO notifier: SendGrid email sent to ...`
   - `INFO main: Scan complete. 31 total, 0 new jobs found.`

---

## Triggering a Redeploy

After pushing code changes to GitHub:

1. In Railway dashboard, click **"Redeploy"** button
2. Wait for build to finish

Or push to `main` branch — Railway auto-deploys by default.

---

## Troubleshooting

### App shows "Application failed to respond"
- Check **Logs** for startup errors
- Ensure Start Command is set correctly
- Wait 10 seconds after deploy

### Email not sending
- Verify `EMAIL_PROVIDER=mailjet` env var is set
- Verify `MAILJET_API_KEY` and `MAILJET_SECRET_KEY` are correct
- Check Railway **Logs** for Mailjet API errors

### Mailjet returns 401 Unauthorized
- API Key or Secret Key may be wrong — copy them again from Mailjet account settings

### Job scraper finds no jobs
- Click **"Scan Now"** manually
- Check logs for scraper errors
- Seed data fallback activates if scraping fails

---

## Project Structure

```
job-alert-system/
├── main.py              # Flask app
├── wsgi.py              # WSGI wrapper for gunicorn
├── Procfile             # Start command reference
├── requirements.txt     # Dependencies
├── config.py            # Config + env var loader
├── database.py          # SQLite database
├── psu_data.py          # 115 PSU definitions
├── filter.py            # CSE/IT + Non-GATE filter
├── scraper.py           # Multi-threaded scraper
├── seed_data.py         # 31 seed job entries
├── notifier.py          # Email via SMTP or SendGrid API
├── scheduler.py         # APScheduler
└── templates/           # Bootstrap 5 HTML files
```
