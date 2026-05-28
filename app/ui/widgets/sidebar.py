"""Sidebar navigation — Studio Graphite design.

Persistent left sidebar with branding header, navigation buttons, and a
footer that pins Settings + version + status indicator.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_VERSION
from app.ui.styles.theme import Colors


class Sidebar(QWidget):
    """Persistent left sidebar with active-state nav."""

    page_changed = Signal(str)

    # (page_id, icon glyph, label)
    PAGES = [
        ("dashboard", "📊", "Dashboard"),
        ("clients", "👥", "Clients"),
        ("projects", "📁", "Projects"),
        ("invoices", "🧾", "Invoices"),
        ("time", "⏱️", "Time Log"),
        ("contracts", "📝", "Contracts"),
        ("analytics", "🤖", "AI Analytics"),
    ]

    FOOTER_PAGES = [
        ("settings", "⚙️", "Settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 28, 0, 24)
        layout.setSpacing(0)

        # ─── Brand header ─────────────────────────────────────────────────
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(20, 0, 20, 0)
        brand_row.setSpacing(12)

        logo = QLabel("◆")
        logo.setFixedSize(36, 36)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(
            f"background-color: {Colors.ACCENT_PRIMARY}; "
            f"border-radius: 10px; color: {Colors.TEXT_ON_PRIMARY}; "
            f"font-size: 18px; font-weight: 700;"
        )
        brand_row.addWidget(logo)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)

        title = QLabel("SmartDesk")
        title.setStyleSheet(
            f"color: {Colors.ACCENT_PRIMARY_LIGHT}; background: transparent; "
            f"font-size: 18px; font-weight: 700; letter-spacing: -0.01em;"
        )
        brand_text.addWidget(title)

        subtitle = QLabel("CREATIVE WORKSPACE")
        subtitle.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 9px; font-weight: 700; letter-spacing: 0.12em;"
        )
        brand_text.addWidget(subtitle)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        layout.addSpacing(28)

        # Subtle divider
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {Colors.BORDER_SUBTLE}; max-height: 1px;")
        layout.addWidget(sep)

        layout.addSpacing(16)

        # Nav section label
        nav_label = QLabel("  NAVIGATION")
        nav_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 10px; font-weight: 700; letter-spacing: 0.12em; "
            f"padding-left: 16px;"
        )
        layout.addWidget(nav_label)
        layout.addSpacing(8)

        # Nav buttons
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}

        for page_id, icon, label in self.PAGES:
            btn = self._make_nav_button(page_id, icon, label)
            self.button_group.addButton(btn)
            self.buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Footer divider
        bottom_sep = QFrame()
        bottom_sep.setFrameShape(QFrame.HLine)
        bottom_sep.setFixedHeight(1)
        bottom_sep.setStyleSheet(
            f"background-color: {Colors.BORDER_SUBTLE}; max-height: 1px;"
        )
        layout.addWidget(bottom_sep)
        layout.addSpacing(10)

        # Footer pages (Settings)
        for page_id, icon, label in self.FOOTER_PAGES:
            btn = self._make_nav_button(page_id, icon, label)
            self.button_group.addButton(btn)
            self.buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addSpacing(14)

        # Status row
        status_row = QHBoxLayout()
        status_row.setContentsMargins(20, 0, 20, 0)
        status_row.setSpacing(8)

        status_dot = QLabel("●")
        status_dot.setStyleSheet(
            f"color: {Colors.ACCENT_SUCCESS}; background: transparent; font-size: 10px;"
        )
        status_row.addWidget(status_dot)

        status_text = QLabel("Offline · Local")
        status_text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; "
            f"font-size: 11px; font-weight: 500;"
        )
        status_row.addWidget(status_text)
        status_row.addStretch()

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 10px; font-weight: 600;"
        )
        status_row.addWidget(version_label)
        layout.addLayout(status_row)

        # Default selection
        if "dashboard" in self.buttons:
            self.buttons["dashboard"].setChecked(True)

    def _make_nav_button(self, page_id: str, icon: str, label: str) -> QPushButton:
        btn = QPushButton(f"  {icon}    {label}")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda _checked=False, pid=page_id: self.page_changed.emit(pid))
        return btn

    def set_active(self, page_id: str) -> None:
        if page_id in self.buttons:
            self.buttons[page_id].setChecked(True)
