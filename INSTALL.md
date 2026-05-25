# PSU Job Alert System — Complete Installation Guide

## Part A: Local Installation (Windows)

### Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download **Python 3.10 or higher** (Windows installer)
3. **IMPORTANT:** During installation, check **"Add Python to PATH"**
4. Click Install

Verify installation:
```powershell
python --version
```

### Step 2: Download the Project

**Option A: If I provided files in a folder**
- The project is already at `C:\Personal\Home business\Blogging\Job notification alert software\job-alert-system`
- Copy the entire `job-alert-system` folder to any location you prefer

**Option B: Download as ZIP**
If you received a ZIP file, extract it to your desired location, e.g.:
```powershell
# Extract to C:\psu-job-alert
```

### Step 3: Open Terminal in Project Folder

```powershell
cd C:\path\to\job-alert-system
```

### Step 4: Create Virtual Environment (Recommended)

```powershell
python -m venv venv
```

### Step 5: Activate Virtual Environment

```powershell
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of the prompt.

### Step 6: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 7: Run the Application

```powershell
python main.py
```

You will see output like:
```
* Serving Flask app 'main'
* Running on http://127.0.0.1:5000
```

### Step 8: Open the Dashboard

1. Open your web browser
2. Go to **http://localhost:5000**
3. You will see the Dashboard with seed jobs pre-loaded

### Step 9: Configure Email (First-Time Setup)

1. Click **"Setup"** in the top menu (or go to http://localhost:5000/setup)
2. Fill in:
   - **Your Email Address** — where you want job alerts delivered
   - **SMTP Server** — `smtp.gmail.com`
   - **SMTP Port** — `587`
   - **SMTP Username** — your full Gmail address
   - **SMTP Password** — your Gmail **App Password** (NOT your regular password)
   - **Scan Interval** — `120` (minutes)
3. Click **"Save Configuration"**

### Step 10: Get Gmail App Password (Critical)

You CANNOT use your regular Gmail password. You must create an App Password:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Search for **"App Passwords"** in Google Account settings
4. Select:
   - App: **Mail**
   - Device: **Other**
   - Name it: **"PSU Job Alert"**
5. Click **Generate**
6. Copy the **16-character password** (looks like `abcd efgh ijkl mnop`)
7. Paste it in the **SMTP Password** field in Setup

### Step 11: Run Your First Scan

1. Go back to Dashboard (http://localhost:5000)
2. Click the **"Scan Now"** button
3. The system will:
   - Scrape PSU career pages
   - Fall back to seed data if scraping fails
   - Filter for CSE/IT, Non-GATE, 2023+ batch jobs
   - Send an email alert to your configured email
   - Log the notification in History

### Step 12: Keep It Running

**To keep scanning 24/7, keep the terminal/PowerShell window open.**

For long-term running, you can:
- Keep your PC on and the terminal open
- Or use Windows Task Scheduler to start it automatically on boot

---

## Part B: Hostinger Deployment (with Custom Domain)

> **Requirement:** Hostinger **Business Shared Hosting** or **VPS** plan.
> The free "Single Shared Hosting" plan does NOT support Python apps.

### Method 1: Hostinger Business/Cloud Shared Hosting

#### Step 1: Purchase Hostinger Business Plan

1. Go to https://www.hostinger.com
2. Choose **Business Shared Hosting** (or Cloud Startup)
3. Complete purchase and **claim your free domain** during checkout
4. Or connect your existing custom domain

#### Step 2: Access hPanel

1. Log into https://hpanel.hostinger.com
2. Find your hosting plan and click **Manage**

#### Step 3: Set Up Your Domain

If you got a free domain with Hostinger:
1. In hPanel, go to **Domains**
2. Your new domain should appear there
3. Point it to your hosting by setting nameservers (auto-done by Hostinger)

If you have an existing custom domain:
1. In hPanel, go to **Domains** → **Add Domain**
2. Enter your domain name
3. Update your domain's nameservers to Hostinger's (provided in hPanel)

#### Step 4: Upload Project Files

**Using hPanel File Manager:**
1. In hPanel, go to **Files** → **File Manager**
2. Navigate to the root of your domain (usually `public_html` or a subfolder)
3. Create a folder named `psu-alert` (or any name you prefer)
4. Upload all files from the `job-alert-system` folder:
   - `main.py`, `config.py`, `database.py`, `scraper.py`, `seed_data.py`
   - `filter.py`, `notifier.py`, `scheduler.py`, `requirements.txt`
   - `templates/` folder (with all 4 HTML files)

**Using FTP (alternative):**
1. In hPanel, go to **FTP** → Create FTP account
2. Use an FTP client like **FileZilla**:
   - Host: your domain or server IP
   - Username: FTP username
   - Password: FTP password
   - Port: 21
3. Upload all files to `public_html/psu-alert/`

#### Step 5: Set Up Python App in hPanel

1. In hPanel, go to **Advanced** → **Python**
2. Click **"Create Python App"**
3. Fill in the details:
   - **Python version:** 3.10 or 3.11
   - **App directory:** Select the folder you created (e.g., `public_html/psu-alert`)
   - **Entry point:** `main.py`
   - **Domain:** Select your custom domain
   - **Subdomain:** Leave blank or enter `psu-alert` (your app will be at `psu-alert.yourdomain.com`)
   - **App name:** `psu-job-alert`
4. Hpanel will show you the **App path** (something like `/home/u123456789/domains/yourdomain.com/public_html/psu-alert`)

#### Step 6: Install Dependencies via SSH

1. In hPanel, go to **Advanced** → **SSH Access**
2. Enable SSH and create an SSH key/password
3. Connect via SSH (use **PuTTY** on Windows or PowerShell):
   ```powershell
   ssh u123456789@yourdomain.com
   ```
4. Navigate to your app directory:
   ```bash
   cd domains/yourdomain.com/public_html/psu-alert
   ```
5. Install Python dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Step 7: Configure the Python App in hPanel

Back in hPanel → **Advanced** → **Python**:

1. Click **"Edit"** on your created Python app
2. Set environment variables (if needed):
   - `FLASK_DEBUG`: `0`
3. Click **"Update"**
4. Click **"Start"** or **"Restart"** to launch the app

#### Step 8: Access Your App

After a minute, your app will be live at:
- **https://psu-alert.yourdomain.com** (if you used a subdomain)
- **https://yourdomain.com/psu-alert** (if configured that way)

#### Step 9: Complete Setup in Browser

1. Visit your app URL
2. Go to the **Setup** page
3. Enter your email credentials (same as local setup instructions)
4. Click **"Save Configuration"**

#### Step 10: Set Up Cron Job for Auto-Scanning

1. In hPanel, go to **Advanced** → **Cron Jobs**
2. Click **"Add Cron Job"**
3. Configure:
   - **Interval:** `Every 2 hours` (or custom: `0 */2 * * *`)
   - **Command:** `cd /home/u123456789/domains/yourdomain.com/public_html/psu-alert && source venv/bin/activate && python -c "from main import create_app; app=create_app(); from scraper import run_scan; from database import init_db, insert_job, is_job_exists, get_unnotified_jobs, mark_job_notified; from notifier import send_email_notification; from config import load_config; init_db(); jobs=run_scan(); new=0; [insert_job(j) for j in jobs if not is_job_exists(j['job_id'])]; ujobs=get_unnotified_jobs(); [send_email_notification(ujobs) and [mark_job_notified(j['job_id'],'email',load_config().get('email_address',''),'success') for j in ujobs] if ujobs else None]"`
4. Click **Submit**

This cron job will scan PSU career pages, find new jobs, and email you automatically.

---

### Method 2: Hostinger VPS (Full Control)

#### Step 1: Purchase Hostinger VPS

1. Go to https://www.hostinger.com/vps
2. Choose a plan (KVM 1 or KVM 2 is sufficient)
3. Select OS: **Ubuntu 22.04 LTS**
4. Complete purchase

#### Step 2: Access Your VPS

**Via hPanel:**
1. Go to **VPS** → your VPS → **Manage**
2. You'll see your server IP and root password

**Connect via SSH:**
```powershell
ssh root@YOUR_SERVER_IP
```
Enter the root password from hPanel.

#### Step 3: Install Required Software

```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install python3 python3-pip python3-venv nginx git -y

