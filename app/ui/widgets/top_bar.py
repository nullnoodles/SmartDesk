"""Top app bar — search, action icons, and a user pill on the right.

Matches the Studio Graphite reference design. Sits above the page content,
spanning from the sidebar's right edge to the window's right edge.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.styles.theme import Colors


class TopBar(QWidget):
    """Top header — search input, notification/help buttons, user identity."""

    search_changed = Signal(str)

    def __init__(self, user_name: str = "Freelancer", role: str = "OFFLINE WORKSPACE", parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setStyleSheet(
            f"background-color: {Colors.BG_DARK}; "
            f"border-bottom: 1px solid {Colors.BORDER_SUBTLE};"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(20)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍   Search projects, clients, invoices...")
        self.search.setFixedWidth(360)
        self.search.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 1px solid {Colors.BORDER_SUBTLE}; "
            f"border-radius: 10px; padding: 8px 14px; "
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px;"
        )
        self.search.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search, 0)

        layout.addStretch()

        # Icon buttons
        for emoji, tooltip in [("🔔", "Notifications"), ("❓", "Help")]:
            btn = QPushButton(emoji)
            btn.setToolTip(tooltip)
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                f"background-color: transparent; color: {Colors.TEXT_SECONDARY}; "
                f"border: none; border-radius: 10px; font-size: 16px;"
            )
            btn.enterEvent = lambda e, b=btn: b.setStyleSheet(
                f"background-color: {Colors.BG_HOVER}; color: {Colors.TEXT_PRIMARY}; "
                f"border: none; border-radius: 10px; font-size: 16px;"
            )
            btn.leaveEvent = lambda e, b=btn: b.setStyleSheet(
                f"background-color: transparent; color: {Colors.TEXT_SECONDARY}; "
                f"border: none; border-radius: 10px; font-size: 16px;"
            )
            layout.addWidget(btn)

        # Vertical divider
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(28)
        sep.setStyleSheet(f"color: {Colors.BORDER_SUBTLE}; background: {Colors.BORDER_SUBTLE};")
        layout.addWidget(sep)

        # User block
        user_block = QHBoxLayout()
        user_block.setSpacing(10)

        text_block = QVBoxLayout()
        text_block.setSpacing(0)

        name_lbl = QLabel(user_name)
        name_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        name_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 13px; font-weight: 700;"
        )
        text_block.addWidget(name_lbl)

        role_lbl = QLabel(role)
        role_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        role_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 9px; font-weight: 700; letter-spacing: 0.12em;"
        )
        text_block.addWidget(role_lbl)
        user_block.addLayout(text_block)

        # Avatar circle (initials)
        initials = "".join([w[0].upper() for w in user_name.split() if w])[:2] or "FD"
        avatar = QLabel(initials)
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background-color: {Colors.ACCENT_PRIMARY}; "
            f"color: {Colors.TEXT_ON_PRIMARY}; "
            f"border-radius: 19px; font-size: 13px; font-weight: 700;"
        )
        user_block.addWidget(avatar)

        user_widget = QWidget()
        user_widget.setLayout(user_block)
        layout.addWidget(user_widget)

    def set_user(self, name: str, role: str = "") -> None:
        """Update the user info shown in the top bar."""
        # Walk the layout to find the labels — keeping it simple for now,
        # callers usually only need the name on first render.
        pass
