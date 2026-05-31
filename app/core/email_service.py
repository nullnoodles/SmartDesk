"""SMTP email service — send invoices and follow-ups directly from the app.

Configuration lives in app_settings (host, port, username, password, from_addr).
Use TLS by default. Supports optional file attachment (PDF invoice).
"""
from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from app.data.database import Database
from app.data.repositories.settings_repo import SettingsRepository


# Setting keys
KEY_SMTP_HOST = "smtp_host"
KEY_SMTP_PORT = "smtp_port"
KEY_SMTP_USERNAME = "smtp_username"
KEY_SMTP_PASSWORD = "smtp_password"
KEY_SMTP_FROM = "smtp_from"
KEY_SMTP_USE_TLS = "smtp_use_tls"


@dataclass
class SMTPConfig:
    """SMTP server connection settings."""

    host: str = ""
    port: int = 587
    username: str = ""
    password: str = ""
    from_addr: str = ""
    use_tls: bool = True

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.from_addr)


class EmailService:
    """Send emails via SMTP — used for invoices and overdue reminders."""

    def __init__(self, db: Database):
        self.repo = SettingsRepository(db)

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------
    def get_config(self) -> SMTPConfig:
        port_raw = self.repo.get(KEY_SMTP_PORT, "587") or "587"
        try:
            port = int(port_raw)
        except (TypeError, ValueError):
            port = 587

        return SMTPConfig(
            host=self.repo.get(KEY_SMTP_HOST, "") or "",
            port=port,
            username=self.repo.get(KEY_SMTP_USERNAME, "") or "",
            password=self.repo.get(KEY_SMTP_PASSWORD, "") or "",
            from_addr=self.repo.get(KEY_SMTP_FROM, "") or "",
            use_tls=(self.repo.get(KEY_SMTP_USE_TLS, "1") or "1") == "1",
        )

    def save_config(self, config: SMTPConfig) -> None:
        self.repo.set(KEY_SMTP_HOST, config.host)
        self.repo.set(KEY_SMTP_PORT, str(config.port))
        self.repo.set(KEY_SMTP_USERNAME, config.username)
        self.repo.set(KEY_SMTP_PASSWORD, config.password)
        self.repo.set(KEY_SMTP_FROM, config.from_addr)
        self.repo.set(KEY_SMTP_USE_TLS, "1" if config.use_tls else "0")

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------
    def send(
        self,
        to_addr: str,
        subject: str,
        body: str,
        attachment: Path | None = None,
    ) -> None:
        """Send a single email. Raises on failure (caller shows the error)."""
        config = self.get_config()
        if not config.is_configured:
            raise RuntimeError(
                "SMTP is not configured. Open Settings → Email to set it up."
            )

        msg = EmailMessage()
        msg["From"] = config.from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment is not None:
            attachment = Path(attachment)
            if attachment.exists():
                ctype = "application/pdf" if attachment.suffix.lower() == ".pdf" else "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                with open(attachment, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=attachment.name,
                    )

        # Connect
        if config.use_tls:
            with smtplib.SMTP(config.host, config.port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if config.username:
                    server.login(config.username, config.password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(config.host, config.port, timeout=30) as server:
                if config.username:
                    server.login(config.username, config.password)
                server.send_message(msg)

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------
    @staticmethod
    def invoice_subject(invoice_number: str, business_name: str = "") -> str:
        if business_name:
            return f"Invoice {invoice_number} from {business_name}"
        return f"Invoice {invoice_number}"

    @staticmethod
    def invoice_body(client_name: str, invoice_number: str, total: float, due_date: str, business_name: str = "") -> str:
        signature = f"\n\nThanks,\n{business_name}" if business_name else ""
        return (
            f"Hi {client_name},\n\n"
            f"Please find attached invoice {invoice_number} for ₹{total:,.2f}.\n"
            f"Payment is due by {due_date}.\n\n"
            f"Let me know if you have any questions."
            f"{signature}\n"
        )

    @staticmethod
    def overdue_subject(invoice_number: str) -> str:
        return f"Friendly reminder: Invoice {invoice_number} is overdue"

    @staticmethod
    def overdue_body(client_name: str, invoice_number: str, total: float, due_date: str, days_overdue: int, business_name: str = "") -> str:
        signature = f"\n\nThanks,\n{business_name}" if business_name else ""
        return (
            f"Hi {client_name},\n\n"
            f"Just a friendly reminder that invoice {invoice_number} for ₹{total:,.2f} "
            f"was due on {due_date} and is now {days_overdue} day(s) overdue.\n\n"
            f"If the payment has already been made, please ignore this message. "
            f"Otherwise, I would appreciate it if you could process it at your earliest convenience."
            f"{signature}\n"
        )
