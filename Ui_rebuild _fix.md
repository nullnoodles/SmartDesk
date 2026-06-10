# Projects Page — Complete Formatting Fix Guide (PySide6)

---

## Issues Identified from Screenshot

| # | Problem | Location |
|---|---------|----------|
| 1 | "New Project" button is cut off on the right edge | Top-right header |
| 2 | "5 Total" badge looks unstyled / dark box visible | Header row |
| 3 | Stat cards are uneven height & icon sizes differ | Top stat cards row |
| 4 | "Workspace Insight" card has no icon, different style | 4th stat card |
| 5 | "OPTIMIZE SCHEDULE" link has dark background box | Workspace Insight card |
| 6 | ID column shows "SD-..." text is truncated | Table |
| 7 | TYPE column text is truncated ("Develop...", "Product...") | Table |
| 8 | DEADLINE column truncated ("Sep 28, ...") | Table |
| 9 | ACTIONS column is empty (no edit/delete icons visible) | Table |
| 10 | Bottom action bar (Ba... / Delete) is cut off | Footer |
| 11 | Row spacing in table is inconsistent | Table rows |
| 12 | Status badges have inconsistent border-radius styling | Table STATUS column |

---

## Fix 1 — Header Layout (Title + Badge + Button)

### Problem:
- "New Project" button clips off screen
- "5 Total" badge has wrong styling
- Header items not aligned properly

### Fix:
```python
# In your projects page __init__ or setup_ui():

# Header layout — use QHBoxLayout with proper margins
header_layout = QHBoxLayout()
header_layout.setContentsMargins(20, 20, 20, 20)
header_layout.setSpacing(12)

# Title + subtitle vertical stack
title_layout = QVBoxLayout()
title_layout.setSpacing(2)

title_label = QLabel("Projects")
title_label.setStyleSheet("""
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    background: transparent;
    border: none;
""")

subtitle_label = QLabel("Manage and track your active production pipeline.")
subtitle_label.setStyleSheet("""
    font-size: 13px;
    color: #8888aa;
    background: transparent;
    border: none;
""")

title_layout.addWidget(title_label)
title_layout.addWidget(subtitle_label)

# "5 Total" badge
total_badge = QLabel("5 Total")
total_badge.setFixedHeight(32)
total_badge.setStyleSheet("""
    QLabel {
        background-color: #2a2a3e;
        color: #aaaacc;
        font-size: 13px;
        font-weight: 600;
        border-radius: 8px;
        padding: 4px 14px;
        border: 1px solid #3a3a5a;
    }
""")
total_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Spacer to push button to right
spacer = QSpacerItem(
    40, 20,
    QSizePolicy.Policy.Expanding,
    QSizePolicy.Policy.Minimum
)

# New Project button — FIXED (no clipping)
new_project_btn = QPushButton("+ New Project")
new_project_btn.setFixedHeight(42)
new_project_btn.setMinimumWidth(140)
new_project_btn.setCursor(Qt.CursorShape.PointingHandCursor)
new_project_btn.setStyleSheet("""
    QPushButton {
        background-color: #6c63ff;
        color: #ffffff;
        font-size: 14px;
        font-weight: 600;
        border-radius: 10px;
        padding: 8px 24px;
        border: none;
    }
    QPushButton:hover {
        background-color: #7c73ff;
    }
    QPushButton:pressed {
        background-color: #5c53ef;
    }
""")

header_layout.addLayout(title_layout)
header_layout.addWidget(total_badge)
header_layout.addSpacerItem(spacer)
header_layout.addWidget(new_project_btn)


