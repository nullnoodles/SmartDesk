"""Settings page — Studio Graphite design with two-column local sub-navigation.

Allows configuration of profile, workspace, notifications, integrations (SMTP),
billing (mock), data backup/restore, and destructive Danger Zone actions.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPainterPath
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_DESCRIPTION, APP_NAME, APP_VERSION
from app.core.backup_service import BackupService
from app.core.csv_exporter import CSVExporter
from app.core.settings_service import BusinessProfile, SettingsService
from app.core.signals import emit_data_changed
from app.data.database import Database
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton, AnimatedCard


def _load_svg_icon(name: str, size: int = 18, color: str = "#9a9cb8") -> QIcon:
    """Load an SVG icon from assets/icons, render/tint it, and return QIcon."""
    from app.config import ASSETS_DIR
    
    svg_path = ASSETS_DIR / "icons" / f"{name}.svg"
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    if not svg_path.exists():
        return QIcon()

    renderer = QSvgRenderer(str(svg_path))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)


class CircularAvatarLabel(QLabel):
    """Circular profile image renderer with anti-aliased clipping and border."""

    def __init__(self, size: int = 80, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setStyleSheet(
            f"border-radius: {size//2}px; border: 1px solid #454652; "
            f"background-color: #1e1f2a;"
        )
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = None

    def setPixmap(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self.update()

    def clear(self) -> None:
        self._pixmap = None
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw circular background
        painter.setBrush(QColor("#1e1f2a"))
        painter.setPen(QColor("#454652"))
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)

        if self._pixmap and not self._pixmap.isNull():
            path = QPainterPath()
            path.addEllipse(0, 0, self.width(), self.height())
            painter.setClipPath(path)
            
            # Scale and center pixmap
            scaled = self._pixmap.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # Fallback initials or icon
            painter.setPen(QColor(Colors.TEXT_MUTED))
            font = painter.font()
            font.setPointSize(self.width() // 3)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "AM")
        painter.end()


class SettingsPage(QWidget):
    """Modern Settings page with two-column local sidebar sub-navigation."""

    def __init__(self, db: Database):
        super().__init__()
        self.setObjectName("settings_page")
        self.db = db
        self.settings = SettingsService(db)
        self.backup = BackupService(db)
        self.csv = CSVExporter(db)

        # Load notification & email services
        from app.core.notification_service import NotificationService
        self.notification_service = NotificationService(db)

        from app.core.email_service import EmailService
        self.email_service = EmailService(db)

        from app.core.receipt_ocr import ReceiptOCR
        self.ocr = ReceiptOCR()

        self._logo_path = ""
        self._receipt_path = ""

        # Outer layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # Header Title
        from app.ui.widgets.page_header import PageHeader
        self.header = PageHeader(
            title="Settings",
            subtitle="Configure profile info, workspace rules, notifications, and SMTP integrations.",
        )
        main_layout.addWidget(self.header)

        # Columns container
        columns_widget = QWidget()
        columns_layout = QHBoxLayout(columns_widget)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(32)

        # ─── Left Column: Sub-navigation menu (width 240px) ─────────────────
        self.sidebar_nav = self._build_sidebar()
        columns_layout.addWidget(self.sidebar_nav)

        # ─── Right Column: Stacked panels (flex-1) ─────────────────────────
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Build individual panels
        self.profile_panel = self._build_profile_panel()
        self.workspace_panel = self._build_workspace_panel()
        self.notifications_panel = self._build_notifications_panel()
        self.billing_panel = self._build_billing_panel()
        self.integrations_panel = self._build_integrations_panel()
        self.danger_panel = self._build_danger_panel()

        # Add to stack with scrollable wrappers
        self.stacked_widget.addWidget(self._wrap_in_scroll(self.profile_panel))
        self.stacked_widget.addWidget(self._wrap_in_scroll(self.workspace_panel))
        self.stacked_widget.addWidget(self._wrap_in_scroll(self.notifications_panel))
        self.stacked_widget.addWidget(self._wrap_in_scroll(self.billing_panel))
        self.stacked_widget.addWidget(self._wrap_in_scroll(self.integrations_panel))
        self.stacked_widget.addWidget(self._wrap_in_scroll(self.danger_panel))

        columns_layout.addWidget(self.stacked_widget, 1)
        main_layout.addWidget(columns_widget, 1)

        # Trigger load / refresh
        self.refresh()

    def _wrap_in_scroll(self, widget: QWidget) -> QScrollArea:
        """Wrap a widget inside a clean, scrollable view."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(widget)
        return scroll

    def _build_sidebar(self) -> QWidget:
        """Build the left sub-navigation sidebar container."""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Button Group for navigation items
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        menu_items = [
            ("Profile & Account", "person_add", 0, False),
            ("Workspace", "settings", 1, False),
            ("Notifications", "notifications", 2, False),
            ("Billing & Plan", "account_balance_wallet", 3, False),
            ("Integrations", "rocket_launch", 4, False),
            (None, None, None, True),  # Separator
            ("Danger Zone", "delete", 5, True),
        ]

        self.nav_buttons: list[QPushButton] = []
        for label, icon_name, index, is_destructive in menu_items:
            if label is None:
                # Add separator line
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setFrameShadow(QFrame.Sunken)
                sep.setStyleSheet("background-color: rgba(69, 70, 82, 0.3); max-height: 1px; margin: 8px 0;")
                layout.addWidget(sep)
                continue

            btn = QPushButton(f"   {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFixedHeight(42)

            # Icon loading
            icon_color = "#e87c8a" if is_destructive else Colors.TEXT_SECONDARY
            icon = _load_svg_icon(icon_name, size=18, color=icon_color)
            btn.setIcon(icon)
            btn.setIconSize(btn.iconSize())

            if is_destructive:
                btn.setObjectName("danger_nav")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {Colors.ACCENT_DANGER};
                        border: 1px solid transparent;
                        border-radius: 8px;
                        padding: 10px 16px;
                        text-align: left;
                        font-size: 14px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(232, 124, 138, 0.08);
                        color: {Colors.ACCENT_DANGER};
                    }}
                    QPushButton:checked {{
                        background-color: rgba(232, 124, 138, 0.12);
                        color: {Colors.ACCENT_DANGER};
                        border: 1px solid rgba(232, 124, 138, 0.25);
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {Colors.TEXT_SECONDARY};
                        border: 1px solid transparent;
                        border-radius: 8px;
                        padding: 10px 16px;
                        text-align: left;
                        font-size: 14px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(51, 52, 64, 0.25);
                        color: {Colors.TEXT_PRIMARY};
                    }}
                    QPushButton:checked {{
                        background-color: rgba(124, 138, 244, 0.1);
                        color: {Colors.ACCENT_PRIMARY_LIGHT};
                        border: 1px solid {Colors.BORDER_SUBTLE};
                    }}
                """)

            btn.clicked.connect(lambda checked=False, idx=index: self.stacked_widget.setCurrentIndex(idx))
            self.nav_group.addButton(btn)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Set first item active by default
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

        return sidebar

    # ─── Panel 1: Profile & Account ─────────────────────────────────────────
    def _build_profile_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        card = AnimatedCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(20)

        title = QLabel("Profile Information")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        card_layout.addWidget(title)

        # Avatar Upload Cluster
        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(16)

        self.avatar_preview = CircularAvatarLabel(size=80)
        avatar_row.addWidget(self.avatar_preview)

        avatar_btn_col = QVBoxLayout()
        avatar_btn_col.setSpacing(8)

        avatar_btn_row = QHBoxLayout()
        self.upload_avatar_btn = AnimatedButton("Upload New", accent=Colors.ACCENT_PRIMARY)
        self.upload_avatar_btn.clicked.connect(self._choose_logo)
        self.remove_avatar_btn = QPushButton("Remove")
        self.remove_avatar_btn.setProperty("accent", "ghost")
        self.remove_avatar_btn.setFixedWidth(100)
        self.remove_avatar_btn.clicked.connect(self._clear_logo)

        avatar_btn_row.addWidget(self.upload_avatar_btn)
        avatar_btn_row.addWidget(self.remove_avatar_btn)
        avatar_btn_row.addStretch()
        avatar_btn_col.addLayout(avatar_btn_row)

        self.avatar_path_label = QLabel("No image selected")
        self.avatar_path_label.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent;")
        avatar_btn_col.addWidget(self.avatar_path_label)

        avatar_row.addLayout(avatar_btn_col)
        avatar_row.addStretch()
        card_layout.addLayout(avatar_row)

        # Grid form fields
        grid = QGridLayout()
        grid.setSpacing(16)

        # Helper to create styled forms
        def add_field(label_text: str, row: int, col: int) -> QLineEdit:
            vbox = QVBoxLayout()
            vbox.setSpacing(6)
            lbl = QLabel(label_text.upper())
            lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {Colors.TEXT_SECONDARY}; text-transform: uppercase; letter-spacing: 0.05em;")
            inp = QLineEdit()
            vbox.addWidget(lbl)
            vbox.addWidget(inp)
            grid.addLayout(vbox, row, col)
            return inp

        self.name_input = add_field("Full Name", 0, 0)
        self.email_input = add_field("Email Address", 0, 1)
        self.phone_input = add_field("Phone Number", 1, 0)
        self.role_input = add_field("Role", 1, 1)

        card_layout.addLayout(grid)

        # Bio field (textarea)
        bio_vbox = QVBoxLayout()
        bio_vbox.setSpacing(6)
        bio_lbl = QLabel("BIO")
        bio_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {Colors.TEXT_SECONDARY}; text-transform: uppercase; letter-spacing: 0.05em;")
        self.bio_input = QTextEdit()
        self.bio_input.setMaximumHeight(80)
        bio_vbox.addWidget(bio_lbl)
        bio_vbox.addWidget(self.bio_input)
        card_layout.addLayout(bio_vbox)

        # Save changes button aligned to right
        save_row = QHBoxLayout()
        save_row.addStretch()
        self.save_profile_btn = AnimatedButton("Save Changes", accent=Colors.ACCENT_PRIMARY)
        self.save_profile_btn.setIcon(_load_svg_icon("task_alt", size=18, color=Colors.TEXT_ON_PRIMARY))
        self.save_profile_btn.clicked.connect(self._save_profile)
        save_row.addWidget(self.save_profile_btn)
        card_layout.addLayout(save_row)

        layout.addWidget(card)
        layout.addStretch()
        return widget

    # ─── Panel 2: Workspace Panel ───────────────────────────────────────────
    def _build_workspace_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Card 1: Workspace / Invoice Settings
        card_work = AnimatedCard()
        card_work.setMinimumHeight(150)
        card_work.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        work_layout = QVBoxLayout(card_work)
        work_layout.setContentsMargins(24, 24, 24, 24)
        work_layout.setSpacing(16)

        title_work = QLabel("Workspace Settings")
        title_work.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        work_layout.addWidget(title_work)

        form_work = QFormLayout()
        form_work.setSpacing(12)

        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter your billing address...")
        self.address_input.setMaximumHeight(60)

        self.gstin_input = QLineEdit()
        self.gstin_input.setPlaceholderText("e.g. 22AAAAA0000A1Z5 (optional)")

        self.due_days_input = QSpinBox()
        self.due_days_input.setRange(1, 90)
        self.due_days_input.setSuffix(" days")

        form_work.addRow("Billing Address", self.address_input)
        form_work.addRow("GSTIN", self.gstin_input)
        form_work.addRow("Payment Due Period", self.due_days_input)
        work_layout.addLayout(form_work)

        # Card 2: UPI details
        title_upi = QLabel("UPI Payments (India)")
        title_upi.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; margin-top: 10px; background: transparent;")
        work_layout.addWidget(title_upi)

        form_upi = QFormLayout()
        form_upi.setSpacing(12)
        self.upi_id_input = QLineEdit()
        self.upi_id_input.setPlaceholderText("yourname@upi")
        self.upi_name_input = QLineEdit()
        self.upi_name_input.setPlaceholderText("Payee display name")
        form_upi.addRow("UPI ID", self.upi_id_input)
        form_upi.addRow("Display Name", self.upi_name_input)
        work_layout.addLayout(form_upi)

        save_work_btn = AnimatedButton("Save Workspace Details", accent=Colors.ACCENT_PRIMARY)
        save_work_btn.clicked.connect(self._save_workspace)
        work_layout.addWidget(save_work_btn)

        layout.addWidget(card_work)

        # Card 3: Data Management & Backups
        card_backup = AnimatedCard()
        card_backup.setMinimumHeight(150)
        card_backup.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        backup_layout = QVBoxLayout(card_backup)
        backup_layout.setContentsMargins(24, 24, 24, 24)
        backup_layout.setSpacing(14)

        title_backup = QLabel("Backup & Export")
        title_backup.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        backup_layout.addWidget(title_backup)

        desc_backup = QLabel("Create zip archives of database and invoices, restore previous snapshots, or export table data directly to CSV.")
        desc_backup.setWordWrap(True)
        desc_backup.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        backup_layout.addWidget(desc_backup)

        backup_btns = QHBoxLayout()
        self.btn_backup = AnimatedButton("Create Backup", accent=Colors.ACCENT_INFO)
        self.btn_backup.clicked.connect(self._create_backup)
        self.btn_restore = AnimatedButton("Restore from Backup", accent=Colors.ACCENT_WARNING)
        self.btn_restore.clicked.connect(self._restore_backup)
        backup_btns.addWidget(self.btn_backup)
        backup_btns.addWidget(self.btn_restore)
        backup_btns.addStretch()
        backup_layout.addLayout(backup_btns)

        csv_btns = QHBoxLayout()
        for lbl, k in [("Clients", "clients"), ("Projects", "projects"), ("Invoices", "invoices")]:
            btn = QPushButton(f"Export {lbl}")
            btn.setProperty("accent", "ghost")
            btn.clicked.connect(lambda _=False, kind=k: self._export_csv(kind))
            csv_btns.addWidget(btn)
        csv_btns.addStretch()
        backup_layout.addLayout(csv_btns)

        layout.addWidget(card_backup)

        # Card 4: Receipt OCR Scanner
        card_ocr = AnimatedCard()
        card_ocr.setMinimumHeight(240)
        card_ocr.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ocr_layout = QVBoxLayout(card_ocr)
        ocr_layout.setContentsMargins(24, 24, 24, 24)
        ocr_layout.setSpacing(12)

        title_ocr = QLabel("Receipt OCR Scanner")
        title_ocr.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        ocr_layout.addWidget(title_ocr)

        status_txt = "✓ Tesseract OCR Detected" if self.ocr.is_available() else "⚠️ Tesseract Not Found (Receipt scanning disabled)"
        ocr_status = QLabel(status_txt)
        ocr_status.setStyleSheet(
            f"font-size: 12px; color: {Colors.ACCENT_SUCCESS if self.ocr.is_available() else Colors.ACCENT_WARNING}; "
            f"font-weight: 500; background: transparent;"
        )
        ocr_layout.addWidget(ocr_status)

        choose_ocr_row = QHBoxLayout()
        self.receipt_path_label = QLabel("No image selected")
        self.receipt_path_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent;")
        btn_choose_rec = QPushButton("Choose Image...")
        btn_choose_rec.setProperty("accent", "ghost")
        btn_choose_rec.clicked.connect(self._choose_receipt)

        btn_run_ocr = AnimatedButton("Extract Text", accent=Colors.ACCENT_PRIMARY)
        btn_run_ocr.clicked.connect(self._run_receipt_ocr)

        choose_ocr_row.addWidget(self.receipt_path_label, 1)
        choose_ocr_row.addWidget(btn_choose_rec)
        choose_ocr_row.addWidget(btn_run_ocr)
        ocr_layout.addLayout(choose_ocr_row)

        self.receipt_summary = QLabel("Extracted data will appear here...")
        self.receipt_summary.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        ocr_layout.addWidget(self.receipt_summary)

        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        self.receipt_text.setPlaceholderText("OCR Output...")
        self.receipt_text.setMaximumHeight(100)
        ocr_layout.addWidget(self.receipt_text)

        layout.addWidget(card_ocr)

        # Card 5: About SmartDesk
        card_about = AnimatedCard()
        card_about.setMinimumHeight(150)
        card_about.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        about_layout = QVBoxLayout(card_about)
        about_layout.setContentsMargins(24, 24, 24, 24)
        about_layout.setSpacing(8)

        lbl_app = QLabel(f"{APP_NAME} — v{APP_VERSION}")
        lbl_app.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.ACCENT_PRIMARY_LIGHT}; background: transparent;")
        about_layout.addWidget(lbl_app)

        lbl_desc = QLabel(APP_DESCRIPTION)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        about_layout.addWidget(lbl_desc)

        lbl_license = QLabel("Built offline with PySide6, SQLite, and scikit-learn. MIT License.")
        lbl_license.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent;")
        about_layout.addWidget(lbl_license)

        layout.addWidget(card_about)
        return widget

    # ─── Panel 3: Notifications Panel ───────────────────────────────────────
    def _build_notifications_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Card 1: Settings
        card_settings = AnimatedCard()
        card_settings.setMinimumHeight(140)
        card_settings.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sett_layout = QVBoxLayout(card_settings)
        sett_layout.setContentsMargins(24, 24, 24, 24)
        sett_layout.setSpacing(14)

        title = QLabel("Notification Preferences")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        sett_layout.addWidget(title)

        self.notifications_enabled = QCheckBox("Enable Notifications")
        self.desktop_notifications = QCheckBox("Desktop Notifications (Pop-ups)")
        self.email_reminders = QCheckBox("Email Reminders")

        sett_layout.addWidget(self.notifications_enabled)
        sett_layout.addWidget(self.desktop_notifications)
        sett_layout.addWidget(self.email_reminders)
        layout.addWidget(card_settings)

        # Card 2: Frequency & Thresholds
        card_freq = AnimatedCard()
        card_freq.setMinimumHeight(120)
        card_freq.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        freq_layout = QFormLayout(card_freq)
        freq_layout.setContentsMargins(24, 24, 24, 24)
        freq_layout.setSpacing(12)

        self.reminder_frequency = QComboBox()
        self.reminder_frequency.addItems(["Daily", "Weekly"])
        
        self.days_before_due = QSpinBox()
        self.days_before_due.setRange(1, 30)
        self.days_before_due.setSuffix(" days")

        freq_layout.addRow("Check Frequency", self.reminder_frequency)
        freq_layout.addRow("Remind Before Deadline", self.days_before_due)
        layout.addWidget(card_freq)

        # Card 3: Types
        card_types = AnimatedCard()
        card_types.setMinimumHeight(140)
        card_types.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        types_layout = QVBoxLayout(card_types)
        types_layout.setContentsMargins(24, 24, 24, 24)
        types_layout.setSpacing(12)

        title_types = QLabel("Notification Types")
        title_types.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        types_layout.addWidget(title_types)

        self.notify_overdue = QCheckBox("Overdue Invoices")
        self.notify_deadlines = QCheckBox("Upcoming Project Deadlines")
        self.notify_payments = QCheckBox("Payments Received")

        types_layout.addWidget(self.notify_overdue)
        types_layout.addWidget(self.notify_deadlines)
        types_layout.addWidget(self.notify_payments)
        layout.addWidget(card_types)

        # Card 4: Status / Test trigger
        card_status = AnimatedCard()
        card_status.setMinimumHeight(140)
        card_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        status_layout = QVBoxLayout(card_status)
        status_layout.setContentsMargins(24, 24, 24, 24)
        status_layout.setSpacing(12)

        title_status = QLabel("System Status")
        title_status.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        status_layout.addWidget(title_status)

        self.notification_status_label = QLabel("Loading status...")
        self.notification_status_label.setWordWrap(True)
        self.notification_status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent; font-size: 13px;")
        status_layout.addWidget(self.notification_status_label)

        btn_row = QHBoxLayout()
        test_btn = QPushButton("Send Test Alert")
        test_btn.setProperty("accent", "ghost")
        test_btn.clicked.connect(self._send_test_notification)

        run_check_btn = AnimatedButton("Check Now", accent=Colors.ACCENT_INFO)
        run_check_btn.clicked.connect(self._check_notifications_now)

        btn_row.addWidget(test_btn)
        btn_row.addWidget(run_check_btn)
        btn_row.addStretch()
        status_layout.addLayout(btn_row)
        layout.addWidget(card_status)

        # Save notifications button
        save_btn = AnimatedButton("Save Notification Preferences", accent=Colors.ACCENT_PRIMARY)
        save_btn.clicked.connect(self._save_notification_settings)
        layout.addWidget(save_btn)
        layout.addStretch()
        return widget

    # ─── Panel 4: Billing & Plan Panel ───────────────────────────────────────
    def _build_billing_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header Title
        title = QLabel("Subscription Plan")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        # Plan 1: Active Local Free Plan
        card_local = AnimatedCard()
        card_local.setMinimumHeight(180)
        card_local.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card_local.setStyleSheet(f"""
            .AnimatedCard {{
                background-color: {Colors.BG_CARD};
                border: 1.5px solid {Colors.ACCENT_SUCCESS};
                border-radius: 14px;
                padding: 24px;
            }}
        """)
        local_layout = QVBoxLayout(card_local)
        local_layout.setContentsMargins(24, 24, 24, 24)
        local_layout.setSpacing(12)

        top_row = QHBoxLayout()
        lbl_local_title = QLabel("SmartDesk Local")
        lbl_local_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        badge = QLabel("✓ ACTIVE LOCAL LICENSE")
        badge.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: #ffffff; "
            f"background-color: {Colors.ACCENT_SUCCESS}; border-radius: 4px; padding: 2px 8px;"
        )
        top_row.addWidget(lbl_local_title)
        top_row.addWidget(badge)
        top_row.addStretch()

        price_lbl = QLabel("₹0 / lifetime")
        price_lbl.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.ACCENT_SUCCESS}; background: transparent;")
        top_row.addWidget(price_lbl)
        local_layout.addLayout(top_row)

        desc = QLabel("Offline-first workspace. Your client profiles, projects, invoices, and analytics data stay secure on this local machine.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        local_layout.addWidget(desc)

        features = [
            "Full SQLite database locally encrypted via OS user account permissions.",
            "Unlimited client profiles, invoice drafts, and project tasks.",
            "Complete local backup exports (.zip) and CSV spreadsheet dumps.",
            "Integrated Tesseract OCR scanner to digitize expense receipts offline.",
        ]
        for f in features:
            flbl = QLabel(f"•  {f}")
            flbl.setWordWrap(True)
            flbl.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_PRIMARY}; background: transparent;")
            local_layout.addWidget(flbl)

        layout.addWidget(card_local)

        # Plan 2: Coming Soon Cloud Upgrade
        card_cloud = AnimatedCard()
        card_cloud.setMinimumHeight(180)
        card_cloud.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card_cloud.setStyleSheet(f"""
            .AnimatedCard {{
                background-color: {Colors.BG_CARD};
                border: 1px dashed {Colors.BORDER_SUBTLE};
                border-radius: 14px;
                padding: 24px;
                opacity: 0.8;
            }}
        """)
        cloud_layout = QVBoxLayout(card_cloud)
        cloud_layout.setContentsMargins(24, 24, 24, 24)
        cloud_layout.setSpacing(12)

        ctop = QHBoxLayout()
        lbl_cloud_title = QLabel("SmartDesk Cloud")
        lbl_cloud_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        cbadge = QLabel("COMING SOON")
        cbadge.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: #3d2a0a; "
            f"background-color: {Colors.ACCENT_WARNING}; border-radius: 4px; padding: 2px 8px;"
        )
        ctop.addWidget(lbl_cloud_title)
        ctop.addWidget(cbadge)
        ctop.addStretch()

        cprice = QLabel("₹499 / mo")
        cprice.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        ctop.addWidget(cprice)
        cloud_layout.addLayout(ctop)

        cdesc = QLabel("Synchronize your workspace across multiple computers, run secure cloud backups, and collaborate with other freelancers.")
        cdesc.setWordWrap(True)
        cdesc.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_MUTED}; background: transparent;")
        cloud_layout.addWidget(cdesc)

        cfeatures = [
            "Secure real-time cloud database synchronization.",
            "Automatic daily off-site encrypted data backups.",
            "Payment gateway integrations (Stripe, Razorpay) with client checkout links.",
            "Automated SMTP client invoicing directly from cloud nodes.",
        ]
        for f in cfeatures:
            flbl = QLabel(f"•  {f}")
            flbl.setWordWrap(True)
            flbl.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_MUTED}; background: transparent;")
            cloud_layout.addWidget(flbl)

        btn_notify = QPushButton("Notify Me on Launch")
        btn_notify.setEnabled(False)
        btn_notify.setStyleSheet(f"background-color: {Colors.BG_ELEVATED}; color: {Colors.TEXT_MUTED}; border-radius: 10px; padding: 10px; font-size: 13px;")
        cloud_layout.addWidget(btn_notify)

        layout.addWidget(card_cloud)
        layout.addStretch()
        return widget

    # ─── Panel 5: Integrations Panel ─────────────────────────────────────────
    def _build_integrations_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header Title
        title = QLabel("Connected Systems")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        # Grid of connected APIs (3rd party placeholders)
        grid = QGridLayout()
        grid.setSpacing(16)

        integrations_data = [
            ("Google Calendar", "Sync deadlines with Google Calendar.", "rocket_launch", 0, 0),
            ("Razorpay Checkout", "Embed instant payment links on bills.", "payments", 0, 1),
            ("Slack Integration", "Post workspace status checks to channels.", "notifications", 1, 0),
            ("Dropbox Backups", "Auto-dump backup zip archives to folders.", "folder_open", 1, 1),
        ]

        for name, desc, icon_name, r, c in integrations_data:
            icard = AnimatedCard()
            icard.setMinimumHeight(130)
            icard.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            ilay = QVBoxLayout(icard)
            ilay.setContentsMargins(16, 16, 16, 16)
            ilay.setSpacing(8)

            trow = QHBoxLayout()
            iname = QLabel(name)
            iname.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
            
            # Simple colored dot indicating disconnect
            dot = QLabel("● Disconnected")
            dot.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED}; background: transparent;")
            trow.addWidget(iname)
            trow.addStretch()
            trow.addWidget(dot)
            ilay.addLayout(trow)

            idesc = QLabel(desc)
            idesc.setWordWrap(True)
            idesc.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
            ilay.addWidget(idesc)

            icon = _load_svg_icon(icon_name, size=16, color=Colors.TEXT_MUTED)
            ibtn = QPushButton("  Connect")
            ibtn.setIcon(icon)
            ibtn.setProperty("accent", "ghost")
            ibtn.setFixedHeight(30)
            ibtn.setCursor(Qt.PointingHandCursor)
            ibtn.clicked.connect(lambda _=False, n=name: QMessageBox.information(self, "Integrations", f"Connecting to {n} is a cloud subscription feature."))
            ilay.addWidget(ibtn)

            grid.addWidget(icard, r, c)

        layout.addLayout(grid)

        # SMTP card (working backend!)
        card_smtp = AnimatedCard()
        card_smtp.setMinimumHeight(280)
        card_smtp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        smtp_layout = QVBoxLayout(card_smtp)
        smtp_layout.setContentsMargins(24, 24, 24, 24)
        smtp_layout.setSpacing(16)

        title_smtp = QLabel("Email (SMTP) Settings")
        title_smtp.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        smtp_layout.addWidget(title_smtp)

        sub_smtp = QLabel("Configure custom SMTP details to auto-mail invoices and payment reminders to clients.")
        sub_smtp.setWordWrap(True)
        sub_smtp.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        smtp_layout.addWidget(sub_smtp)

        form_smtp = QFormLayout()
        form_smtp.setSpacing(12)

        self.smtp_host = QLineEdit()
        self.smtp_host.setPlaceholderText("e.g. smtp.gmail.com")

        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(587)

        self.smtp_username = QLineEdit()
        self.smtp_username.setPlaceholderText("smtp_username@example.com")

        self.smtp_password = QLineEdit()
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.smtp_password.setPlaceholderText("Password or client App Token")

        self.smtp_from = QLineEdit()
        self.smtp_from.setPlaceholderText("sender_email@example.com")

        self.smtp_use_tls = QCheckBox("Use STARTTLS (default 587)")
        self.smtp_use_tls.setChecked(True)

        form_smtp.addRow("SMTP Server Host", self.smtp_host)
        form_smtp.addRow("Port Number", self.smtp_port)
        form_smtp.addRow("Username", self.smtp_username)
        form_smtp.addRow("Password", self.smtp_password)
        form_smtp.addRow("Sender Address", self.smtp_from)
        form_smtp.addRow("", self.smtp_use_tls)
        smtp_layout.addLayout(form_smtp)

        smtp_btns = QHBoxLayout()
        save_smtp_btn = AnimatedButton("Save SMTP Settings", accent=Colors.ACCENT_PRIMARY)
        save_smtp_btn.clicked.connect(self._save_smtp)
        
        test_email_btn = QPushButton("Send Test Email")
        test_email_btn.setProperty("accent", "ghost")
        test_email_btn.clicked.connect(self._send_test_email)

        smtp_btns.addWidget(save_smtp_btn)
        smtp_btns.addWidget(test_email_btn)
        smtp_btns.addStretch()
        smtp_layout.addLayout(smtp_btns)

        layout.addWidget(card_smtp)
        layout.addStretch()
        return widget

    # ─── Panel 6: Danger Zone Panel ──────────────────────────────────────────
    def _build_danger_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        card = AnimatedCard()
        card.setMinimumHeight(240)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setStyleSheet(f"""
            .AnimatedCard {{
                background-color: {Colors.BG_CARD};
                border: 1.5px solid {Colors.ACCENT_DANGER};
                border-radius: 14px;
                padding: 24px;
            }}
        """)
        danger_layout = QVBoxLayout(card)
        danger_layout.setContentsMargins(24, 24, 24, 24)
        danger_layout.setSpacing(16)

        title = QLabel("Danger Zone")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.ACCENT_DANGER}; background: transparent;")
        danger_layout.addWidget(title)

        desc = QLabel("These operations are destructive and modify or delete workspace parameters, settings keys, and transactional logs. Be careful.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        danger_layout.addWidget(desc)

        # Destructive buttons column
        btns_col = QVBoxLayout()
        btns_col.setSpacing(12)

        # Button 1: Reset Preferences
        row1 = QHBoxLayout()
        lbl1 = QLabel("Reset settings keys (SMTP configurations and UI preferences) to defaults. Data is safe.")
        lbl1.setWordWrap(True)
        lbl1.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        btn1 = QPushButton("Reset Preferences")
        btn1.setProperty("accent", "danger")
        btn1.setFixedWidth(160)
        btn1.clicked.connect(self._reset_preferences)
        row1.addWidget(lbl1, 1)
        row1.addWidget(btn1)
        btns_col.addLayout(row1)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: rgba(232, 124, 138, 0.2); max-height: 1px;")
        btns_col.addWidget(sep)

        # Button 2: Clear Workspace Data
        row2 = QHBoxLayout()
        lbl2 = QLabel("Delete all client records, invoice lists, payment registries, time log sheets, and active contracts. Settings are safe.")
        lbl2.setWordWrap(True)
        lbl2.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        btn2 = QPushButton("Clear All Data")
        btn2.setProperty("accent", "danger")
        btn2.setFixedWidth(160)
        btn2.clicked.connect(self._clear_workspace_data)
        row2.addWidget(lbl2, 1)
        row2.addWidget(btn2)
        btns_col.addLayout(row2)

        # Separator line
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background-color: rgba(232, 124, 138, 0.2); max-height: 1px;")
        btns_col.addWidget(sep2)

        # Button 3: Reset Database (Destructive)
        row3 = QHBoxLayout()
        lbl3 = QLabel("Drop all local SQLite tables and run initial database scripts again. Wipes all settings and data.")
        lbl3.setWordWrap(True)
        lbl3.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        btn3 = QPushButton("Reset Database")
        btn3.setProperty("accent", "danger")
        btn3.setFixedWidth(160)
        btn3.clicked.connect(self._reset_database)
        row3.addWidget(lbl3, 1)
        row3.addWidget(btn3)
        btns_col.addLayout(row3)

        danger_layout.addLayout(btns_col)
        layout.addWidget(card)
        layout.addStretch()
        return widget

    # ─── Refresh from settings ──────────────────────────────────────────────
    def refresh(self) -> None:
        """Load configuration details from SQLite DB and update page fields."""
        try:
            profile = self.settings.get_business()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load settings: {e}")
            return

        self.name_input.setText(profile.name)
        self.email_input.setText(profile.email)
        self.phone_input.setText(profile.phone)
        self.role_input.setText(profile.role)
        self.bio_input.setPlainText(profile.bio)

        self.address_input.setPlainText(profile.address)
        self.gstin_input.setText(profile.gstin)
        self._set_logo_path(profile.logo_path)

        self.upi_id_input.setText(profile.upi_id)
        self.upi_name_input.setText(profile.upi_name)

        self.due_days_input.setValue(self.settings.get_default_due_days())

        # SMTP Configuration load
        try:
            cfg = self.email_service.get_config()
            self.smtp_host.setText(cfg.host)
            self.smtp_port.setValue(cfg.port)
            self.smtp_username.setText(cfg.username)
            self.smtp_password.setText(cfg.password)
            self.smtp_from.setText(cfg.from_addr)
            self.smtp_use_tls.setChecked(cfg.use_tls)
        except Exception:
            pass

        # Notification Preferences load
        try:
            notif_cfg = self.notification_service.get_config()
            self.notifications_enabled.setChecked(notif_cfg.enabled)
            self.desktop_notifications.setChecked(notif_cfg.desktop_enabled)
            self.email_reminders.setChecked(notif_cfg.email_enabled)
            self.days_before_due.setValue(notif_cfg.days_before_due)
            self.reminder_frequency.setCurrentText(notif_cfg.frequency.capitalize())
            self.notify_overdue.setChecked(notif_cfg.notify_overdue)
            self.notify_deadlines.setChecked(notif_cfg.notify_deadlines)
            self.notify_payments.setChecked(notif_cfg.notify_payments)
            self._update_notification_status()
        except Exception:
            pass

    # ─── Save Handlers ──────────────────────────────────────────────────────
    def _save_profile(self) -> None:
        """Save account details (Full Name, email, phone, role, bio) to DB."""
        profile = self.settings.get_business()
        profile.name = self.name_input.text().strip()
        profile.email = self.email_input.text().strip()
        profile.phone = self.phone_input.text().strip()
        profile.role = self.role_input.text().strip()
        profile.bio = self.bio_input.toPlainText().strip()
        profile.logo_path = self._logo_path

        try:
            self.settings.save_business(profile)
            emit_data_changed()
            QMessageBox.information(self, "Saved", "Profile & Account changes saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save profile: {e}")

    def _save_workspace(self) -> None:
        """Save workspace and payment settings to SQLite database."""
        profile = self.settings.get_business()
        profile.address = self.address_input.toPlainText().strip()
        profile.gstin = self.gstin_input.text().strip()
        profile.upi_id = self.upi_id_input.text().strip()
        profile.upi_name = self.upi_name_input.text().strip()

        try:
            self.settings.save_business(profile)
            self.settings.set_default_due_days(self.due_days_input.value())
            emit_data_changed()
            QMessageBox.information(self, "Saved", "Workspace details updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save workspace details: {e}")

    # ─── Avatar / Logo Selection ────────────────────────────────────────────
    def _choose_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose Profile Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
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
                self.avatar_preview.setPixmap(pix)
            self.avatar_path_label.setText(Path(self._logo_path).name)
        else:
            self.avatar_preview.clear()
            self.avatar_path_label.setText("No image selected")

    # ─── SMTP Server handlers ────────────────────────────────────────────────
    def _save_smtp(self) -> None:
        """Collect input fields and store SMTP configuration properties."""
        from app.core.email_service import SMTPConfig

        cfg = SMTPConfig(
            host=self.smtp_host.text().strip(),
            port=self.smtp_port.value(),
            username=self.smtp_username.text().strip(),
            password=self.smtp_password.text(),
            from_addr=self.smtp_from.text().strip(),
            use_tls=self.smtp_use_tls.isChecked(),
        )
        try:
            self.email_service.save_config(cfg)
            QMessageBox.information(self, "Saved", "SMTP server integration saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save SMTP: {e}")

    def _send_test_email(self) -> None:
        """Trigger SMTP validation by sending a test message."""
        from_addr = self.smtp_from.text().strip()
        if not from_addr:
            QMessageBox.warning(self, "Validation", "Configure sender email address first.")
            return

        self._save_smtp()

        try:
            self.email_service.send(
                to_addr=from_addr,
                subject="SmartDesk Verification Mail",
                body="Testing SMTP email delivery server config. Connection successful.",
            )
            QMessageBox.information(self, "Sent", f"SMTP verification sent to {from_addr}.")
        except Exception as e:
            QMessageBox.critical(self, "Verification Failed", f"Connection error: {e}")

    # ─── Data Management backup/restore/CSV ──────────────────────────────────
    def _create_backup(self) -> None:
        suggested = BackupService.suggested_filename()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Backup Archive", suggested, "Zip Files (*.zip)"
        )
        if not path:
            return
        try:
            output = self.backup.create_backup(Path(path))
            QMessageBox.information(self, "Backup Success", f"ZIP archive exported:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Error: {e}")

    def _restore_backup(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Restore Snapshot",
            "This will completely overwrite the local database with backup snapshot. Continue?",
        )
        if confirm != QMessageBox.Yes:
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup Archive", "", "Zip Files (*.zip)"
        )
        if not path:
            return

        try:
            self.backup.restore_backup(Path(path))
            QMessageBox.information(
                self,
                "Restore Success",
                "Snapshot restored. Please restart SmartDesk to load latest database.",
            )
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", f"Error: {e}")

    def _export_csv(self, kind: str) -> None:
        suggested = f"{kind}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, f"Export {kind.capitalize()}", suggested, "CSV Files (*.csv)"
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
            QMessageBox.information(self, "Export Complete", f"Data saved to:\n{output}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error: {e}")

    # ─── Receipt OCR tools ──────────────────────────────────────────────────
    def _choose_receipt(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Scanned Receipt", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self._receipt_path = path
            self.receipt_path_label.setText(Path(path).name)

    def _run_receipt_ocr(self) -> None:
        if not self._receipt_path:
            QMessageBox.warning(self, "Warning", "Select receipt image first.")
            return

        result = self.ocr.extract(self._receipt_path)
        if not result.get("success"):
            QMessageBox.critical(self, "OCR Error", result.get("error", "Failed to run OCR."))
            return

        amt = result.get("amount")
        dt = result.get("date") or "—"
        amt_str = f"₹{amt:,.2f}" if amt else "Not detected"

        self.receipt_summary.setText(f"Detected Sum: {amt_str}   |   Date: {dt}")
        self.receipt_text.setPlainText(result.get("text", ""))

    # ─── Notification Settings ──────────────────────────────────────────────
    def _save_notification_settings(self) -> None:
        """Collect notification fields and save configuration to SQLite."""
        from app.core.notification_service import NotificationConfig

        config = NotificationConfig(
            enabled=self.notifications_enabled.isChecked(),
            desktop_enabled=self.desktop_notifications.isChecked(),
            email_enabled=self.email_reminders.isChecked(),
            days_before_due=self.days_before_due.value(),
            frequency=self.reminder_frequency.currentText().lower(),
            notify_overdue=self.notify_overdue.isChecked(),
            notify_deadlines=self.notify_deadlines.isChecked(),
            notify_payments=self.notify_payments.isChecked(),
        )

        try:
            self.notification_service.save_config(config)
            self._update_notification_status()
            QMessageBox.information(self, "Saved", "Notification configurations saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save preferences: {e}")

    def _send_test_notification(self) -> None:
        """Trigger an instant OS desktop notification validation alert."""
        success = self.notification_service.send_desktop_notification(
            title="SmartDesk Verification Alert",
            message="OS notifications integrated. Communication channels are open.",
            timeout=8,
        )
        if success:
            QMessageBox.information(self, "Test Alert Sent", "Desktop notification triggered successfully.")
        else:
            QMessageBox.warning(
                self,
                "Test Alert Failed",
                "Desktop alerts are not available.\n\n"
                "Install plyer package via pip and make sure notifications are enabled."
            )

    def _check_notifications_now(self) -> None:
        """Trigger immediate notification daemon check."""
        try:
            overdue_res = self.notification_service.send_all_overdue_reminders()
            deadline_res = self.notification_service.send_all_deadline_reminders()
            self.notification_service.mark_reminder_check_done()

            msg = (
                f"Automated notification scan complete:\n\n"
                f"Overdue Invoices:\n"
                f"  • Found: {overdue_res['total']}\n"
                f"  • Desktop Popups: {overdue_res['desktop_sent']}\n"
                f"  • Reminders Emailed: {overdue_res['emails_sent']}\n\n"
                f"Upcoming Project Deadlines:\n"
                f"  • Found: {deadline_res['total']}\n"
                f"  • Popups Triggered: {deadline_res['sent']}\n"
            )
            if overdue_res["failed"] or deadline_res["failed"]:
                msg += "\n⚠️ Some reminders failed to deliver."

            self._update_notification_status()
            QMessageBox.information(self, "Scan Complete", msg)
        except Exception as e:
            QMessageBox.critical(self, "Scan Failed", f"Error: {e}")

    def _update_notification_status(self) -> None:
        """Query and display notification background daemon stats."""
        try:
            sumry = self.notification_service.get_notification_summary()
            parts = []

            if sumry["enabled"]:
                parts.append("✅ Notifications active")
            else:
                parts.append("❌ Notifications muted")

            if sumry["desktop_available"]:
                parts.append("✅ OS popup alerts available")
            else:
                parts.append("⚠️ OS popup alerts disabled (missing plyer)")

            parts.append(f"📧 {sumry['pending_overdue']} unpaid overdue bills need reminders")
            parts.append(f"📅 {sumry['pending_deadlines']} projects approaching deadline")

            self.notification_status_label.setText("\n".join(parts))
        except Exception:
            self.notification_status_label.setText("⚠️ Failed to load daemon stats")

    # ─── Danger Zone Actions ────────────────────────────────────────────────
    def _reset_preferences(self) -> None:
        """Clear all preference configurations and SMTP keys to defaults."""
        confirm = QMessageBox.question(
            self,
            "Reset Preferences",
            "Are you sure you want to reset all preferences and SMTP integration settings to defaults?\n"
            "This will not modify database clients, projects, or invoices.",
        )
        if confirm != QMessageBox.Yes:
            return

        keys_to_delete = [
            "smtp_host", "smtp_port", "smtp_username", "smtp_password", "smtp_from", "smtp_use_tls",
            "notifications_enabled", "desktop_notifications_enabled", "email_reminders_enabled",
            "reminder_days_before_due", "reminder_frequency", "last_reminder_check",
            "notify_overdue_invoices", "notify_upcoming_deadlines", "notify_payments_received",
            "default_due_days", "user_role", "user_bio"
        ]
        try:
            for key in keys_to_delete:
                self.settings.repo.delete(key)

            emit_data_changed()
            self.refresh()
            QMessageBox.information(self, "Reset Complete", "All preferences have been reset to default values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Reset failed: {e}")

    def _clear_workspace_data(self) -> None:
        """Delete all transaction/workspace tables. Retain configuration."""
        text, ok = QInputDialog.getText(
            self,
            "Clear Workspace Data",
            "This will delete all client, project, invoice, payment, task, contract, and time records.\n"
            "This action cannot be undone.\n\n"
            "To confirm, type 'CLEAR' below:"
        )
        if not ok or text.strip() != "CLEAR":
            return

        try:
            # Clear all transactions in reverse-dependency order
            self.db.execute("DELETE FROM payments")
            self.db.execute("DELETE FROM invoices")
            self.db.execute("DELETE FROM time_logs")
            self.db.execute("DELETE FROM tasks")
            self.db.execute("DELETE FROM contracts")
            self.db.execute("DELETE FROM ml_predictions")
            self.db.execute("DELETE FROM projects")
            self.db.execute("DELETE FROM clients")

            emit_data_changed()
            QMessageBox.information(self, "Success", "All workspace records have been deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear workspace: {e}")

    def _reset_database(self) -> None:
        """Drop all tables and re-initialize completely."""
        text, ok = QInputDialog.getText(
            self,
            "Reset Database",
            "Wipe all tables, configurations, preferences, and data.\n"
            "This action is destructive and cannot be undone.\n\n"
            "To confirm, type 'RESET' below:"
        )
        if not ok or text.strip() != "RESET":
            return

        try:
            # Disable foreign keys temporarily for clean dropping
            self.db.execute("PRAGMA foreign_keys = OFF")
            
            tables = [
                "payments", "invoices", "time_logs", "tasks", "contracts",
                "ml_predictions", "projects", "clients", "app_settings", "schema_version"
            ]
            for table in tables:
                self.db.execute(f"DROP TABLE IF EXISTS {table}")
            
            self.db.execute("PRAGMA foreign_keys = ON")
            
            # Recreate schema and migrations
            self.db.initialize()
            emit_data_changed()
            self.refresh()
            QMessageBox.information(self, "Success", "Database has been fully reset and re-initialized.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset database: {e}")
