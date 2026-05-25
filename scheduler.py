import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
_scan_job_func = None


def set_scan_function(func):
    global _scan_job_func
    _scan_job_func = func


def start_scheduler(interval_minutes=1):
    if scheduler.running:
        logger.info("Scheduler already running")
        return
    scheduler.add_job(
        func=_run_scan_wrapper,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="job_scan",
        name="PSU Job Scan",
        replace_existing=True,
        next_run_time=None
    )
    scheduler.start()
    logger.info(f"Scheduler started with {interval_minutes}-minute interval")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def restart_scheduler(interval_minutes=120):
    stop_scheduler()
    start_scheduler(interval_minutes)


def _run_scan_wrapper():
    if _scan_job_func:
        logger.info(f"Auto-scan triggered at {datetime.now().isoformat()}")
        try:
            _scan_job_func()
        except Exception as e:
            logger.error(f"Auto-scan failed: {e}")
    else:
        logger.warning("No scan function registered")


def get_next_run_time():
    for job in scheduler.get_jobs():
        if job.id == "job_scan":
            return job.next_run_time
    return None
