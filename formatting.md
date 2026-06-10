# Projects Page — Complete Formatting Reference

## CURRENT ISSUES
- "New Project" button clipped on right edge
- "5 Total" badge unstyled
- Stat cards uneven height
- Dark boxes behind labels
- Table columns truncating text
- Actions column empty
- Bottom bar clipped
- Status badges inconsistent
- Row heights inconsistent

---

## COMPLETE CODE

### projects_page.py

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QSpacerItem,
    QScrollArea, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont


# ============================================================
# COLOR CONSTANTS
# ============================================================
BG_MAIN        = "#0d0d1a"
BG_CARD        = "#1a1a2e"
BG_TABLE       = "#12121f"
BORDER         = "#2a2a3e"
BORDER_LIGHT   = "#3a3a5a"
TEXT_PRIMARY   = "#ffffff"
TEXT_SECONDARY = "#8888aa"
TEXT_MUTED     = "#6666aa"
ACCENT_PURPLE  = "#6c63ff"
ACCENT_GREEN   = "#44cc88"
ACCENT_RED     = "#cc4444"
ACCENT_ORANGE  = "#cc8844"
ACCENT_BLUE    = "#44aaff"
ROW_SELECTED   = "#2a2a4a"
AVATAR_BG      = "#4a4a8a"


# ============================================================
# SAMPLE DATA
# ============================================================
PROJECTS_DATA = [
    {
        "id":       "SD-001",
        "name":     "Cloud Architecture Audit",
        "subtitle": "Consultancy",
        "avatar":   "GL",
        "client":   "Global Logistics",
        "type":     "Consulting",
        "status":   "Archived",
        "deadline": "Sep 28, 2025",
    },
    {
        "id":       "SD-002",
        "name":     "Apex Mobile App",
        "subtitle": "iOS & Android MVP",
        "avatar":   "DK",
        "client":   "David Kim",
        "type":     "Development",
        "status":   "Delayed",
        "deadline": "In 2 Days",
    },
    {
        "id":       "SD-003",
        "name":     "Nexus Landing Page",
        "subtitle": "Marketing Collateral",
        "avatar":   "SC",
        "client":   "Sarah Connor",
        "type":     "Web Dev",
        "status":   "Revision",
        "deadline": "Oct 30, 2025",
    },
    {
        "id":       "SD-004",
        "name":     "Solaris Dashboard UI",
        "subtitle": "High-Fidelity Prototyping",
        "avatar":   "MC",
        "client":   "Marcus Chen",
        "type":     "Product Design",
        "status":   "Completed",
        "deadline": "Oct 12, 2025",
    },
    {
        "id":       "SD-005",
        "name":     "Brand Identity Redesign",
        "subtitle": "Creative Suite Expansion",
        "avatar":   "MP",
        "client":   "Meera Patel",
        "type":     "Branding",
        "status":   "Active",
        "deadline": "Oct 24, 2025",
    },
]


# ============================================================
# STATUS BADGE COLORS
# ============================================================
STATUS_COLORS = {
    "Active":    ("#1a3a2a", "#44cc88", "#44cc88"),
    "Completed": ("#1a3a2a", "#44cc88", "#44cc88"),
    "Delayed":   ("#3a1a1a", "#cc4444", "#cc4444"),
    "Revision":  ("#3a2a1a", "#cc8844", "#cc8844"),
    "Archived":  ("#2a2a2a", "#888888", "#555555"),
    "On Hold":   ("#2a2a3a", "#6666aa", "#6666aa"),
}


