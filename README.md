# PSU Job Notification Alert System

> Automated job alert system for Indian Public Sector (PSU) jobs targeting **Computer Engineer Trainee** positions.
> **Filters:** Non-GATE only | CSE/IT graduates | 2023+ batch | Email notifications

---

## Features

- **Scrapes 10+ PSU career pages** — BEL, HPCL, ECIL, ISRO, DRDO, SSC, RRB, BARC, NIELIT, HAL
- **Smart filtering** — Only Computer Science/IT, Non-GATE, fresher-friendly roles
- **Seed data fallback** — Pre-loaded jobs from verified PSU sources (from the companion HTML file)
- **Email alerts** — Beautiful HTML email notifications via SMTP (Gmail)
- **Web Dashboard** — Monitor jobs, trigger scans, view history
- **Auto-scheduler** — Scans every 2 hours (configurable)
- **Dedup** — Never notifies you about the same job twice
- **Free-tier ready** — Deploy on PythonAnywhere, Render, or local PC

---

## Quick Start (Local)

### Prerequisites
- Python 3.10 or higher
- Gmail account (for sending email alerts)

### 1. Install

```bash
# Navigate to the project folder
cd job-alert-system

# Create virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run

```bash
python main.py
```

The dashboard will be available at **http://localhost:5000**

### 3. Configure

1. Open http://localhost:5000/setup in your browser
2. Enter your email address where alerts should be sent
3. Enter your Gmail SMTP credentials (see App Password guide below)
4. Set scan interval (default: 120 minutes = 2 hours)
5. Click **Save Configuration**

The system will immediately start scanning every N minutes.

### 4. Scan Manually

On the Dashboard, click **"Scan Now"** to trigger an immediate scan. New jobs will be detected, stored in the database, and an email alert will be sent to your configured address.

---

## SMTP Configuration

The system uses SMTP to send email alerts. You can use any email provider:

| Provider | SMTP Server | Port | Notes |
|----------|------------|------|-------|
| Gmail | `smtp.gmail.com` | 587 | Enable "Less secure apps" or use App Password |
| Outlook/Hotmail | `smtp.office365.com` | 587 | Normal password works |
| Yahoo Mail | `smtp.mail.yahoo.com` | 587 | Normal password works |

**Default setup:** Enter your email address and password. If using the same email for login, leave SMTP Username blank (it defaults to your email).

---

## Deployment to PythonAnywhere (Free)

PythonAnywhere offers a free Flask hosting tier with 512MB storage and scheduled tasks.

### Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Sign up for a **Free Beginner** account

### Step 2: Upload Files

```bash
# Option A: Upload via Git
# In PythonAnywhere Bash console:
git clone https://github.com/YOUR_USERNAME/job-alert-system.git

# Option B: Upload via Files page
# 1. Click "Files" tab
# 2. Upload the job-alert-system folder contents
# 3. Or use "Upload a file" button for each file
```

### Step 3: Set Up Virtual Environment

In the PythonAnywhere Bash console:

```bash
cd job-alert-system
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure WSGI

1. Go to **Web** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Select **Manual Configuration** > **Python 3.10**
4. In the **WSGI configuration file** section, edit the file:

```python
# Replace the contents of /var/www/yourusername_pythonanywhere_com_wsgi.py
import sys
import os

path = '/home/yourusername/job-alert-system'
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_DEBUG'] = '0'

from main import create_app
application = create_app()
```

5. Replace `yourusername` with your actual PythonAnywhere username

### Step 5: Set Up Scheduled Tasks (Auto-Scan)

PythonAnywhere free plan supports scheduled tasks.

1. Go to **Tasks** tab
2. Add a new scheduled task:

