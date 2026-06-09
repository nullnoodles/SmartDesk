"""Notification service — desktop alerts and automated reminders.

Supports:
- Desktop notifications (via plyer)
- Email reminders (via email_service)
- Configurable frequency and thresholds
- Multiple notification types (overdue invoices, deadlines, payments)
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.data.database import Database
from app.data.repositories.settings_repo import SettingsRepository


# Setting keys
KEY_NOTIFICATIONS_ENABLED = "notifications_enabled"
KEY_DESKTOP_NOTIFICATIONS = "desktop_notifications_enabled"
KEY_EMAIL_REMINDERS = "email_reminders_enabled"
KEY_REMINDER_DAYS_BEFORE = "reminder_days_before_due"
KEY_REMINDER_FREQUENCY = "reminder_frequency"  # daily, weekly
KEY_LAST_REMINDER_CHECK = "last_reminder_check"
KEY_NOTIFY_OVERDUE_INVOICES = "notify_overdue_invoices"
KEY_NOTIFY_UPCOMING_DEADLINES = "notify_upcoming_deadlines"
KEY_NOTIFY_PAYMENTS_RECEIVED = "notify_payments_received"


class NotificationType(Enum):
    """Types of notifications the system can send."""
    OVERDUE_INVOICE = "overdue_invoice"
    UPCOMING_DEADLINE = "upcoming_deadline"
    PAYMENT_RECEIVED = "payment_received"
    GENERAL = "general"


@dataclass
class NotificationConfig:
    """User notification preferences."""
    enabled: bool = True
    desktop_enabled: bool = True
    email_enabled: bool = True
    days_before_due: int = 3
    frequency: str = "daily"  # daily or weekly
    notify_overdue: bool = True
    notify_deadlines: bool = True
    notify_payments: bool = True

    @property
    def is_configured(self) -> bool:
        return self.enabled and (self.desktop_enabled or self.email_enabled)


class NotificationService:
    """Manages all notification types and delivery methods."""

    def __init__(self, db: Database):
        self.db = db
        self.repo = SettingsRepository(db)
        self._plyer_available = self._check_plyer()

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------
    def get_config(self) -> NotificationConfig:
        """Load notification preferences from database."""
        enabled = self.repo.get(KEY_NOTIFICATIONS_ENABLED, "1") == "1"
        desktop = self.repo.get(KEY_DESKTOP_NOTIFICATIONS, "1") == "1"
        email = self.repo.get(KEY_EMAIL_REMINDERS, "1") == "1"
        
        days_raw = self.repo.get(KEY_REMINDER_DAYS_BEFORE, "3")
        try:
            days = int(days_raw)
        except (TypeError, ValueError):
            days = 3

        frequency = self.repo.get(KEY_REMINDER_FREQUENCY, "daily") or "daily"
        notify_overdue = self.repo.get(KEY_NOTIFY_OVERDUE_INVOICES, "1") == "1"
        notify_deadlines = self.repo.get(KEY_NOTIFY_UPCOMING_DEADLINES, "1") == "1"
        notify_payments = self.repo.get(KEY_NOTIFY_PAYMENTS_RECEIVED, "1") == "1"

        return NotificationConfig(
            enabled=enabled,
            desktop_enabled=desktop,
            email_enabled=email,
            days_before_due=days,
            frequency=frequency,
            notify_overdue=notify_overdue,
            notify_deadlines=notify_deadlines,
            notify_payments=notify_payments,
        )

    def save_config(self, config: NotificationConfig) -> None:
        """Save notification preferences to database."""
        self.repo.set(KEY_NOTIFICATIONS_ENABLED, "1" if config.enabled else "0")
        self.repo.set(KEY_DESKTOP_NOTIFICATIONS, "1" if config.desktop_enabled else "0")
        self.repo.set(KEY_EMAIL_REMINDERS, "1" if config.email_enabled else "0")
        self.repo.set(KEY_REMINDER_DAYS_BEFORE, str(config.days_before_due))
        self.repo.set(KEY_REMINDER_FREQUENCY, config.frequency)
        self.repo.set(KEY_NOTIFY_OVERDUE_INVOICES, "1" if config.notify_overdue else "0")
        self.repo.set(KEY_NOTIFY_UPCOMING_DEADLINES, "1" if config.notify_deadlines else "0")
        self.repo.set(KEY_NOTIFY_PAYMENTS_RECEIVED, "1" if config.notify_payments else "0")

    # ------------------------------------------------------------------
    # Desktop notifications (plyer)
    # ------------------------------------------------------------------
    def _check_plyer(self) -> bool:
        """Check if plyer is available for desktop notifications."""
        try:
            from plyer import notification
            return True
        except ImportError:
            return False

    def send_desktop_notification(
        self,
        title: str,
        message: str,
        timeout: int = 10,
    ) -> bool:
        """Send desktop notification. Returns True if sent successfully."""
        config = self.get_config()
        if not config.enabled or not config.desktop_enabled:
            return False

        if not self._plyer_available:
            return False

        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="SmartDesk",
                timeout=timeout,
            )
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Check for pending notifications
    # ------------------------------------------------------------------

    def check_overdue_invoices(self) -> list[dict[str, Any]]:
        """Find all overdue unpaid invoices."""
        config = self.get_config()
        if not config.enabled or not config.notify_overdue:
            return []

        today = datetime.date.today().isoformat()
        
        rows = self.db.execute(
            """
            SELECT 
                i.id, i.invoice_number, i.total, i.due_date,
                c.name as client_name, c.email as client_email,
                p.name as project_name
            FROM invoices i
            JOIN projects p ON i.project_id = p.id
            JOIN clients c ON p.client_id = c.id
            WHERE i.status = 'Unpaid'
            AND i.due_date < ?
            ORDER BY i.due_date ASC
            """,
            (today,),
        )
        
        return [dict(row) for row in rows]

    def check_upcoming_deadlines(self, days_ahead: int | None = None) -> list[dict[str, Any]]:
        """Find projects with deadlines in next N days."""
        config = self.get_config()
        if not config.enabled or not config.notify_deadlines:
            return []

        if days_ahead is None:
            days_ahead = config.days_before_due

        today = datetime.date.today()
        future_date = (today + datetime.timedelta(days=days_ahead)).isoformat()
        today_str = today.isoformat()

        rows = self.db.execute(
            """
            SELECT 
                p.id, p.name as project_name, p.deadline, p.status,
                c.name as client_name, c.email as client_email
            FROM projects p
            JOIN clients c ON p.client_id = c.id
            WHERE p.status NOT IN ('Completed', 'Cancelled')
            AND p.deadline IS NOT NULL
            AND p.deadline >= ?
            AND p.deadline <= ?
            ORDER BY p.deadline ASC
            """,
            (today_str, future_date),
        )
        
        return [dict(row) for row in rows]

    def check_recent_payments(self, hours_ago: int = 24) -> list[dict[str, Any]]:
        """Find payments received in last N hours."""
        config = self.get_config()
        if not config.enabled or not config.notify_payments:
            return []

        cutoff = (
            datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
        ).isoformat()

        rows = self.db.execute(
            """
            SELECT 
                pay.id, pay.amount_paid, pay.payment_date, pay.payment_mode,
                i.invoice_number, i.total as invoice_total,
                c.name as client_name,
                p.name as project_name
            FROM payments pay
            JOIN invoices i ON pay.invoice_id = i.id
            JOIN projects p ON i.project_id = p.id
            JOIN clients c ON p.client_id = c.id
            WHERE pay.payment_date >= ?
            ORDER BY pay.payment_date DESC
            """,
            (cutoff,),
        )
        
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Send notifications for specific events
    # ------------------------------------------------------------------
    def notify_overdue_invoice(self, invoice_data: dict[str, Any]) -> dict[str, bool]:
        """Send notifications for a single overdue invoice."""
        config = self.get_config()
        results = {"desktop": False, "email": False}

        if not config.enabled:
            return results

        # Desktop notification
        if config.desktop_enabled:
            days_overdue = self._calculate_days_overdue(invoice_data["due_date"])
            title = f"Invoice {invoice_data['invoice_number']} Overdue"
            message = (
                f"{invoice_data['client_name']}: ₹{invoice_data['total']:,.2f}\n"
                f"Overdue by {days_overdue} day(s)"
            )
            results["desktop"] = self.send_desktop_notification(title, message)

        # Email reminder (if email address exists)
        if config.email_enabled and invoice_data.get("client_email"):
            try:
                from app.core.email_service import EmailService
                email_service = EmailService(self.db)
                
                days_overdue = self._calculate_days_overdue(invoice_data["due_date"])
                subject = email_service.overdue_subject(invoice_data["invoice_number"])
                body = email_service.overdue_body(
                    client_name=invoice_data["client_name"],
                    invoice_number=invoice_data["invoice_number"],
                    total=invoice_data["total"],
                    due_date=invoice_data["due_date"],
                    days_overdue=days_overdue,
                )
                
                email_service.send(
                    to_addr=invoice_data["client_email"],
                    subject=subject,
                    body=body,
                )
                results["email"] = True
            except Exception:
                results["email"] = False

        return results

    def notify_upcoming_deadline(self, project_data: dict[str, Any]) -> bool:
        """Send desktop notification for upcoming project deadline."""
        config = self.get_config()
        if not config.enabled or not config.desktop_enabled:
            return False

        days_until = self._calculate_days_until(project_data["deadline"])
        title = f"Deadline Approaching: {project_data['project_name']}"
        message = (
            f"Client: {project_data['client_name']}\n"
            f"Due in {days_until} day(s) ({project_data['deadline']})"
        )
        
        return self.send_desktop_notification(title, message)

    def notify_payment_received(self, payment_data: dict[str, Any]) -> bool:
        """Send desktop notification for received payment."""
        config = self.get_config()
        if not config.enabled or not config.desktop_enabled:
            return False

        title = "💰 Payment Received"
        message = (
            f"₹{payment_data['amount_paid']:,.2f} from {payment_data['client_name']}\n"
            f"Invoice: {payment_data['invoice_number']}"
        )
        
        return self.send_desktop_notification(title, message, timeout=15)

    # ------------------------------------------------------------------
    # Batch notification processing
    # ------------------------------------------------------------------
    def send_all_overdue_reminders(self) -> dict[str, Any]:
        """Send notifications for all overdue invoices."""
        overdue = self.check_overdue_invoices()
        results = {
            "total": len(overdue),
            "desktop_sent": 0,
            "emails_sent": 0,
            "failed": [],
        }

        for invoice in overdue:
            sent = self.notify_overdue_invoice(invoice)
            if sent["desktop"]:
                results["desktop_sent"] += 1
            if sent["email"]:
                results["emails_sent"] += 1
            if not sent["desktop"] and not sent["email"]:
                results["failed"].append(invoice["invoice_number"])

        return results

    def send_all_deadline_reminders(self) -> dict[str, Any]:
        """Send notifications for all upcoming deadlines."""
        deadlines = self.check_upcoming_deadlines()
        results = {
            "total": len(deadlines),
            "sent": 0,
            "failed": [],
        }

        for project in deadlines:
            if self.notify_upcoming_deadline(project):
                results["sent"] += 1
            else:
                results["failed"].append(project["project_name"])

        return results

    # ------------------------------------------------------------------
    # Scheduling helpers
    # ------------------------------------------------------------------
    def should_check_reminders(self) -> bool:
        """Check if enough time has passed since last reminder check."""
        config = self.get_config()
        if not config.enabled:
            return False

        last_check_str = self.repo.get(KEY_LAST_REMINDER_CHECK)
        if not last_check_str:
            return True

        try:
            last_check = datetime.datetime.fromisoformat(last_check_str)
        except (TypeError, ValueError):
            return True

        now = datetime.datetime.now()
        hours_since = (now - last_check).total_seconds() / 3600

        # Check based on frequency setting
        if config.frequency == "daily":
            return hours_since >= 24
        elif config.frequency == "weekly":
            return hours_since >= 168  # 7 days
        else:
            return hours_since >= 24  # default to daily

    def mark_reminder_check_done(self) -> None:
        """Record that reminder check was just performed."""
        now = datetime.datetime.now().isoformat()
        self.repo.set(KEY_LAST_REMINDER_CHECK, now)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _calculate_days_overdue(due_date_str: str) -> int:
        """Calculate how many days overdue an invoice is."""
        try:
            due_date = datetime.date.fromisoformat(due_date_str)
            today = datetime.date.today()
            delta = (today - due_date).days
            return max(0, delta)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _calculate_days_until(deadline_str: str) -> int:
        """Calculate how many days until a deadline."""
        try:
            deadline = datetime.date.fromisoformat(deadline_str)
            today = datetime.date.today()
            delta = (deadline - today).days
            return max(0, delta)
        except (TypeError, ValueError):
            return 0

    # ------------------------------------------------------------------
    # System status
    # ------------------------------------------------------------------
    def get_notification_summary(self) -> dict[str, Any]:
        """Get current notification status and pending items."""
        config = self.get_config()
        overdue = self.check_overdue_invoices()
        deadlines = self.check_upcoming_deadlines()
        
        return {
            "enabled": config.enabled,
            "desktop_available": self._plyer_available,
            "pending_overdue": len(overdue),
            "pending_deadlines": len(deadlines),
            "config": config,
        }
