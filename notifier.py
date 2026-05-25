import smtplib
import logging
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import load_config
import requests

logger = logging.getLogger(__name__)


def build_email_body(jobs):
    html = """
    <html>
    <head>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; padding: 20px; }
            .container { max-width: 650px; margin: 0 auto; background: white; border-radius: 16px;
                         overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
            .header { background: #0b3b5f; color: white; padding: 24px 30px; }
            .header h1 { margin: 0; font-size: 22px; }
            .header .badge { background: #ff8c42; color: #0b3b5f; border-radius: 20px;
                            padding: 4px 14px; font-size: 12px; font-weight: bold; display: inline-block; margin-top: 8px; }
            .body { padding: 24px 30px; }
            .job-card { background: #f8fafc; border-radius: 14px; padding: 18px; margin-bottom: 16px;
                       border-left: 4px solid #ff8c42; }
            .job-title { font-size: 17px; font-weight: 700; color: #0b3b5f; margin-bottom: 4px; }
            .org-name { font-size: 13px; font-weight: 600; color: #ff8c42; text-transform: uppercase; }
            .details { font-size: 13px; color: #4a627a; margin: 10px 0; }
            .detail { background: #eef2f5; border-radius: 12px; padding: 2px 10px; display: inline-block; margin: 2px 4px 2px 0; }
            .apply-link { display: inline-block; background: #0b3b5f; color: white; text-decoration: none;
                         padding: 8px 20px; border-radius: 24px; font-size: 13px; font-weight: 600; margin-top: 10px; }
            .footer { background: #eef2f5; padding: 16px 30px; font-size: 12px; color: #4a627a; text-align: center; }
            .non-gate-badge { background: #d9f0ec; color: #1e6f5c; border-radius: 12px; padding: 2px 10px;
                             font-size: 11px; font-weight: bold; display: inline-block; margin-top: 6px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>\U0001f4e2 New Non-GATE PSU Job Alerts</h1>
                <span class="badge">No GATE Required</span>
                <p style="opacity:0.9; font-size:14px; margin-top:8px;">
                    Computer Engineer Trainee opportunities for 2023+ batch graduates
                </p>
            </div>
            <div class="body">
                <p style="font-size:15px; color:#1e2a3a;">
                    Hello,<br><br>
                    Your job monitoring system has detected <strong>""" + str(len(jobs)) + """ new opportunity/opportunities</strong>
                    matching your profile (CSE/IT, Non-GATE, Public Sector).
                </p>
    """
    for job in jobs:
        html += f"""
                <div class="job-card">
                    <div class="org-name">{job.get('organization', '')}</div>
                    <div class="job-title">{job.get('title', '')}</div>
                    <div class="details">
                        <span class="detail">\U0001f4cd {job.get('location', 'N/A')}</span>
                        <span class="detail">\U0001f4c5 Deadline: {job.get('deadline', 'TBA')}</span>
                        <span class="detail">\U0001f393 {job.get('eligibility', 'N/A')}</span>
                    </div>
                    <div class="non-gate-badge">\u2705 No GATE Required</div>
                    <br>
                    <a class="apply-link" href="{job.get('apply_url', '#')}" target="_blank">
                        \U0001f517 View Official Notification
                    </a>
                </div>
        """
    html += f"""
                <p style="font-size:13px; color:#4a627a; margin-top:20px;">
                    \u2139\ufe0f This is an automated alert from your PSU Job Notification System.
                    Always verify details on the official website before applying.
                </p>
            </div>
            <div class="footer">
                Sent on {datetime.now().strftime('%d %B %Y at %I:%M %p')} |
                PSU Job Alert System
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_email_via_mailjet(api_key, secret_key, from_email, to_email, subject, html_body):
    url = "https://api.mailjet.com/v3.1/send"
    payload = {
        "Messages": [{
            "From": {"Email": from_email, "Name": "PSU Job Alert"},
            "To": [{"Email": to_email}],
            "Subject": subject,
            "HTMLPart": html_body,
        }]
    }
    resp = requests.post(url, auth=(api_key, secret_key), json=payload, timeout=30)
    if resp.status_code in (200, 201, 202):
        logger.info(f"Mailjet email sent to {to_email}")
        return True, ""
    body = resp.text[:500]
    logger.error(f"Mailjet API error {resp.status_code}: {body}")
    return False, f"Mailjet API error {resp.status_code}: {body}"


def send_email_notification(jobs, recipient_email=None):
    config = load_config()
    if recipient_email:
        to_email = recipient_email
    else:
        to_email = config.get("email_address", "")
    if not to_email:
        logger.error("No recipient email configured")
        return False, "No recipient email configured"

    provider = config.get("email_provider", "smtp")
    html_body = build_email_body(jobs)
    subject = f"\U0001f4e2 Job Alert: {len(jobs)} New Non-GATE PSU Opportunity/ies Found"

    if provider == "mailjet":
        api_key = config.get("mailjet_api_key", "")
        secret_key = config.get("mailjet_secret_key", "")
        if not api_key or not secret_key:
            return False, "Mailjet API credentials not configured"
        from_email = config.get("email_username") or config.get("email_address", "")
        return send_email_via_mailjet(api_key, secret_key, from_email, to_email, subject, html_body)

    # SMTP (default)
    smtp_server = config.get("email_smtp_server", "smtp.gmail.com")
    smtp_port = config.get("email_smtp_port", 587)
    username = config.get("email_username", "")
    password = config.get("email_password", "")
    if not username or not password:
        logger.error("SMTP credentials not configured")
        return False, "SMTP credentials not configured"
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = username
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        logger.info(f"Email notification sent to {to_email} with {len(jobs)} jobs")
        return True, ""
    except smtplib.SMTPAuthenticationError:
        msg = "SMTP Authentication failed. Gmail blocks regular passwords. Use a Gmail App Password (requires 2FA)."
        logger.error(msg)
        return False, msg
    except smtplib.SMTPException as e:
        msg = f"SMTP error: {e}"
        logger.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Failed to send email: {e}"
        logger.error(msg)
        return False, msg
