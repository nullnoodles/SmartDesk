"""Settings service — typed accessors over the key/value SettingsRepository."""
from __future__ import annotations

from dataclasses import asdict, dataclass

from app.data.database import Database
from app.data.repositories.settings_repo import SettingsRepository


# Setting keys (centralized to avoid typos)
KEY_FIRST_RUN_DONE = "first_run_done"
KEY_BUSINESS_NAME = "business_name"
KEY_BUSINESS_EMAIL = "business_email"
KEY_BUSINESS_PHONE = "business_phone"
KEY_BUSINESS_ADDRESS = "business_address"
KEY_BUSINESS_GSTIN = "business_gstin"
KEY_BUSINESS_LOGO_PATH = "business_logo_path"
KEY_UPI_ID = "upi_id"
KEY_UPI_NAME = "upi_name"
KEY_DEFAULT_CURRENCY = "default_currency"
KEY_DEFAULT_GST_RATE = "default_gst_rate"
KEY_DEFAULT_DUE_DAYS = "default_due_days"


@dataclass
class BusinessProfile:
    """Sender details rendered on PDF invoices."""

    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    gstin: str = ""
    logo_path: str = ""
    upi_id: str = ""
    upi_name: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(self.name.strip())


class SettingsService:
    """High-level wrapper over the settings repository with typed accessors."""

    def __init__(self, db: Database):
        self.repo = SettingsRepository(db)

    # ---- First-run flag --------------------------------------------------
    def is_first_run(self) -> bool:
        return self.repo.get(KEY_FIRST_RUN_DONE) != "1"

    def mark_first_run_done(self) -> None:
        self.repo.set(KEY_FIRST_RUN_DONE, "1")

    # ---- Business profile ------------------------------------------------
    def get_business(self) -> BusinessProfile:
        return BusinessProfile(
            name=self.repo.get(KEY_BUSINESS_NAME, "") or "",
            email=self.repo.get(KEY_BUSINESS_EMAIL, "") or "",
            phone=self.repo.get(KEY_BUSINESS_PHONE, "") or "",
            address=self.repo.get(KEY_BUSINESS_ADDRESS, "") or "",
            gstin=self.repo.get(KEY_BUSINESS_GSTIN, "") or "",
            logo_path=self.repo.get(KEY_BUSINESS_LOGO_PATH, "") or "",
            upi_id=self.repo.get(KEY_UPI_ID, "") or "",
            upi_name=self.repo.get(KEY_UPI_NAME, "") or "",
        )

    def save_business(self, profile: BusinessProfile) -> None:
        mapping = {
            KEY_BUSINESS_NAME: profile.name,
            KEY_BUSINESS_EMAIL: profile.email,
            KEY_BUSINESS_PHONE: profile.phone,
            KEY_BUSINESS_ADDRESS: profile.address,
            KEY_BUSINESS_GSTIN: profile.gstin,
            KEY_BUSINESS_LOGO_PATH: profile.logo_path,
            KEY_UPI_ID: profile.upi_id,
            KEY_UPI_NAME: profile.upi_name,
        }
        for key, value in mapping.items():
            self.repo.set(key, value or "")

    # ---- Defaults --------------------------------------------------------
    def get_default_due_days(self, fallback: int = 14) -> int:
        raw = self.repo.get(KEY_DEFAULT_DUE_DAYS)
        try:
            return int(raw) if raw else fallback
        except (TypeError, ValueError):
            return fallback

    def set_default_due_days(self, days: int) -> None:
        self.repo.set(KEY_DEFAULT_DUE_DAYS, str(int(days)))

    def get_default_gst_rate(self, fallback: float = 0.18) -> float:
        raw = self.repo.get(KEY_DEFAULT_GST_RATE)
        try:
            return float(raw) if raw else fallback
        except (TypeError, ValueError):
            return fallback

    def set_default_gst_rate(self, rate: float) -> None:
        self.repo.set(KEY_DEFAULT_GST_RATE, str(rate))

    # ---- Debug -----------------------------------------------------------
    def as_dict(self) -> dict[str, str]:
        return self.repo.get_all()

    def export_business_as_dict(self) -> dict[str, str]:
        return asdict(self.get_business())
