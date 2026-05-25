# Deploy PSU Job Alert System on Render (Free Tier)

Complete step-by-step guide to deploy on Render's free tier — no credit card required.

## Important: Render Blocks SMTP

Render's free tier **blocks outbound SMTP ports** (25, 465, 587). You cannot send email directly via Gmail/Outlook SMTP.

**Solution:** We use **SendGrid API** which sends email over HTTPS (port 443) — works perfectly on Render.

---

## Prerequisites

- A **GitHub account** (free — https://github.com)
- A **SendGrid account** (free — 100 emails/day, https://sendgrid.com)
- Your project already pushed to GitHub as `YOUR_USERNAME/job-alert-psu`

---

## Step 1: Get a SendGrid API Key

1. Go to **https://sendgrid.com** and click **"Sign up"** (use same email `swapansanjayk@gmail.com`)
2. Select **"Free Plan"** (100 emails/day, never expires)
3. Verify your email address
4. Once logged in:
   - Go to **Settings → API Keys** (left sidebar)
   - Click **"Create API Key"**
   - Name: `PSU Job Alert`
   - Permission: **"Full Access"** (or "Restricted Access" with **Mail Send** checked)
   - Click **"Create & View"**
5. **Copy the API key** — it starts with `SG.` and looks like `SG.xxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxx`
6. Save it somewhere safe (you can't see it again)

---

## Step 2: Create a SendGrid Sender (Verify Sender Email)

1. In SendGrid, go to **Settings → Sender Authentication**
2. Click **"Verify a Single Sender"**
3. Enter:
   - **Email:** `swapansanjayk@gmail.com`
   - **Name:** `PSU Job Alert`
4. Check the verification email in your Gmail inbox and click the link
5. Wait a few minutes for the verification to process

---

## Step 3: Create a Render Account

1. Go to **https://render.com**
2. Click **"Sign up for free"**
3. Click **"Sign in with GitHub"** (this connects Render to your GitHub repos)
4. Authorize Render when GitHub asks for permission
5. You land on the **Render Dashboard**

---

## Step 4: Deploy Your Web Service

### 4a. Create new Web Service

1. On the Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub account if prompted (authorize Render)
3. Find and select your repo: **`YOUR_USERNAME/job-alert-psu`**

### 4b. Configure the service

| Setting | Value |
|---------|-------|
| **Name** | `psu-job-alert` (auto-filled) |
| **Region** | Choose the closest (e.g. `Frankfurt` or `Oregon`) |
| **Branch** | `main` |
| **Runtime** | `Python 3` (auto-detected) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 wsgi:application` |
| **Plan** | **Free** ($0/month) |

### 4c. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

| Variable | Value |
|----------|-------|
| `EMAIL_PROVIDER` | `sendgrid` |
| `SENDGRID_API_KEY` | *(your SG.xxxxxxxx key from Step 1)* |
| `SMTP_EMAIL` | `swapansanjayk@gmail.com` |
| `CHECK_INTERVAL` | `120` |

> **Why these env vars?** Render's filesystem is ephemeral — config.json is lost on redeploy. Env vars persist.

### 4d. Deploy

1. Scroll down and click **"Create Web Service"**
2. Wait 2–5 minutes for the build. Watch the **build logs** in real-time.
3. When done, you'll see: `"Your service is live 🎉"`
4. URL will be: `https://psu-job-alert.onrender.com` (or similar)

---

## Step 5: First-Time Setup on Render

1. Open your app URL: `https://psu-job-alert.onrender.com`
2. Wait **5-10 seconds** for the scheduler to initialize (cold start)
3. Go to the **Setup** page — you'll see `SendGrid API` pre-selected
4. Verify `SENDGRID_API_KEY` is populated (from env vars, field won't show the full key)
5. Click **"Save Configuration & Start Monitoring"**
6. Go to **Dashboard** and click **"Scan Now"**

---

## Step 6: Verify Email Delivery

1. After scan completes, check your Gmail inbox (and **Spam** folder)
2. You should receive an HTML email titled: `📢 Job Alert: X New Non-GATE PSU Opportunity/ies Found`
3. Check **History** page to see notification status
4. If no email arrives:
   - Go to Render Dashboard → your service → **Logs** → **Runtime**
   - Look for lines like `notifier: SendGrid email sent to ...` or `SendGrid API error ...`

---

## Important: Render Free Tier Limitations

| Resource | Free Limit | Notes |
|----------|-----------|-------|
| vCPU | 0.1 CPU | Enough for this app |
| RAM | 512 MB | Sufficient |
| Disk | Ephemeral | Wiped on every deploy |
| **SMTP Ports** | **BLOCKED** | Ports 25, 465, 587 blocked |
| HTTPS (port 443) | Allowed | SendGrid works here |
| Idle timeout | Spins down after **15 minutes** of inactivity | Cold start takes 30-60 seconds |
| Bandwidth | 100 GB/month | More than enough |
| Build minutes | 500 min/month | Plenty for this project |
| **Scheduler** | **Runs only when app is awake** | If app spins down, scheduler stops |

> **Critical:** Render free web services spin down after 15 minutes of inactivity. When you visit the URL, it wakes up (30-60 second cold start). The scheduler runs only while the app is awake. For 24/7 operation, upgrade to a paid plan ($7/month) or manually visit the URL periodically to keep it alive.

---

## Triggering a Manual Redeploy

After pushing code changes to GitHub:

1. Go to **https://dashboard.render.com**
2. Click on your web service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**
4. Wait for build (2-3 minutes)

Render also auto-deploys when you push to the `main` branch.

---

## Viewing Logs

1. In Render dashboard, click on your web service
2. Click **"Logs"** tab
3. Two types:
   - **Build logs** — shows pip install and build process
   - **Runtime logs** — shows your app output (scheduler runs, email sends, errors)

Look for:
- `INFO scheduler: Auto-scan triggered at ...`
- `INFO scraper: Scraped 102 PSU career pages`
- `INFO notifier: SendGrid email sent to ...`
- `INFO main: Scan complete. 31 total, 0 new jobs found.`

---

## Troubleshooting

### App shows "502 Bad Gateway"
- Wait 30-60 seconds — cold start is happening
- Check Runtime logs for startup errors
- Ensure the Start Command in Render settings matches exactly

### Email not sending on Render
- Verify `EMAIL_PROVIDER=sendgrid` env var is set
- Verify `SENDGRID_API_KEY` env var has the correct key (starts with `SG.`)
- Check SendGrid sender verification is complete (Step 2)
- Check Render Runtime logs for SendGrid API errors

### SendGrid returns 401 Unauthorized
- The API key might be wrong — regenerate it in SendGrid
- Make sure there are no extra spaces in the env var value

### App keeps spinning down
- This is normal for Render free tier — it sleeps after 15 minutes
- Visit the URL periodically to wake it up
- Or set up a free cron job service (e.g., cron-job.org) to ping your URL every 10 minutes

### Job scraper finds no jobs
- Click "Scan Now" manually from the Dashboard
- Check Runtime logs for scraper errors
- Seed data is injected only if the scraper finds nothing

---

## Keeping the App Alive (Free Workaround)

To prevent the free tier from sleeping, use a free uptime monitor:

1. Go to **https://cron-job.org** and create a free account
2. Create a new cron job:
   - **URL:** `https://psu-job-alert.onrender.com/api/health`
   - **Interval:** Every 10 minutes
3. This pings your app every 10 minutes, keeping it from spinning down

---

## Project Structure

```
job-alert-system/
├── main.py              # Flask app entry point
├── wsgi.py              # WSGI wrapper for gunicorn/Render
├── Procfile             # Start command (optional for Render)
├── requirements.txt     # Python dependencies
├── .gitignore           # Files excluded from git
├── config.py            # Config file + env var loader
├── database.py          # SQLite database layer
├── psu_data.py          # 115 PSU definitions
├── filter.py            # CSE/IT + Non-GATE filter
├── scraper.py           # Multi-threaded PSU scraper
├── seed_data.py         # 31 seed job entries
├── notifier.py          # Email via SMTP or SendGrid API
├── scheduler.py         # APScheduler wrapper
└── templates/           # Bootstrap 5 HTML files
    ├── base.html
    ├── dashboard.html
    ├── setup.html
    └── history.html
```
