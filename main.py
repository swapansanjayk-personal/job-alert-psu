import logging
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

from database import init_db, get_config, update_config, insert_job, \
    is_job_exists, get_unnotified_jobs, mark_job_notified, \
    get_all_jobs, get_notification_history, get_stats
from config import load_config, save_config, is_configured
from scheduler import start_scheduler, stop_scheduler, restart_scheduler, \
    set_scan_function, get_next_run_time
from scraper import run_scan
from notifier import send_email_notification

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()


def scan_and_notify():
    logger.info("Starting job scan...")
    all_jobs = run_scan()
    new_count = 0
    for job in all_jobs:
        if not is_job_exists(job["job_id"]):
            insert_job(job)
            new_count += 1
    logger.info(f"Scan complete. {len(all_jobs)} total, {new_count} new jobs found.")
    email_sent = False
    email_error = ""
    if new_count > 0:
        unnnotified = get_unnotified_jobs()
        logger.info(f"Sending notification for {len(unnnotified)} unnotified jobs...")
        if unnnotified:
            email_sent, email_error = send_email_notification(unnnotified)
            if email_sent:
                for j in unnnotified:
                    mark_job_notified(
                        job_id=j["job_id"],
                        channel="email",
                        recipient=get_config().get("email_address", ""),
                        status="success"
                    )
                logger.info(f"Notification sent for {len(unnnotified)} jobs")
            else:
                logger.error(f"Failed to send email notification: {email_error}")
    else:
        logger.info("No new jobs to notify.")
    return new_count, email_sent, email_error


set_scan_function(scan_and_notify)


@app.before_request
def ensure_db():
    if not hasattr(app, "_db_initialized"):
        init_db()
        app._db_initialized = True


@app.route("/")
def dashboard():
    cfg = get_config()
    configured = is_configured()
    stats = get_stats()
    jobs = get_all_jobs(limit=30)
    next_run = get_next_run_time()
    return render_template(
        "dashboard.html",
        active_page="dashboard",
        configured=configured,
        stats=stats,
        jobs=jobs,
        email_address=cfg.get("email_address", ""),
        next_run=next_run,
        check_interval=cfg.get("check_interval_minutes", 1)
    )


@app.route("/setup", methods=["GET", "POST"])
def setup():
    cfg = get_config()
    stats_val = get_stats()
    if request.method == "POST":
        email = request.form.get("email_address", "").strip()
        provider = request.form.get("email_provider", "smtp").strip()
        smtp_server = request.form.get("email_smtp_server", "smtp.gmail.com").strip()
        smtp_port = int(request.form.get("email_smtp_port", 587))
        username = request.form.get("email_username", "").strip()
        password = request.form.get("email_password", "").strip()
        sendgrid_key = request.form.get("sendgrid_api_key", "").strip()
        interval = int(request.form.get("check_interval_minutes", 1))
        save_config(
            email_address=email,
            email_provider=provider,
            email_smtp_server=smtp_server,
            email_smtp_port=smtp_port,
            email_username=username if username else email,
            email_password=password,
            sendgrid_api_key=sendgrid_key,
            check_interval_minutes=interval
        )
        update_config(
            email_address=email,
            email_provider=provider,
            email_smtp_server=smtp_server,
            email_smtp_port=smtp_port,
            email_username=username if username else email,
            email_password=password,
            sendgrid_api_key=sendgrid_key,
            check_interval_minutes=interval
        )
        restart_scheduler(interval)
        flash("Configuration saved successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("setup.html", active_page="setup", config=cfg, stats=stats_val)


@app.route("/scan", methods=["POST"])
def scan():
    count, email_sent, email_error = scan_and_notify()
    if count > 0:
        if email_sent:
            flash(f"Scan complete! {count} new job(s) found and email sent.", "success")
        else:
            flash(f"Scan complete! {count} new job(s) found but EMAIL FAILED: {email_error}", "danger")
    else:
        flash("Scan complete. No new jobs found.", "info")
    return redirect(url_for("dashboard"))


@app.route("/history")
def history():
    logs = get_notification_history(limit=100)
    stats_val = get_stats()
    return render_template("history.html", active_page="history", logs=logs, stats=stats_val)


@app.route("/api/jobs")
def api_jobs():
    jobs = get_all_jobs(limit=50)
    return jsonify({"jobs": jobs})


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/scan", methods=["POST"])
def api_scan():
    count, email_sent, email_error = scan_and_notify()
    return jsonify({
        "status": "ok",
        "new_jobs": count,
        "email_sent": email_sent,
        "email_error": email_error,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "running",
        "configured": is_configured(),
        "timestamp": datetime.now().isoformat()
    })


def create_app():
    init_db()
    cfg = get_config()
    interval = cfg.get("check_interval_minutes", 1)
    start_scheduler(interval)
    return app


if __name__ == "__main__":
    create_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
