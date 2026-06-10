"Apply the SmartDesk Studio Graphite design system consistently across ALL pages. Read every page file first, then update colors. Do not change any layout, functionality, or data.
Design system to apply:
Background (Deep):  #12131d — sidebar, page background
Surface (Main):     #1a1b26 — card backgrounds
Surface (Bright):   #383844 — hover states
Accent (Primary):   #7c8af4 — buttons, active nav
Text (Primary):     #e2e4f0 — headings, body
Text (Secondary):   #9a9cb8 — labels, captions

Success (Mint):     #7dd3a8 — Completed, Paid
Warning (Amber):    #f0c878 — Unpaid, On Hold
Danger (Rose):      #e87c8a — Overdue, Critical, destructive
Info (Teal):        #6ec5d4 — In Progress, analytical


Step 1 — Update style.qss with these exact values:
css/* Page backgrounds */
QMainWindow, QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: #12131d;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #12131d;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Cards */
QFrame#card, QFrame#statCard {
    background-color: #1a1b26;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.06);
}

/* Hover */
QFrame#card:hover, QFrame#statCard:hover {
    background-color: #383844;
}

/* Text */
QLabel#titleLabel {
    color: #e2e4f0;
}
QLabel#subtitleLabel {
    color: #9a9cb8;
}

/* Primary button */
QPushButton#primaryBtn {
    background-color: #7c8af4;
    color: #e2e4f0;
    border-radius: 8px;
    border: none;
    padding: 6px 16px;
    font-weight: 600;
}
QPushButton#primaryBtn:hover {
    background-color: #9099f5;
}

/* Danger button */
QPushButton#dangerBtn {
    background-color: #e87c8a;
    color: #e2e4f0;
    border-radius: 8px;
    border: none;
}

/* Table */
QTableWidget {
    background-color: #1a1b26;
    border-radius: 12px;
    border: none;
    gridline-color: rgba(255,255,255,0.06);
}
QTableWidget::item {
    color: #e2e4f0;
    background: transparent;
    border: none;
    padding: 8px 12px;
}
QTableWidget::item:selected {
    background-color: rgba(124,138,244,0.12);
}
QTableWidget::item:hover {
    background-color: rgba(255,255,255,0.04);
}
QHeaderView::section {
    background-color: #1a1b26;
    color: #9a9cb8;
    font-size: 11px;
    font-weight: 600;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

/* Status pill badges */
QLabel#badgeCompleted { background-color: rgba(125,211,168,0.15); color: #7dd3a8; border: 1px solid #7dd3a8; border-radius: 10px; padding: 2px 10px; }

QLabel#badgeInProgress { background-color: rgba(110,197,212,0.15); color: #6ec5d4; border: 1px solid #6ec5d4; border-radius: 10px; padding: 2px 10px; }

QLabel#badgeOnHold { background-color: rgba(240,200,120,0.15); color: #f0c878; border: 1px solid #f0c878; border-radius: 10px; padding: 2px 10px; }

QLabel#badgeOverdue { background-color: rgba(232,124,138,0.15); color: #e87c8a; border: 1px solid #e87c8a; border-radius: 10px; padding: 2px 10px; }

QLabel#badgeNotStarted { background-color: rgba(154,156,184,0.15); color: #9a9cb8; border: 1px solid #9a9cb8; border-radius: 10px; padding: 2px 10px; }


Step 2 — Update all status pill badges across Dashboard, Clients, Projects pages to use these objectNames and colors:
pythonbadge_config = {
    "Completed":   ("badgeCompleted",  "#7dd3a8"),
    "In Progress": ("badgeInProgress", "#6ec5d4"),
    "Active":      ("badgeInProgress", "#6ec5d4"),
    "On Hold":     ("badgeOnHold",     "#f0c878"),
    "Unpaid":      ("badgeOnHold",     "#f0c878"),
    "Review":      ("badgeOnHold",     "#f0c878"),
    "Overdue":     ("badgeOverdue",    "#e87c8a"),
    "Not Started": ("badgeNotStarted", "#9a9cb8"),
    "Inactive":    ("badgeNotStarted", "#9a9cb8"),
    "Cancelled":   ("badgeOverdue",    "#e87c8a"),
    "Paid":        ("badgeCompleted",  "#7dd3a8"),
}
badge.setObjectName(badge_config[status][0])

Step 3 — Update stat card subtitle 3-color logic to use design system colors:
pythonGREEN  = "#7dd3a8"  # was #4ADE80
GREY   = "#9a9cb8"  # was #8B8FA8
RED    = "#e87c8a"  # was #E53E5A

Step 4 — Update all primary buttons across all pages to use #7c8af4

Step 5 — Update sidebar active nav item to use #7c8af4 background

Step 6 — Remove dark boxes from all QLabels — set background: transparent on every QLabel that's inside a card

Step 7 — Run app, verify all pages look consistent, run pytest, commit with message 'style: apply Studio Graphite design system'"