```
Time: Every 2 hours (e.g., 00:00, 02:00, 04:00, ...)
Command:
cd /home/yourusername/job-alert-system && source venv/bin/activate && python -c "from main import create_app; from scraper import run_scan; from database import init_db, insert_job, is_job_exists, get_unnotified_jobs, mark_job_notified; from notifier import send_email_notification; from config import load_config, is_configured; init_db(); jobs=run_scan(); new=0; [None for j in jobs if (is_job_exists(j['job_id']) or (insert_job(j), setattr(__import__('builtins'),'x',1)))]; jobs2=get_unnotified_jobs(); [send_email_notification(jobs2) and [mark_job_notified(j['job_id'],'email',load_config().get('email_address',''),'success') for j in jobs2] if jobs2 else None]"
```

Or simpler — use `curl` to hit your app's scan endpoint:

```
Time: Every 2 hours
Command:
curl -X POST https://yourusername.pythonanywhere.com/api/scan
```

### Step 6: Reload & Visit

- Click **Reload** on the Web tab
- Visit `https://yourusername.pythonanywhere.com`
- Complete the Setup page with your email/SMTP credentials

---

## Deployment to Render (Free Alternative)

1. Create account at https://render.com
2. Click **New** > **Web Service**
3. Connect your Git repository
4. Configure:
   - **Name:** `psu-job-alert`
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app`
5. Add a **Cron Job** (free) to hit `/api/scan` every 2 hours:
   - **Schedule:** `0 */2 * * *`
   - **Command:** `curl -X POST https://psu-job-alert.onrender.com/api/scan`

---

## Using the Seed Data

The system comes with **10 pre-loaded job entries** extracted from the companion HTML file (from PSU career pages). These serve as:

- **Immediate demo data** — See results right after setup
- **Fallback data** — When live scraping fails, seed data ensures you never miss known openings

Jobs from seed data are labeled with \U0001f331 "Seed" on the dashboard.

---

## Adding WhatsApp Notifications (Future)

The codebase is ready for WhatsApp integration. The `config.py` has placeholder fields for Twilio:

```python
# In config.py — already structured for WhatsApp
"whatsapp_enabled": False,
"whatsapp_number": "",
"twilio_account_sid": "",
"twilio_auth_token": "",
"twilio_whatsapp_number": ""
```

To enable:
1. Create a Twilio account (https://twilio.com)
2. Verify a WhatsApp sender number
3. Fill in the Twilio credentials
4. A `send_whatsapp()` function can be added to `notifier.py`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web Dashboard |
| `/setup` | GET/POST | Configuration page |
| `/history` | GET | Notification history |
| `/scan` | POST | Trigger manual scan |
| `/api/jobs` | GET | JSON list of all jobs |
| `/api/stats` | GET | JSON statistics |
| `/api/scan` | POST | API-triggered scan |
| `/api/health` | GET | Health check |

---

## Project Structure

```
job-alert-system/
├── main.py              # Flask app, routes, scheduler init
├── config.py            # JSON config reader/writer
├── database.py          # SQLite database layer
├── scraper.py           # Web scraper for 10 PSU sites
├── seed_data.py         # 10 seed jobs from HTML file
├── filter.py            # CSE/IT + Non-GATE + batch filter
├── notifier.py          # SMTP email sender
├── scheduler.py         # APScheduler wrapper
├── requirements.txt     # Python dependencies
├── templates/           # Flask HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── setup.html
│   └── history.html
└── README.md            # This file
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Web Framework | Flask 3.x |
| Scraping | requests + BeautifulSoup4 |
| Database | SQLite |
| Scheduler | APScheduler |
| Email | smtplib (Gmail SMTP) |
| Frontend | Bootstrap 5 |
| Templates | Jinja2 |

---

## Troubleshooting

**Email not sending?**
- Make sure you used a Gmail **App Password**, not your regular password
- Check that 2-Step Verification is enabled on your Google Account
- Verify the SMTP server/port: `smtp.gmail.com:587` for TLS

**Scraping returns no results?**
- PSU websites may change their HTML structure — check manually
- The system falls back to seed data automatically
- Run a manual scan via the Dashboard button

**Scheduler not running?**
- On PythonAnywhere: use **Scheduled Tasks** (not the in-app scheduler)
- Locally: ensure the app stays running (don't close the terminal)
