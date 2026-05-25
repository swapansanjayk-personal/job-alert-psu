# PSU Job Alert System — Email Setup User Manual

This guide explains how to **change the email address** where job notifications are delivered.

---

## Quick Answer: Do I need a Gmail App Password?

| Situation | Need App Password? |
|-----------|-------------------|
| **I changed the recipient email** (where alerts go) | **No** — just type the new email address in the Setup page |
| **I changed the sender email** (Gmail used for SMTP sending) | **Yes** — each Gmail sender needs its own App Password |
| **I'm using Mailjet API** (Render cloud) | **No** — just verify the new sender in Mailjet dashboard |

---

## Part 1: Change the Recipient Email (Where Notifications Arrive)

This is the simplest change — you just update the email address on the Setup page.

### Step 1: Open the Setup Page

- **Local:** http://localhost:5000/setup
- **Render:** https://your-app.onrender.com/setup

### Step 2: Update the "Your Email Address" Field

In the **Email Notification Settings** section, change the **"Your Email Address"** field to the new email where you want alerts delivered.

### Step 3: Save

Click **"Save Configuration & Start Monitoring"**.

### Example

| Old | New |
|-----|-----|
| `swapansanjayk@gmail.com` | `newemail@gmail.com` |

The system will now send all future job alerts to the new address.

### What Happens to Old Notifications?

- The **History** page still shows past notifications sent to the old email
- All **future** scans will send emails to the new address

---

## Part 2: Change the Sender Email (For SMTP / Gmail)

If you're using **SMTP mode** (local setup) and want to send FROM a different Gmail account:

### Step 1: Generate App Password for the New Gmail

Each Gmail account needs its own App Password:

1. Sign into the **new** Gmail account
2. Go to https://myaccount.google.com/security
3. Enable **2-Step Verification** (if not already on)
4. Search for **"App Passwords"** in account settings
5. Select: App = **Mail**, Device = **Other**, name = **"PSU Job Alert"**
6. Click **Generate** → copy the 16-character password

### Step 2: Update SMTP Fields in Setup

1. Open **Setup** page
2. In the SMTP fields:
   - **SMTP Username:** Enter the **new** Gmail address
   - **SMTP Password:** Paste the **new** App Password
3. The **"Your Email Address"** field can be the same or different (sending and receiving can be different addresses)
4. Click **"Save Configuration & Start Monitoring"**

### Example

| Field | Old Value | New Value |
|-------|-----------|-----------|
| SMTP Username | `swapansanjayk@gmail.com` | `newaccount@gmail.com` |
| SMTP Password | `abcd efgh ijkl mnop` | (new App Password for newaccount) |
| Your Email Address | `swapansanjayk@gmail.com` | `swapansanjayk@gmail.com` or any address |

---

## Part 3: Change the Sender Email (For Mailjet API / Cloud)

If you're using **Mailjet API** (Render deployment) and want to send FROM a different email:

### Step 1: Add the New Sender in Mailjet

1. Log into https://mailjet.com
2. Go to **Account Settings** → **Sender Addresses**
3. Click **"Add a Sender"**
4. Enter the **new email address**
5. Mailjet sends a verification email — check that inbox and **click the verification link**

### Step 2: Wait for Verification

The sender must show a **green checkmark** in Mailjet. If it shows "Unverified" or has no checkmark, emails will still appear as "sent" in the system log but will NOT be delivered to your inbox.

### Step 3: Update the App

**If running locally:** Open Setup page → enter the new email in **"Your Email Address"** → Save.

**If running on Render:** You have two options:

#### Option A: Update via Setup Page (Recommended)
1. Open your app's **Setup** page
2. Change **"Your Email Address"** to the new email (the one verified in Mailjet)
3. Click **"Save Configuration & Start Monitoring"**

#### Option B: Update Environment Variable
1. In Render dashboard, go to **Environment**
2. Update `SMTP_EMAIL` to the new email address
3. Click **Deploy** / **Redeploy** to apply the change

### Example

| Step | Action |
|------|--------|
| 1 | Add `mynewemail@gmail.com` in Mailjet → Sender Addresses |
| 2 | Verify the email from Gmail inbox |
| 3 | Wait for green checkmark in Mailjet |
| 4 | Update `SMTP_EMAIL` env var to `mynewemail@gmail.com` |
| 5 | Redeploy on Render |

