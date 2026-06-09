"""Background notification scheduler using QTimer.

Checks for pending notifications every hour and sends them automatically.
Runs in the main Qt event loop (no threading needed).
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal

from app.data.database import Database
from app.core.notification_service import NotificationService


class NotificationScheduler(QObject):
    """Background scheduler for automated notifications."""

    # Signals
    notifications_sent = Signal(dict)  # Emits results after sending
    check_completed = Signal()

    def __init__(self, db: Database, check_interval_ms: int = 3600000):
        """
        Initialize scheduler.
        
        Args:
            db: Database connection
            check_interval_ms: Check interval in milliseconds (default: 1 hour = 3600000ms)
        """
        super().__init__()
        self.db = db
        self.notification_service = NotificationService(db)
        self.check_interval_ms = check_interval_ms
        
        # Timer for periodic checks
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_and_send)
        self.timer.setInterval(check_interval_ms)
        
        self._running = False

    def start(self) -> None:
        """Start the background scheduler."""
        if self._running:
            return
        
        self._running = True
        self.timer.start()
        
        # Do initial check immediately
        self._check_and_send()

    def stop(self) -> None:
        """Stop the background scheduler."""
        if not self._running:
            return
        
        self._running = False
        self.timer.stop()

    def is_running(self) -> bool:
        """Check if scheduler is currently running."""
        return self._running

    def trigger_manual_check(self) -> None:
        """Manually trigger a notification check (bypasses frequency limit)."""
        self._check_and_send(force=True)

    def _check_and_send(self, force: bool = False) -> None:
        """Check for pending notifications and send them."""
        # Check if we should run based on frequency settings
        if not force and not self.notification_service.should_check_reminders():
            return

        try:
            results = {
                "overdue": {"total": 0, "desktop_sent": 0, "emails_sent": 0},
                "deadlines": {"total": 0, "sent": 0},
                "success": True,
                "error": None,
            }

            # Send overdue invoice reminders
            overdue_results = self.notification_service.send_all_overdue_reminders()
            results["overdue"] = overdue_results

            # Send deadline reminders
            deadline_results = self.notification_service.send_all_deadline_reminders()
            results["deadlines"] = deadline_results

            # Mark check as completed
            self.notification_service.mark_reminder_check_done()

            # Emit signal with results
            self.notifications_sent.emit(results)
            self.check_completed.emit()

        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
            }
            self.notifications_sent.emit(results)

    def set_check_interval(self, interval_ms: int) -> None:
        """Change the check interval (in milliseconds)."""
        self.check_interval_ms = interval_ms
        self.timer.setInterval(interval_ms)

    def get_status(self) -> dict:
        """Get current scheduler status."""
        return {
            "running": self._running,
            "interval_hours": self.check_interval_ms / 3600000,
            "next_check_in_ms": self.timer.remainingTime() if self._running else 0,
        }
