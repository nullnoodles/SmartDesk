"""First-run welcome dialog — introduces the app and offers sample data."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

from app.config import APP_NAME, APP_VERSION
from app.ui.styles.theme import Colors


class WelcomeDialog(QDialog):
    """Welcome dialog shown on first run.

    User can choose to load sample data and is reminded to fill in business info.
    Use ``load_sample_data`` after ``exec()`` to read the user's choice.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Welcome to {APP_NAME}")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 22)
        layout.setSpacing(14)

        title = QLabel(f"Welcome to {APP_NAME} 👋")
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.ACCENT_PRIMARY};"
        )
        layout.addWidget(title)

        version = QLabel(f"Version {APP_VERSION}")
        version.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(version)

        body = QLabel(
            "SmartDesk helps you manage clients, projects, invoices, time, "
            "and contracts — all offline.\n\n"
            "A few quick tips to get started:\n"
            "  • Visit Settings → Business Profile to add your name, address, "
            "GSTIN, and UPI ID.\n"
            "  • Add a client first, then create a project for them.\n"
            "  • Generate invoices with auto-GST and export them as PDFs."
        )
        body.setWordWrap(True)
        body.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; line-height: 1.5;"
        )
        layout.addWidget(body)

        self.sample_checkbox = QCheckBox("Load sample data so I can explore the app")
        self.sample_checkbox.setChecked(False)
        layout.addWidget(self.sample_checkbox)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.button(QDialogButtonBox.Ok).setText("Get Started")
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    @property
    def load_sample_data(self) -> bool:
        return self.sample_checkbox.isChecked()