---

## Part 4: Switching Between SMTP and Mailjet

### From SMTP (Local) → Mailjet (Cloud)

1. Get Mailjet API Key + Secret Key (Mailjet → Account Settings → API Keys)
2. Add your sender email in Mailjet → **Sender Addresses** and verify it
3. Open app's **Setup** page
4. Change **Email Provider** dropdown to **Mailjet API**
5. Enter **Mailjet API Key** and **Mailjet Secret Key**
6. Make sure **"Your Email Address"** matches the verified sender in Mailjet
7. Click **"Save Configuration & Start Monitoring"**

### From Mailjet (Cloud) → SMTP (Local)

1. Open app's **Setup** page
2. Change **Email Provider** dropdown to **SMTP**
3. Fill in SMTP fields (server, port, username, App Password)
4. Click **"Save Configuration & Start Monitoring"**

---

## Part 5: Testing If Email Works

After changing the email address, always verify delivery:

### Step 1: Trigger a Manual Scan

- Go to **Dashboard**
- Click **"Scan Now"**

### Step 2: Check the Result

| Dashboard Message | Meaning |
|------------------|---------|
| "Email sent" (green) | System accepted the email |
| "EMAIL FAILED: ..." (red) | Something is wrong — check the error message |

### Step 3: Check Your Inbox

| Where to Check | What to Look For |
|----------------|-----------------|
| Gmail **Inbox** | Email from your sender with subject "Job Alert: X New Non-GATE PSU..." |
| Gmail **Spam** | Same — sometimes it lands here |
| Gmail **Promotions** tab | Can also land here |

### Step 4: Check History Page

Go to **History** → look for:
- ✅ **Sent** — Email was accepted by the mail server
- ❌ **Failed** — Error message explains why

### Step 5: Check Logs (if email still not received)

- **Local:** Look at the PowerShell terminal output
- **Render:** Dashboard → your service → **Logs** tab

Look for lines like:
```
notifier: Mailjet email sent to ...
notifier: Mailjet API error 401: ... (wrong API key)
notifier: SMTP Authentication error (wrong App Password)
```

---

## Common Email Issues

### "Mailjet API error 401"
- API Key or Secret Key is wrong
- Regenerate them in Mailjet → Account Settings → API Keys

### "Mailjet email sent" but NOT in Gmail inbox
- **Sender not verified in Mailjet** — this is the #1 cause
- Go to Mailjet → Account Settings → Sender Addresses
- Check if your sender email has a **green checkmark**
- If not, click "Verify" and check your email for the verification link

### "SMTP Authentication error"
- Gmail App Password is wrong or expired
- Generate a new App Password at https://myaccount.google.com/apppasswords
- Make sure 2-Step Verification is enabled

### "No recipient email configured"
- You haven't entered an email address in the Setup page
- Go to Setup → fill in **"Your Email Address"**

---

## Files That Store Email Configuration

| File | Purpose | Where |
|------|---------|-------|
| `config.json` | Local config (API keys, email, password) | In project folder (excluded from git via `.gitignore`) |
| Environment Variables | Cloud config for Render | Set in Render dashboard |

**On Render:** The `config.json` is **ephemeral** (wiped on redeploy). Always set email settings via **Environment Variables** in the dashboard:

| Env Var | Purpose |
|---------|---------|
| `EMAIL_PROVIDER` | `smtp` or `mailjet` |
| `MAILJET_API_KEY` | Mailjet API Key (required for Mailjet mode) |
| `MAILJET_SECRET_KEY` | Mailjet Secret Key (required for Mailjet mode) |
| `SMTP_EMAIL` | Recipient and sender email address |
| `SMTP_PASSWORD` | Gmail App Password (required for SMTP mode) |
| `CHECK_INTERVAL` | Scan interval in minutes (default: 120) |

---

## Summary: Email Change Checklist

| Task | Local (SMTP) | Cloud (Mailjet) |
|------|-------------|-----------------|
| Change recipient email | Update Setup page | Update Setup page or `SMTP_EMAIL` env var |
| Use different Gmail as sender | Generate App Password for new Gmail | Add & verify new sender in Mailjet |
| Switch email provider | Change dropdown in Setup page | Change dropdown in Setup page |
| Test delivery | Click "Scan Now" | Click "Scan Now" |
| Debug if not received | Check terminal logs | Check Render logs |
