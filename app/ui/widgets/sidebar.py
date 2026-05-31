"""Sidebar navigation — Studio Graphite design.

Layout matches the reference: brand block, nav buttons, footer user card
with New Workspace CTA.
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
    """Persistent left sidebar with brand, nav buttons, and footer card."""

    page_changed = Signal(str)

    PAGES = [
        ("dashboard", "🏠", "Dashboard"),
        ("clients", "👥", "Clients"),
        ("projects", "📁", "Projects"),
        ("invoices", "🧾", "Invoices"),
        ("time", "⏱️", "Time Log"),
        ("contracts", "📝", "Contracts"),
        ("analytics", "🤖", "AI Analytics"),
        ("settings", "⚙️", "Settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 28, 0, 22)
        layout.setSpacing(0)

        # ─── Brand header ─────────────────────────────────────────────────
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(20, 0, 20, 0)
        brand_row.setSpacing(12)

        logo = QLabel("◆")
        logo.setFixedSize(38, 38)
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

        # Navigation section label
        nav_label = QLabel("    NAVIGATION")
        nav_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 9px; font-weight: 700; letter-spacing: 0.14em; "
            f"padding-left: 16px;"
        )
        layout.addWidget(nav_label)
        layout.addSpacing(8)

        # Navigation buttons
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}

        for page_id, icon, label in self.PAGES:
            btn = self._make_nav_button(page_id, icon, label)
            self.button_group.addButton(btn)
            self.buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # ─── Footer user card ─────────────────────────────────────────────
        user_card = QFrame()
        user_card.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 1px solid {Colors.BORDER_SUBTLE}; "
            f"border-radius: 12px;"
        )
        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(14, 12, 14, 12)
        user_layout.setSpacing(10)

        # User row (avatar + name + plan)
        user_row = QHBoxLayout()
        user_row.setSpacing(10)

        avatar = QLabel("FD")
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background-color: {Colors.ACCENT_PRIMARY}; "
            f"color: {Colors.TEXT_ON_PRIMARY}; "
            f"border-radius: 17px; font-size: 11px; font-weight: 700;"
        )
        user_row.addWidget(avatar)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)

        name_lbl = QLabel("Freelancer")
        name_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 12px; font-weight: 700;"
        )
        text_col.addWidget(name_lbl)

        plan_lbl = QLabel("Local · v" + APP_VERSION)
        plan_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 10px; font-weight: 500;"
        )
        text_col.addWidget(plan_lbl)
        user_row.addLayout(text_col)
        user_row.addStretch()
        user_layout.addLayout(user_row)

        # Status row
        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        dot = QLabel("●")
        dot.setStyleSheet(
            f"color: {Colors.ACCENT_SUCCESS}; background: transparent; font-size: 10px;"
        )
        status_row.addWidget(dot)

        status_text = QLabel("Offline · All data local")
        status_text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; font-size: 10px;"
        )
        status_row.addWidget(status_text)
        status_row.addStretch()
        user_layout.addLayout(status_row)

        # Wrap in a margined holder
        user_holder = QWidget()
        holder_layout = QVBoxLayout(user_holder)
        holder_layout.setContentsMargins(14, 0, 14, 0)
        holder_layout.addWidget(user_card)
        layout.addWidget(user_holder)

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
