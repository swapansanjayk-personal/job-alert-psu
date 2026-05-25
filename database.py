import sqlite3
import os
from datetime import datetime

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "job_alert.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            email_address TEXT NOT NULL DEFAULT '',
            email_provider TEXT NOT NULL DEFAULT 'smtp',
            email_smtp_server TEXT NOT NULL DEFAULT 'smtp.gmail.com',
            email_smtp_port INTEGER NOT NULL DEFAULT 587,
            email_username TEXT NOT NULL DEFAULT '',
            email_password TEXT NOT NULL DEFAULT '',
            mailjet_api_key TEXT NOT NULL DEFAULT '',
            mailjet_secret_key TEXT NOT NULL DEFAULT '',
            check_interval_minutes INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            organization TEXT NOT NULL,
            location TEXT DEFAULT '',
            eligibility TEXT DEFAULT '',
            selection_process TEXT DEFAULT '',
            posted_date TEXT DEFAULT '',
            deadline TEXT DEFAULT '',
            apply_url TEXT DEFAULT '',
            description TEXT DEFAULT '',
            is_non_gate INTEGER DEFAULT 1,
            tags TEXT DEFAULT '',
            source TEXT DEFAULT 'seed',
            batch_years TEXT DEFAULT '',
            found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notified INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS notification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            job_title TEXT DEFAULT '',
            organization TEXT DEFAULT '',
            channel TEXT NOT NULL,
            recipient TEXT DEFAULT '',
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'pending',
            error_message TEXT DEFAULT ''
        );

        CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_notified ON jobs(notified);
        CREATE INDEX IF NOT EXISTS idx_notification_log_sent ON notification_log(sent_at);

        INSERT OR IGNORE INTO config (id) VALUES (1);
    """)
    # Migrate old databases: add missing columns
    for col, col_type in [("email_provider", "TEXT NOT NULL DEFAULT 'smtp'"),
                          ("mailjet_api_key", "TEXT NOT NULL DEFAULT ''"),
                          ("mailjet_secret_key", "TEXT NOT NULL DEFAULT ''")]:
        try:
            conn.execute(f"ALTER TABLE config ADD COLUMN {col} {col_type}")
        except Exception:
            pass
    conn.commit()
    conn.close()


def get_config():
    conn = get_connection()
    row = conn.execute("SELECT * FROM config WHERE id = 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}


def update_config(**kwargs):
    allowed = ["email_address", "email_provider", "email_smtp_server",
               "email_smtp_port", "email_username", "email_password",
               "mailjet_api_key", "mailjet_secret_key", "check_interval_minutes"]
    sets = []
    values = []
    for key, val in kwargs.items():
        if key in allowed:
            sets.append(f"{key} = ?")
            values.append(val)
    if not sets:
        return
    values.append(datetime.now().isoformat())
    sets.append("updated_at = ?")
    conn = get_connection()
    conn.execute(f"UPDATE config SET {', '.join(sets)} WHERE id = 1", values)
    conn.commit()
    conn.close()


def is_job_exists(job_id):
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    conn.close()
    return row is not None


def insert_job(job):
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO jobs
            (job_id, title, organization, location, eligibility,
             selection_process, posted_date, deadline, apply_url,
             description, is_non_gate, tags, source, batch_years)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job.get("job_id"),
        job.get("title"),
        job.get("organization"),
        job.get("location", ""),
        job.get("eligibility", ""),
        job.get("selection_process", ""),
        job.get("posted_date", ""),
        job.get("deadline", ""),
        job.get("apply_url", ""),
        job.get("description", ""),
        1 if job.get("is_non_gate", True) else 0,
        ",".join(job.get("tags", [])),
        job.get("source", "seed"),
        ",".join(job.get("batch_years", []))
    ))
    conn.commit()
    conn.close()


def get_unnotified_jobs():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM jobs WHERE notified = 0 ORDER BY found_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_job_notified(job_id, channel="email", recipient="", status="success", error=""):
    conn = get_connection()
    conn.execute("UPDATE jobs SET notified = 1 WHERE job_id = ?", (job_id,))
    conn.execute("""
        INSERT INTO notification_log
            (job_id, job_title, organization, channel, recipient, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        _get_job_title(job_id, conn),
        _get_job_org(job_id, conn),
        channel,
        recipient,
        status,
        error
    ))
    conn.commit()
    conn.close()


def _get_job_title(job_id, conn=None):
    if conn:
        row = conn.execute("SELECT title FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return row["title"] if row else ""
    c = get_connection()
    row = c.execute("SELECT title FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    c.close()
    return row["title"] if row else ""


def _get_job_org(job_id, conn=None):
    if conn:
        row = conn.execute("SELECT organization FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return row["organization"] if row else ""
    c = get_connection()
    row = c.execute("SELECT organization FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    c.close()
    return row["organization"] if row else ""


def get_all_jobs(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM jobs ORDER BY found_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_notification_history(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notification_log ORDER BY sent_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_connection()
    total_jobs = conn.execute("SELECT COUNT(*) as c FROM jobs").fetchone()["c"]
    active_jobs = conn.execute("SELECT COUNT(*) as c FROM jobs WHERE notified = 0").fetchone()["c"]
    notified = conn.execute("SELECT COUNT(*) as c FROM jobs WHERE notified = 1").fetchone()["c"]
    orgs = conn.execute("SELECT COUNT(DISTINCT organization) as c FROM jobs").fetchone()["c"]
    sent = conn.execute("SELECT COUNT(*) as c FROM notification_log WHERE status = 'success'").fetchone()["c"]
    conn.close()
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "notified": notified,
        "organizations": orgs,
        "notifications_sent": sent
    }
