import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from app.database import log_agent_event, get_db_connection
from app.services.notification_service import send_windows_notification

logger = logging.getLogger("scheduler_service")

class WorkstationDaemon:
    def __init__(self):
        self.is_running = False
        self.interval_seconds = 6 * 3600  # Run every 6 hours by default
        self.thread: Optional[threading.Thread] = None
        self.last_run_time: Optional[str] = None
        self.auto_apply_enabled = True

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Workstation continuous daemon started.")

    def stop(self):
        self.is_running = False
        logger.info("Workstation continuous daemon stopped.")

    def _run_loop(self):
        # Initial wait of 60 seconds after server startup
        time.sleep(60)
        while self.is_running:
            try:
                self._execute_routine()
            except Exception as e:
                logger.error(f"Daemon routine error: {e}")
            
            # Sleep in small increments so we can terminate cleanly
            for _ in range(self.interval_seconds):
                if not self.is_running:
                    break
                time.sleep(1)

    def _execute_routine(self):
        self.last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_agent_event("INFO", f"Executing periodic background daemon checks at {self.last_run_time}")

        # 1. Academic Attendance Risk Check
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, attendance_percentage FROM subjects WHERE attendance_percentage < 75.0")
            at_risk = cursor.fetchall()
            conn.close()

            if at_risk:
                names = ", ".join([r[0] for r in at_risk])
                send_windows_notification(
                    "Student OS Academic Alert",
                    f"Warning: Attendance below 75% threshold in: {names}"
                )
        except Exception as e:
            logger.warning(f"Attendance check error in daemon: {e}")

        # 2. Continuous Auto-Apply Opportunity Check
        if self.auto_apply_enabled:
            try:
                from app.services.auto_apply_engine import run_auto_apply_pipeline
                summary = run_auto_apply_pipeline()
                if summary.get("applied", 0) > 0:
                    send_windows_notification(
                        "Auto-Apply Success",
                        f"Successfully applied to {summary['applied']} new opportunity!"
                    )
            except Exception as e:
                logger.debug(f"Auto-apply check in daemon: {e}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "auto_apply_enabled": self.auto_apply_enabled,
            "interval_hours": round(self.interval_seconds / 3600, 1),
            "last_run": self.last_run_time or "Pending first run"
        }

workstation_daemon = WorkstationDaemon()
