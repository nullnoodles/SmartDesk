"""Settings page — business profile, preferences, backup/restore, about."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_AUTHOR, APP_DESCRIPTION, APP_NAME, APP_VERSION
from app.core.backup_service import BackupService
from app.core.csv_exporter import CSVExporter
from app.core.settings_service import BusinessProfile, SettingsService
from app.data.database import Database
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton, AnimatedCard


class SettingsPage(QWidget):
    """Configurable user preferences and tools (backup, export, about)."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.settings = SettingsService(db)
        self.backup = BackupService(db)
        self.csv = CSVExporter(db)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setSpacing(20)

        from app.ui.widgets.page_header import PageHeader
        header = PageHeader(
            title="Settings",
            subtitle="Business profile, preferences, backup, and CSV export",
        )
        outer.addWidget(header)

        tabs = QTabWidget()
        tabs.addTab(self._build_business_tab(), "Business Profile")
        tabs.addTab(self._build_preferences_tab(), "Preferences")
        tabs.addTab(self._build_data_tab(), "Backup & Export")
        tabs.addTab(self._build_about_tab(), "About")
        outer.addWidget(tabs)

        self.refresh()

    # ------------------------------------------------------------------
    # Business profile tab
    # ------------------------------------------------------------------
    def _build_business_tab(self) -> QWidget:
        wrapper = QScrollArea()
        wrapper.setWidgetResizable(True)
        wrapper.setFrameShape(QScrollArea.NoFrame)

        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(16)

        card = AnimatedCard()
        form = QFormLayout(card)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your name or business name")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@example.com")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+91 98765 43210")
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Street, city, state, pincode")
        self.address_input.setMaximumHeight(80)
        self.gstin_input = QLineEdit()
        self.gstin_input.setPlaceholderText("22AAAAA0000A1Z5 (optional)")

        form.addRow("Business Name *", self.name_input)
        form.addRow("Email", self.email_input)
        form.addRow("Phone", self.phone_input)
        form.addRow("Address", self.address_input)
        form.addRow("GSTIN", self.gstin_input)

        # Logo selector
        logo_row = QHBoxLayout()
        self.logo_path_label = QLabel("No logo selected")
        self.logo_path_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        logo_row.addWidget(self.logo_path_label, 1)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(64, 64)
        self.logo_preview.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; border-radius: 8px;"
        )
        logo_row.addWidget(self.logo_preview)

        choose_logo_btn = QPushButton("Choose…")
        choose_logo_btn.setObjectName("secondary")
        choose_logo_btn.clicked.connect(self._choose_logo)
        logo_row.addWidget(choose_logo_btn)

        clear_logo_btn = QPushButton("Clear")
        clear_logo_btn.setObjectName("secondary")
        clear_logo_btn.clicked.connect(self._clear_logo)
        logo_row.addWidget(clear_logo_btn)

        form.addRow("Logo", logo_row)
        layout.addWidget(card)

        # UPI section
        upi_card = AnimatedCard()
        upi_form = QFormLayout(upi_card)
        upi_form.setContentsMargins(24, 20, 24, 20)
        upi_form.setSpacing(12)

        upi_header = QLabel("UPI Payment (India)")
        upi_header.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        upi_form.addRow(upi_header)

        self.upi_id_input = QLineEdit()
        self.upi_id_input.setPlaceholderText("yourname@upi")
        self.upi_name_input = QLineEdit()
        self.upi_name_input.setPlaceholderText("Display name on payee app")
        upi_form.addRow("UPI ID", self.upi_id_input)
        upi_form.addRow("Display Name", self.upi_name_input)

        layout.addWidget(upi_card)

        # Save button
        save_btn = AnimatedButton("Save Changes", accent=Colors.ACCENT_PRIMARY)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_business)
        layout.addWidget(save_btn)
        layout.addStretch()

        wrapper.setWidget(host)
        return wrapper

    # ------------------------------------------------------------------
    # Preferences tab
    # ------------------------------------------------------------------
    def _build_preferences_tab(self) -> QWidget:
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(16)

        card = AnimatedCard()
        form = QFormLayout(card)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(12)

        self.due_days_input = QSpinBox()
        self.due_days_input.setRange(1, 90)
        self.due_days_input.setSuffix(" days")
        form.addRow("Default Payment Due In", self.due_days_input)

        save_btn = AnimatedButton("Save Preferences", accent=Colors.ACCENT_PRIMARY)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_preferences)

        layout.addWidget(card)
        layout.addWidget(save_btn)
        layout.addStretch()
        return host

    # ------------------------------------------------------------------
    # Data tab — backup & CSV export
    # ------------------------------------------------------------------
    def _build_data_tab(self) -> QWidget:
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(16)

        # Backup card
        backup_card = AnimatedCard()
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(24, 20, 24, 20)
        backup_layout.setSpacing(12)

        backup_layout.addWidget(self._section_title("Backup & Restore"))
        backup_layout.addWidget(
            self._helper_text(
                "Download a single .zip containing your database and exported PDFs. "
                "Restore replaces the current database with the one inside the backup."
            )
        )

        btn_row = QHBoxLayout()
        backup_btn = AnimatedButton("⬇  Create Backup", accent=Colors.ACCENT_INFO)
        backup_btn.clicked.connect(self._create_backup)
        btn_row.addWidget(backup_btn)

        restore_btn = AnimatedButton("⬆  Restore from Backup", accent=Colors.ACCENT_WARNING)
        restore_btn.clicked.connect(self._restore_backup)
        btn_row.addWidget(restore_btn)
        btn_row.addStretch()
        backup_layout.addLayout(btn_row)

        layout.addWidget(backup_card)

        # CSV export card
        csv_card = AnimatedCard()
        csv_layout = QVBoxLayout(csv_card)
        csv_layout.setContentsMargins(24, 20, 24, 20)
        csv_layout.setSpacing(12)

        csv_layout.addWidget(self._section_title("Export to CSV"))
        csv_layout.addWidget(
            self._helper_text(
                "Export tables to CSV files for accountants or spreadsheet software."
            )
        )

        csv_row = QHBoxLayout()
        for label, kind in [
            ("Clients", "clients"),
            ("Projects", "projects"),
            ("Invoices", "invoices"),
        ]:
            btn = QPushButton(f"Export {label}")
            btn.setObjectName("secondary")
            btn.clicked.connect(lambda _=False, k=kind: self._export_csv(k))
            csv_row.addWidget(btn)
        csv_row.addStretch()
        csv_layout.addLayout(csv_row)

        layout.addWidget(csv_card)
        layout.addStretch()
        return host

    # ------------------------------------------------------------------
    # About tab
    # ------------------------------------------------------------------
    def _build_about_tab(self) -> QWidget:
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(16)

        card = AnimatedCard()
        about_layout = QVBoxLayout(card)
        about_layout.setContentsMargins(24, 24, 24, 24)
        about_layout.setSpacing(10)

        title = QLabel(f"{APP_NAME}")
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.ACCENT_PRIMARY}; "
            f"background: transparent;"
        )
        about_layout.addWidget(title)

        version = QLabel(f"Version {APP_VERSION}")
        version.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        about_layout.addWidget(version)

        description = QLabel(APP_DESCRIPTION)
        description.setWordWrap(True)
        description.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 13px;"
        )
        about_layout.addWidget(description)

        about_layout.addSpacing(8)

        meta = QLabel(
            "Offline-first desktop app for freelance creatives.\n"
            "Built with Python, PySide6 (Qt), SQLite, and scikit-learn.\n"
            "Licensed under MIT."
        )
        meta.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        about_layout.addWidget(meta)

        layout.addWidget(card)
        layout.addStretch()
        return host

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        return label

    def _helper_text(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; font-size: 12px;"
        )
        return label

    # ------------------------------------------------------------------
    # Refresh from settings
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        try:
            profile = self.settings.get_business()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load settings: {e}")
            return

        self.name_input.setText(profile.name)
        self.email_input.setText(profile.email)
        self.phone_input.setText(profile.phone)
        self.address_input.setPlainText(profile.address)
        self.gstin_input.setText(profile.gstin)
        self.upi_id_input.setText(profile.upi_id)
        self.upi_name_input.setText(profile.upi_name)
        self._set_logo_path(profile.logo_path)

        self.due_days_input.setValue(self.settings.get_default_due_days())

    # ------------------------------------------------------------------
    # Logo handling
    # ------------------------------------------------------------------
    def _choose_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose Logo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self._set_logo_path(path)

    def _clear_logo(self) -> None:
        self._set_logo_path("")

    def _set_logo_path(self, path: str) -> None:
        self._logo_path = path or ""
        if self._logo_path and Path(self._logo_path).exists():
            pix = QPixmap(self._logo_path)
            if not pix.isNull():
                scaled = pix.scaled(
                    64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.logo_preview.setPixmap(scaled)
            self.logo_path_label.setText(Path(self._logo_path).name)
        else:
            self.logo_preview.clear()
            self.logo_path_label.setText("No logo selected")

    # ------------------------------------------------------------------
    # Save handlers
    # ------------------------------------------------------------------
    def _save_business(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self, "Validation", "Business name is required for invoices."
            )
            self.name_input.setFocus()
            return

        profile = BusinessProfile(
            name=self.name_input.text().strip(),
            email=self.email_input.text().strip(),
            phone=self.phone_input.text().strip(),
            address=self.address_input.toPlainText().strip(),
            gstin=self.gstin_input.text().strip(),
            logo_path=getattr(self, "_logo_path", ""),
            upi_id=self.upi_id_input.text().strip(),
            upi_name=self.upi_name_input.text().strip(),
        )
        try:
            self.settings.save_business(profile)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save: {e}")
            return
        QMessageBox.information(self, "Saved", "Business profile updated.")

    def _save_preferences(self) -> None:
        try:
            self.settings.set_default_due_days(self.due_days_input.value())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save: {e}")
            return
        QMessageBox.information(self, "Saved", "Preferences updated.")

    # ------------------------------------------------------------------
    # Backup / Restore / CSV
    # ------------------------------------------------------------------
    def _create_backup(self) -> None:
        suggested = BackupService.suggested_filename()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Backup", suggested, "Zip Files (*.zip)"
        )
        if not path:
            return
        try:
            output = self.backup.create_backup(Path(path))
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Error: {e}")
            return
        QMessageBox.information(self, "Backup Created", f"Saved to:\n{output}")

    def _restore_backup(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Restore Backup",
            "Restoring will replace your current database. Continue?",
        )
        if confirm != QMessageBox.Yes:
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Choose Backup", "", "Zip Files (*.zip)"
        )
        if not path:
            return

        try:
            self.backup.restore_backup(Path(path))
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", f"Error: {e}")
            return

        QMessageBox.information(
            self,
            "Restore Complete",
            "Backup restored successfully. Please restart SmartDesk to load the new database.",
        )

    def _export_csv(self, kind: str) -> None:
        suggested = f"{kind}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, f"Export {kind}", suggested, "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            if kind == "clients":
                output = self.csv.export_clients(Path(path))
            elif kind == "projects":
                output = self.csv.export_projects(Path(path))
            elif kind == "invoices":
                output = self.csv.export_invoices(Path(path))
            else:
                return
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error: {e}")
            return
        QMessageBox.information(self, "Exported", f"Saved to:\n{output}")