# Install virtualenv
pip3 install virtualenv
```

#### Step 4: Create a User (Security)

```bash
adduser psuadmin
usermod -aG sudo psuadmin
su - psuadmin
```

#### Step 5: Upload Project Files

**On your local computer**, transfer files to VPS:
```powershell
scp -r C:\path\to\job-alert-system\* psuadmin@YOUR_SERVER_IP:/home/psuadmin/psu-alert/
```

**Or use Git:**
```bash
# On VPS
cd /home/psuadmin
git clone https://github.com/YOUR_USERNAME/psu-job-alert.git psu-alert
```

#### Step 6: Set Up Python Environment

```bash
cd /home/psuadmin/psu-alert
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### Step 7: Test the App

```bash
python main.py
```
Visit `http://YOUR_SERVER_IP:5000` — if it works, press Ctrl+C to stop.

#### Step 8: Configure Gunicorn as a Service

Create a systemd service:

```bash
sudo nano /etc/systemd/system/psu-alert.service
```

Paste:
```ini
[Unit]
Description=PSU Job Alert System
After=network.target

[Service]
User=psuadmin
WorkingDirectory=/home/psuadmin/psu-alert
ExecStart=/home/psuadmin/psu-alert/venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 "main:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Save (Ctrl+X, Y, Enter)

#### Step 9: Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl start psu-alert
sudo systemctl enable psu-alert
sudo systemctl status psu-alert
```