# ============================================================
# MAIN PROJECTS PAGE
# ============================================================
class ProjectsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectsPage")
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        self._setup_ui()

    # ----------------------------------------------------------
    # MASTER LAYOUT
    # ----------------------------------------------------------
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 16)
        main_layout.setSpacing(20)

        main_layout.addLayout(self._build_header())
        main_layout.addLayout(self._build_stat_cards())
        main_layout.addWidget(self._build_table_section(), stretch=1)
        main_layout.addWidget(self._build_bottom_bar())

    # ----------------------------------------------------------
    # SECTION 1 — HEADER
    # ----------------------------------------------------------
    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # --- Title block ---
        title_block = QVBoxLayout()
        title_block.setSpacing(4)

        title = QLabel("Projects")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: 700;
                color: {TEXT_PRIMARY};
                background: transparent;
                border: none;
            }}
        """)

        subtitle = QLabel("Manage and track your active production pipeline.")
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: {TEXT_SECONDARY};
                background: transparent;
                border: none;
            }}
        """)

        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        # --- Total badge ---
        total_badge = QLabel("5 Total")
        total_badge.setFixedHeight(32)
        total_badge.setContentsMargins(14, 0, 14, 0)
        total_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_CARD};
                color: #aaaacc;
                font-size: 13px;
                font-weight: 600;
                border-radius: 8px;
                border: 1px solid {BORDER_LIGHT};
            }}
        """)

        # --- Spacer ---
        spacer = QSpacerItem(
            40, 20,
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        # --- New Project button ---
        new_btn = QPushButton("+ New Project")
        new_btn.setFixedHeight(42)
        new_btn.setMinimumWidth(145)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_PURPLE};
                color: {TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 600;
                border-radius: 10px;
                padding: 8px 24px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #7c73ff;
            }}
            QPushButton:pressed {{
                background-color: #5c53ef;
            }}
        """)

        layout.addLayout(title_block)
        layout.addWidget(
            total_badge,
            alignment=Qt.AlignmentFlag.AlignVCenter
        )
        layout.addSpacerItem(spacer)
        layout.addWidget(
            new_btn,
            alignment=Qt.AlignmentFlag.AlignVCenter
        )

        return layout

    # ----------------------------------------------------------
    # SECTION 2 — STAT CARDS ROW
    # ----------------------------------------------------------
    def _build_stat_cards(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._stat_card(
            icon="🔥",
            icon_bg="#1a3a2e",
            top_value="+12%",
            top_color=ACCENT_GREEN,
            label="ACTIVE VELOCITY",
            main_value="1 Current",
        ))
        layout.addWidget(self._stat_card(
            icon="⏳",
            icon_bg="#3a2a1a",
            top_value="2 Late",
            top_color=ACCENT_RED,
            label="UPCOMING DEADLINES",
            main_value="0 Urgent",
        ))
        layout.addWidget(self._stat_card(
            icon="💻",
            icon_bg="#1a2a3a",
            top_value="$12.4k",
            top_color=ACCENT_BLUE,
            label="PIPELINE VALUE",
            main_value="$17,800",
        ))
        layout.addWidget(self._workspace_insight_card(
            message=(
                "You're currently at 85% capacity. "
                "AI suggests shifting the Apex Mobile deadline."
            ),
            action="OPTIMIZE SCHEDULE",
        ))

        return layout

    def _stat_card(
        self,
        icon: str,
        icon_bg: str,
        top_value: str,
        top_color: str,
        label: str,
        main_value: str,
    ) -> QFrame:

        card = QFrame()
        card.setFixedHeight(120)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 14px;
                border: 1px solid {BORDER};
            }}
        """)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(6)

        # Top row
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {icon_bg};
                border-radius: 10px;
                font-size: 18px;
                border: none;
            }}
        """)

        top_val = QLabel(top_value)
        top_val.setStyleSheet(f"""
            QLabel {{
                color: {top_color};
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        top_row.addWidget(top_val)

        # Sub label
        sub_lbl = QLabel(label)
        sub_lbl.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                font-size: 11px;
                font-weight: 500;
                background: transparent;
                border: none;
                letter-spacing: 1px;
            }}
        """)

        # Main value
        main_lbl = QLabel(main_value)
        main_lbl.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 22px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)

        outer.addLayout(top_row)
        outer.addWidget(sub_lbl)
        outer.addWidget(main_lbl)

        return card

    def _workspace_insight_card(
        self,
        message: str,
        action: str,
    ) -> QFrame:

        card = QFrame()
        card.setFixedHeight(120)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 14px;
                border: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title = QLabel("Workspace Insight")
        title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 15px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)

        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 12px;
                background: transparent;
                border: none;
            }}
        """)

        optimize_btn = QPushButton(f"{action}  ›")
        optimize_btn.setFixedHeight(24)
        optimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        optimize_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #aaaaff;
                font-size: 11px;
                font-weight: 700;
                border: none;
                text-align: left;
                letter-spacing: 1px;
                padding: 0px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY};
            }}
        """)

        layout.addWidget(title)
        layout.addWidget(msg)
        layout.addWidget(optimize_btn)

        return card

    # ----------------------------------------------------------
    # SECTION 3 — TABLE
    # ----------------------------------------------------------
    def _build_table_section(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_TABLE};
                border-radius: 14px;
                border: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_table())

        return frame

    def _build_table(self) -> QTableWidget:
        headers = [
            "ID", "PROJECT", "CLIENT",
            "TYPE", "STATUS", "DEADLINE", "ACTIONS"
        ]

        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(PROJECTS_DATA))

        # --- Column widths ---
        table.setColumnWidth(0, 110)   # ID
        table.setColumnWidth(1, 200)   # PROJECT
        table.setColumnWidth(2, 180)   # CLIENT
        table.setColumnWidth(3, 150)   # TYPE
        table.setColumnWidth(4, 130)   # STATUS
        table.setColumnWidth(5, 140)   # DEADLINE
        table.setColumnWidth(6, 110)   # ACTIONS

        # --- Resize modes ---
        hdr = table.horizontalHeader()
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in [0, 2, 3, 4, 5, 6]:
            hdr.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)

        # --- Row height ---
        table.verticalHeader().setDefaultSectionSize(64)
        table.verticalHeader().setVisible(False)

        # --- Behaviour ---
        table.setShowGrid(False)
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # --- Stylesheet ---
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_TABLE};
                border: none;
                border-radius: 14px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 10px 12px;
                border: none;
                background: transparent;
                border-bottom: 1px solid {BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {ROW_SELECTED};
                border: none;
            }}
            QHeaderView {{
                background-color: {BG_TABLE};
                border: none;
            }}
            QHeaderView::section {{
                background-color: {BG_TABLE};
                color: {TEXT_MUTED};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
                padding: 14px 12px;
                border: none;
                border-bottom: 1px solid {BORDER};
            }}
            QScrollBar:vertical {{
                background: {BG_TABLE};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER_LIGHT};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # --- Populate rows ---
        for row, project in enumerate(PROJECTS_DATA):
            # ID
            id_item = QTableWidgetItem(project["id"])
            id_item.setForeground(QColor(TEXT_MUTED))
            table.setItem(row, 0, id_item)

            # PROJECT — two-line widget
            table.setCellWidget(
                row, 1,
                self._project_name_cell(
                    project["name"],
                    project["subtitle"]
                )
            )

            # CLIENT — avatar + name
            table.setCellWidget(
                row, 2,
                self._client_cell(
                    project["avatar"],
                    project["client"]
                )
            )

            # TYPE
            type_item = QTableWidgetItem(project["type"])
            type_item.setForeground(QColor(TEXT_SECONDARY))
            table.setItem(row, 3, type_item)

            # STATUS — badge widget
            table.setCellWidget(
                row, 4,
                self._status_badge(project["status"])
            )

            # DEADLINE
            deadline_item = QTableWidgetItem(project["deadline"])
            if project["deadline"] == "In 2 Days":
                deadline_item.setForeground(QColor(ACCENT_RED))
                font = QFont()
                font.setBold(True)
                deadline_item.setFont(font)
            else:
                deadline_item.setForeground(QColor(TEXT_SECONDARY))
            table.setItem(row, 5, deadline_item)

            # ACTIONS — edit + delete
            table.setCellWidget(
                row, 6,
                self._action_buttons(project["id"])
            )

        self.table = table
        return table

    # ----------------------------------------------------------
    # TABLE CELL WIDGETS
    # ----------------------------------------------------------
    def _project_name_cell(
        self,
        name: str,
        subtitle: str
    ) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(3)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                font-size: 11px;
                font-weight: 400;
                background: transparent;
                border: none;
            }}
        """)

        layout.addWidget(name_lbl)
        layout.addWidget(sub_lbl)

        return w

    def _client_cell(
        self,
        initials: str,
        name: str
    ) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(w)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        avatar = QLabel(initials)
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {AVATAR_BG};
                color: {TEXT_PRIMARY};
                border-radius: 16px;
                font-size: 11px;
                font-weight: 700;
                border: none;
            }}
        """)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"""
            QLabel {{
                color: #ccccee;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)

        layout.addWidget(avatar)
        layout.addWidget(name_lbl)
        layout.addStretch()

        return w

    def _status_badge(self, status: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(w)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        bg, text_color, border = STATUS_COLORS.get(
            status, ("#2a2a2a", "#aaaaaa", "#555555")
        )

        badge = QLabel(status)
        badge.setFixedHeight(28)
        badge.setMinimumWidth(85)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {text_color};
                border: 1px solid {border};
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                padding: 2px 10px;
            }}
        """)

        layout.addWidget(badge)
        layout.addStretch()

        return w

    def _action_buttons(self, row_id: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(w)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        edit_btn = QPushButton("✏")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setToolTip(f"Edit {row_id}")
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2a2a4a;
                color: #aaaaff;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #3a3a6a;
            }}
        """)

        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setToolTip(f"Delete {row_id}")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2a1a1a;
                color: {ACCENT_RED};
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #3a2a2a;
            }}
        """)

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()

        return w

    # ----------------------------------------------------------
    # SECTION 4 — BOTTOM ACTION BAR
    # ----------------------------------------------------------
    def _build_bottom_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(56)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-top: 1px solid {BORDER};
                border-radius: 0px;
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(12)

        edit_btn = QPushButton("✏   Edit Selected")
        edit_btn.setFixedHeight(38)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2a2a4a;
                color: #aaaaff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 20px;
            }}
            QPushButton:hover {{ background-color: #3a3a6a; }}
            QPushButton:pressed {{ background-color: #1a1a3a; }}
        """)

        delete_btn = QPushButton("🗑   Delete Selected")
        delete_btn.setFixedHeight(38)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2a1a1a;
                color: {ACCENT_RED};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 20px;
            }}
            QPushButton:hover {{ background-color: #3a2a2a; }}
            QPushButton:pressed {{ background-color: #1a0a0a; }}
        """)

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()

        return bar




GLOBAL STYLESHEET PATCH
Add to your main window or app stylesheet:
Python

GLOBAL_QSS = f"""
    QWidget {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    QLabel {{
        background: transparent;
        border: none;
    }}
    QFrame {{
        border: none;
    }}
    QTableWidget {{
        outline: none;
    }}
    QScrollBar:vertical {{
        background: {BG_TABLE};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER_LIGHT};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        height: 0px;
    }}
"""


COLUMN WIDTH REFERENCE
Column	Index	Width	Mode
ID	0	110px	Fixed
PROJECT	1	200px	Stretch
CLIENT	2	180px	Fixed
TYPE	3	150px	Fixed
STATUS	4	130px	Fixed
DEADLINE	5	140px	Fixed
ACTIONS	6	110px	Fixed


STAT CARD REFERENCE
Card	Icon	Icon BG	Top Value	Top Color
Active Velocity	🔥	#1a3a2e	+12%	#44cc88
Upcoming Deadlines	⏳	#3a2a1a	2 Late	#cc4444
Pipeline Value	💻	#1a2a3a	$12.4k	#44aaff
Workspace Insight	none	none	n/a	n/a

STATUS BADGE REFERENCE
Status	Background	Text	Border
Active	#1a3a2a	#44cc88	#44cc88
Completed	#1a3a2a	#44cc88	#44cc88
Delayed	#3a1a1a	#cc4444	#cc4444
Revision	#3a2a1a	#cc8844	#cc8844
Archived	#2a2a2a	#888888	#555555
On Hold	#2a2a3a	#6666aa	#6666aa


SIZE REFERENCE
Element	Property	Value
Stat cards	height	120px
Card icons	size	40 x 40px
Table rows	height	64px
Status badges	height	28px
Status badges	min-width	85px
Avatar circles	size	32 x 32px
Action buttons	size	32 x 32px
New Project button	height	42px
New Project button	min-width	145px
Total badge	height	32px
Bottom bar	height	56px
Edit/Delete buttons	height	38px
Border radius — cards		14px
Border radius — badges		8px
Border radius — buttons		8-10px
Border radius — avatars		16px
COLOR REFERENCE
Python

BG_MAIN        = "#0d0d1a"   # page background
BG_CARD        = "#1a1a2e"   # card background
BG_TABLE       = "#12121f"   # table background
BORDER         = "#2a2a3e"   # default border
BORDER_LIGHT   = "#3a3a5a"   # lighter border
TEXT_PRIMARY   = "#ffffff"   # main text
TEXT_SECONDARY = "#8888aa"   # secondary text
TEXT_MUTED     = "#6666aa"   # muted / label text
ACCENT_PURPLE  = "#6c63ff"   # primary button
ACCENT_GREEN   = "#44cc88"   # active / completed
ACCENT_RED     = "#cc4444"   # delayed / delete
ACCENT_ORANGE  = "#cc8844"   # revision
ACCENT_BLUE    = "#44aaff"   # pipeline value
ROW_SELECTED   = "#2a2a4a"   # table row highlight
AVATAR_BG      = "#4a4a8a"   # avatar circle
CHECKLIST
text

[ ] "New Project" button — fully visible, not clipped
[ ] "5 Total" badge — correct color and border-radius
[ ] All 4 stat cards — same height (120px)
[ ] All stat card icons — same size (40x40px)
[ ] "OPTIMIZE SCHEDULE" — no dark box, transparent background
[ ] Table ID column — full ID visible (110px wide)
[ ] Table TYPE column — full text visible (150px wide)
[ ] Table DEADLINE column — full date visible (140px wide)
[ ] Table PROJECT column — two-line name + subtitle
[ ] Table CLIENT column — avatar circle + name
[ ] Table ACTIONS column — edit and delete buttons visible
[ ] Status badges — all same height, consistent border-radius
[ ] Bottom bar — fully visible, not clipped (56px height)
[ ] No dark boxes behind any QLabel
[ ] Table rows — consistent 64px height
[ ] Row selected highlight — correct color (#2a2a4a)
[ ] Scrollbar — styled and narrow (8px)
[ ] All inner widgets — background: transparent; border: none