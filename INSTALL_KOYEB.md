# Deploy PSU Job Alert System on Koyeb (Free Tier)

Complete step-by-step guide to deploy the PSU Job Alert Flask application on Koyeb's free tier — no credit card required for signup (card needed only for verification).

---

## Prerequisites

- A **GitHub account** (free — sign up at https://github.com if you don't have one)
- Your Gmail **App Password** ready (you already have this from earlier)
- Your project code ready on your local machine

---

## Step 1: Create a Koyeb Account (Free)

1. Open your browser and go to **https://app.koyeb.com**
2. Click **"Sign up"**
3. Choose **"Sign up with GitHub"** (recommended — connects Koyeb to your GitHub repos automatically)
4. Authorize Koyeb when GitHub asks for permission
5. Complete your profile (name, etc.)
6. **Credit card for verification (optional, only if prompted):**
   - Koyeb may ask for a credit card to verify your account
   - This is only for verification — you will **NOT be charged** as long as you use the `free` instance type
   - No charges occur unless you manually upgrade to a paid instance or enable paid features
7. Once signed in, you'll land on the **Koyeb Control Panel** dashboard

---

## Step 2: Create GitHub Repository

1. Open browser → go to **https://github.com**
2. Click **"+"** icon (top-right) → **"New repository"**
3. **Repository name:** `job-alert-psu`
4. **Description (optional):** `PSU Job Notification Alert System for CSE/IT Non-GATE graduates`
5. **Visibility:** Select **Public**
6. **DO NOT** check "Add a README", ".gitignore", or "License"
7. Click **"Create repository"**
8. Keep this page open — you'll use the commands from it next.

---

## Step 3: Push Your Local Code to GitHub

Open a **fresh PowerShell** window and run these commands **one by one**:

### 3a. Navigate to project folder
```powershell
cd "C:\Personal\Home business\Blogging\Job notification alert software\job-alert-system"
```

### 3b. Initialize git and switch to `main` branch
```powershell
git init
git branch -M main
```

### 3c. Stage all files and commit
```powershell
git add .
git commit -m "Initial commit: PSU Job Alert System"
```

### 3d. Connect to your GitHub repo
Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username (e.g. `swapansanjayk`):

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/job-alert-psu.git
```

### 3e. Push code to GitHub
```powershell
git push -u origin main
```

### 3f. Verify
Refresh your GitHub repo page at `https://github.com/YOUR_GITHUB_USERNAME/job-alert-psu` — you should see all project files listed.

---

## Step 4: Deploy to Koyeb from GitHub

### 4a. Connect Koyeb to your repository

1. Go to **https://app.koyeb.com** → click **"Create Service"**
2. Select **"Web Service"**
3. Under **"Deploy from"**, select **"GitHub"**
4. Authorize Koyeb to access your GitHub repos (if prompted)
5. In the repository dropdown, find and select: **`YOUR_GITHUB_USERNAME/job-alert-psu`**
6. **Branch:** `main`

### 4b. Configure build settings

1. **Builder:** Select **"Buildpack"** (NOT Dockerfile)
2. **Build command:** Leave blank — Koyeb auto-detects `requirements.txt`
3. **Run command:** Click **"Override"** and enter:

   ```
   gunicorn --bind :$PORT --workers 1 --threads 2 --timeout 120 wsgi:application
   ```

### 4c. Configure instance

1. **Instance type:** Select **"Nano (Free)"** — 0.1 vCPU, 512 MB RAM
2. **Region:** Choose the one closest to you (Frankfurt or Washington DC for free)
3. Leave all other settings at default

### 4d. Set environment variables (RECOMMENDED)

Click **"Add Environment Variable"** and enter your SMTP credentials so they persist across redeploys:

| Variable | Value |
|----------|-------|
| `SMTP_EMAIL` | `swapansanjayk@gmail.com` |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `swapansanjayk@gmail.com` |
| `SMTP_PASSWORD` | *(your 16-character Gmail App Password)* |
| `CHECK_INTERVAL` | `120` |

> **Why env vars?** Koyeb's filesystem is **ephemeral** — any files you save (config.json, SQLite DB) are lost on every redeploy. Env vars survive redeploys.

### 4e. Deploy

1. Click **"Deploy"** at the bottom
2. Wait 2–5 minutes for the build and deploy to complete
3. You'll see "Healthy" status when ready
4. Your app URL will be: `https://job-alert-psu-YOUR_ORG.koyeb.app`

---

## Step 5: First-Time Setup

1. Open your app URL in the browser: `https://job-alert-psu-YOUR_ORG.koyeb.app`
2. Go to **Setup** page
3. Verify your email and App Password are already filled (from env vars)
4. Click **"Scan Now"** to trigger the first job scan
5. You'll see seed jobs populate the dashboard
6. If email is configured correctly, you'll get a success flash message

> **Note:** The first deploy has NO seed jobs in the DB (SQLite starts empty). Click "Scan Now" to scan all 102 PSU career pages. The scraper will find real jobs or fall back to seed data from `seed_data.py`.

---

## Step 6: Verify Email Notifications

1. After scanning, check your Gmail inbox (and spam folder)
2. You should receive an HTML email with job listings
3. Go to the **History** page to see notification delivery status
4. If email fails, check the error message on the dashboard and verify your App Password

---

## Important: Koyeb Free Tier Limitations

| Resource | Free Limit | Notes |
|----------|-----------|-------|
| vCPU | 0.1 vCPU | Enough for light scraping |
| RAM | 512 MB | Sufficient for Flask + scheduler |
| Storage | 2 GB SSD | Shared across app + DB |
| **Data Persistence** | **Ephemeral** | SQLite DB + config.json lost on redeploy |
| Outbound SMTP | Allowed | Port 587 works |
| Idle timeout | None | Service runs 24/7 |

### Why env vars matter

On Koyeb free tier, every redeploy wipes the filesystem. This means:
- **`job_alert.db`** (SQLite) — all scanned jobs and history are lost
- **`config.json`** — SMTP settings are lost

**Solution:** Set the environment variables listed in Step 4d. The app will read SMTP settings from env vars automatically. For the database, simply click **"Scan Now"** after each redeploy — the scraper will refill the DB.

---

## Triggering a Manual Redeploy

After pushing code changes to GitHub:

1. Go to **https://app.koyeb.com**
2. Click on your service
3. Click **"Redeploy"** button (top-right)
4. Wait for build + deploy to finish (2–5 minutes)

Or push a commit to GitHub — Koyeb auto-deploys the `main` branch by default.

---

## Viewing Logs

1. In your Koyeb service dashboard, click **"Logs"** tab
2. Filter by **"Build"** (to see deployment logs) or **"Runtime"** (to see app output)
3. Look for lines like:
   - `INFO scheduler: Auto-scan triggered at ...`
   - `INFO main: Scan complete. 31 total, 0 new jobs found.`
   - `INFO notifier: Email notification sent to ...`

---

## Troubleshooting

### App shows "502 Bad Gateway"
- Wait 10 seconds after deploy for the scheduler to initialize
- Check Runtime logs for startup errors
- Ensure `wsgi:application` is correct in the Run command

### Email not sending
- Verify you're using a **Gmail App Password** (not your regular password)
- Check that App Password has NO spaces when pasted
- Verify env vars are set correctly in Koyeb dashboard
- Check Runtime logs for SMTP errors

### Scraper returns no jobs
- Click **"Scan Now"** manually from the dashboard (the scheduler may not have run yet)
- Check Runtime logs for scraper errors
- Some PSU career pages may be blocked — the seed data fallback handles this

### Config not saved after redeploy
- This is expected — Koyeb free tier has ephemeral storage
- Use **environment variables** (Step 4d) instead of the Setup form
- The app reads `SMTP_EMAIL`, `SMTP_PASSWORD`, etc. from env vars automatically

---

## Project Structure (for reference)

```
job-alert-system/
├── main.py              # Flask app entry point
├── wsgi.py              # WSGI wrapper for gunicorn/Koyeb
├── Procfile             # Koyeb start command
├── requirements.txt     # Python dependencies
├── .gitignore           # Files excluded from git
├── config.py            # Config file + env var loader
├── database.py          # SQLite database layer
├── psu_data.py          # 115 PSU definitions
├── filter.py            # CSE/IT + Non-GATE filter
├── scraper.py           # Multi-threaded PSU scraper
├── seed_data.py         # 31 seed job entries
├── notifier.py          # Email notification (SMTP)
├── scheduler.py         # APScheduler wrapper
└── templates/           # Bootstrap 5 HTML files
    ├── base.html
    ├── dashboard.html
    ├── setup.html
    └── history.html
```

---

## Next Steps (Optional)

- **Custom domain:** Koyeb free tier supports 10 custom domains with auto HTTPS
- **Managed PostgreSQL:** Upgrade to use Koyeb's managed Postgres (first 5 hours free) instead of SQLite for persistent data
- **Custom scraper logic:** Edit `psu_data.py` or `scraper.py` to add more PSUs or change scraping patterns
- **Reduce scan interval:** Set `CHECK_INTERVAL` env var to `120` (2 hours) for production
