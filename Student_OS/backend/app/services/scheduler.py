import asyncio
import logging
from datetime import datetime, timedelta
from app.database import get_db_connection, log_agent_event
from app.services.digicampus_scraper import sync_digicampus
from app.services.notifications import dispatch_alert

logger = logging.getLogger("scheduler")

async def check_upcoming_deadlines():
    """
    Checks for assignments due within 48 hours or 24 hours and dispatches mobile alerts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.id, a.title, a.deadline, s.name as subject_name
    FROM assignments a
    JOIN subjects s ON a.subject_id = s.id
    WHERE a.status = 'pending' AND a.deadline IS NOT NULL
    """)
    assignments = cursor.fetchall()
    now = datetime.now()

    for item in assignments:
        try:
            deadline_dt = datetime.fromisoformat(item["deadline"].replace(" ", "T"))
            time_left = deadline_dt - now
            hours_left = time_left.total_seconds() / 3600.0

            if 0 < hours_left <= 24:
                msg = f"⏳ Urgent: '{item['title']}' for {item['subject_name']} is due in {int(hours_left)} hours!"
                await dispatch_alert("Assignment Deadline < 24h", msg, priority="urgent", tags="alarm_clock")
            elif 24 < hours_left <= 48:
                msg = f"📌 Reminder: '{item['title']}' for {item['subject_name']} is due in {int(hours_left)} hours."
                await dispatch_alert("Assignment Reminder", msg, priority="default", tags="calendar")
        except Exception as e:
            logger.debug(f"Could not parse deadline for assignment {item['id']}: {e}")

    conn.close()

async def background_scheduler_loop(interval_seconds: int = 1800):
    """
    Runs every 30 minutes to check deadlines and synchronize portal data.
    """
    log_agent_event("INFO", "Background Student OS scheduler started.")
    while True:
        try:
            await check_upcoming_deadlines()
        except Exception as e:
            logger.error(f"Error in scheduler check: {e}")
        await asyncio.sleep(interval_seconds)
