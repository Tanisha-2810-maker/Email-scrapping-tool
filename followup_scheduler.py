from datetime import datetime, timedelta

from emailer.sender import send_email

_scheduler = None


def get_scheduler():
    global _scheduler
    if _scheduler is None:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
        except ImportError as exc:
            raise ImportError("Install APScheduler first: pip install apscheduler") from exc

        _scheduler = BackgroundScheduler()
        _scheduler.start()
    return _scheduler


def send_followup(receiver, subject="Follow-up", body="Hi, just following up on my previous email."):
    send_email(receiver, subject, body)


def schedule_followups(receiver, delay_hours=24):
    """Schedule one follow-up email. No auto-run and no infinite loop."""
    run_time = datetime.now() + timedelta(hours=delay_hours)
    scheduler = get_scheduler()
    scheduler.add_job(
        send_followup,
        "date",
        run_date=run_time,
        args=[receiver],
        id=f"followup-{receiver}-{int(run_time.timestamp())}",
        replace_existing=True,
    )
    return run_time