#### Step 10: Set Up Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/psu-alert
```

Paste:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save and enable:
```bash
sudo ln -s /etc/nginx/sites-available/psu-alert /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 11: Point Your Domain

1. In your domain registrar's DNS settings, add:
   - **A Record:** `@` → `YOUR_SERVER_IP`
   - **CNAME:** `www` → `yourdomain.com`

#### Step 12: Set Up SSL (HTTPS) with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts. SSL will auto-renew.

#### Step 13: Set Up Cron Job for Auto-Scanning

```bash
crontab -e
```

Add:
```
0 */2 * * * cd /home/psuadmin/psu-alert && source venv/bin/activate && python -c "from main import create_app; app=create_app(); from scraper import run_scan; from database import init_db, insert_job, is_job_exists, get_unnotified_jobs, mark_job_notified; from notifier import send_email_notification; from config import load_config; init_db(); jobs=run_scan(); new=0; [insert_job(j) for j in jobs if not is_job_exists(j['job_id'])]; ujobs=get_unnotified_jobs(); [send_email_notification(ujobs) and [mark_job_notified(j['job_id'],'email',load_config().get('email_address',''),'success') for j in ujobs] if ujobs else None]"
```

#### Step 14: Access Your App

Open `https://yourdomain.com` in your browser.

Complete the **Setup** page with your email/Gmail App Password.

Your app is now live and scanning every 2 hours automatically!

---

## Part C: Keeping the App Running 24/7

### Option 1: Local PC (24/7)

Keep your PC on and the Python terminal open. The in-app APScheduler handles auto-scans.

### Option 2: Hostinger Shared Hosting

The app runs on Hostinger's servers 24/7. Cron jobs trigger scans every 2 hours.

### Option 3: Hostinger VPS

The systemd service ensures the app restarts on crashes. Cron triggers scans.

---

## Troubleshooting

### "App not starting" on Hostinger Shared Hosting
- Check Python version: Go to hPanel → Advanced → Python
- Verify the entry point is `main.py`
- Check app logs: hPanel → Advanced → Python → View Logs

### "Email not sending"
- You MUST use a Gmail App Password, not your regular password
- Generate a new one at https://myaccount.google.com/apppasswords

### "No jobs found"
- The seed data provides 10 initial jobs
- Click "Scan Now" to scrape live PSU career pages
- Some PSU sites may block scraping — the seed data acts as fallback

### Need to restart the app?
- **Shared hosting:** hPanel → Advanced → Python → Restart
- **VPS:** `sudo systemctl restart psu-alert`
