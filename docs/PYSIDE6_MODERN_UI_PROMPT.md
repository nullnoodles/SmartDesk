# Complete Prompt: Build a Modern Minimalist PySide6 UI

Use this prompt with AI assistants (Claude, ChatGPT, etc.) to build professional, modern PySide6 desktop applications.

---

## 🎯 Project Overview

I need you to build a modern, minimalist desktop application using **PySide6 (Qt 6)** with a professional dark theme. The application should look and feel like modern professional software (think Figma, Notion, Linear, or VS Code).

---

## 🎨 Design System Requirements

### **Color Palette (Dark Theme)**

Use this exact color palette for consistency:

```python
# Backgrounds (3-tier depth system)
BG_DARKEST = "#12131a"      # Deepest layer (sidebar, footer)
BG_DARK = "#1a1b26"         # Main canvas background
BG_CARD = "#222336"         # Card surfaces (elevated)
BG_ELEVATED = "#1e1f2a"     # Input fields, dropdowns
BG_HOVER = "#28293c"        # Hover state overlay
BG_DEEPEST = "#0c0d18"      # Sub-cards, nested elements

# Borders
BORDER_SUBTLE = "#2d2e42"   # Default borders
BORDER_DEFAULT = "#454652"  # Emphasized borders
BORDER_FOCUS = "#7c8af4"    # Focus/active state

# Text
TEXT_PRIMARY = "#e2e4f0"    # Main text
TEXT_SECONDARY = "#9a9cb8"  # Secondary text
TEXT_MUTED = "#6b6d85"      # Muted/placeholder text
TEXT_INVERSE = "#0f208b"    # Text on primary buttons

# Accent Colors (Semantic)
ACCENT_PRIMARY = "#7c8af4"          # Primary actions (buttons)
ACCENT_PRIMARY_HOVER = "#9aa4f7"    # Primary hover
ACCENT_PRIMARY_LIGHT = "#bcc2ff"    # Active states, links
ACCENT_SUCCESS = "#82d8ac"          # Success, positive
ACCENT_WARNING = "#f0c878"          # Warning, pending
ACCENT_DANGER = "#e87c8a"           # Danger, error
ACCENT_INFO = "#7dd3e3"             # Info, neutral

# Chart Colors (harmonious palette)
CHART_1 = "#7c8af4"  # Lavender
CHART_2 = "#82d8ac"  # Mint
CHART_3 = "#f0c878"  # Amber
CHART_4 = "#e87c8a"  # Rose
CHART_5 = "#7dd3e3"  # Teal
CHART_6 = "#bcc2ff"  # Light lavender
CHART_7 = "#f4a87c"  # Coral
```

### **Typography Scale**

```python
# Headings
HEADING_XL = "32px, 700 weight, -0.02em letter-spacing"  # Page titles
HEADING_LG = "24px, 700 weight, -0.01em letter-spacing"  # Section titles
HEADING_MD = "18px, 700 weight, -0.01em letter-spacing"  # Card titles
HEADING_SM = "16px, 700 weight, normal letter-spacing"   # Sub-sections

# Body Text
BODY_LG = "14px, 500 weight"    # Large body text
BODY_MD = "13px, 500 weight"    # Standard body text
BODY_SM = "12px, 500 weight"    # Small text

# Labels
LABEL_CAPS = "11px, 700 weight, 0.05em letter-spacing, UPPERCASE"  # Section labels
LABEL_SM = "10px, 500 weight"   # Fine print

# Fonts
FONT_FAMILY = '"Inter", "Segoe UI", "SF Pro Display", sans-serif'
```

### **Spacing System**

Use a consistent 4px base unit:

```python
SPACING_XS = 4    # 4px
SPACING_SM = 8    # 8px
SPACING_MD = 12   # 12px
SPACING_LG = 16   # 16px
SPACING_XL = 20   # 20px
SPACING_2XL = 24  # 24px
SPACING_3XL = 32  # 32px
SPACING_4XL = 40  # 40px
```

### **Border Radius**

```python
RADIUS_SM = 8     # Small elements
RADIUS_MD = 10    # Buttons, inputs
RADIUS_LG = 14    # Cards, containers
RADIUS_XL = 20    # Large cards
RADIUS_FULL = 999 # Pills, circular avatars
```

---

## 🏗️ Application Structure

### **Layout Pattern**

```
┌─────────────────────────────────────────────────────────┐
│ ┌─────────┐ ┌────────────────────────────────────────┐ │
│ │         │ │ TOP BAR (72px height)                  │ │
│ │         │ │ [Search] [Notifications] [User Avatar] │ │
│ │ SIDEBAR │ ├────────────────────────────────────────┤ │
│ │ (240px) │ │                                        │ │
│ │         │ │                                        │ │
│ │  Logo   │ │          PAGE CONTENT                  │ │
│ │  Nav    │ │          (QStackedWidget)              │ │
│ │  Items  │ │                                        │ │
│ │         │ │                                        │ │
│ │  User   │ │                                        │ │
│ │  Card   │ │                                        │ │
│ └─────────┘ └────────────────────────────────────────┘ │
│ STATUS BAR (Bottom, 32px height)                       │
└─────────────────────────────────────────────────────────┘
```

### **File Structure**

```
app/
├── ui/
│   ├── main_window.py          # Root window with sidebar + stack
│   ├── styles/
│   │   └── theme.py            # Color palette + stylesheet
│   ├── widgets/
│   │   ├── sidebar.py          # Navigation sidebar
│   │   ├── top_bar.py          # Top search/user bar
│   │   ├── stat_card.py        # KPI card component
│   │   ├── page_header.py      # Page title component
│   │   ├── animated.py         # Animated widgets
│   │   └── status_pill.py      # Status badge component
│   └── pages/
│       ├── dashboard_page.py   # Each page is a QWidget
│       ├── clients_page.py
│       └── settings_page.py
├── data/
│   ├── database.py             # Database connection
│   └── repositories/           # Data access layer
└── config.py                   # App constants
```

---

## 📋 Component Specifications

### **1. Sidebar Navigation**

**Requirements:**
- Fixed width: 240px
- Dark background (`BG_DARKEST`)
- Logo/brand at top (38x38 icon + app name)
- Navigation buttons with icons
- Active state: lavender accent border-left, light background
- Hover state: slightly lighter background
- User card at bottom (avatar + name + status)

**Code Pattern:**
```python
class Sidebar(QWidget):
    page_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 28, 0, 22)
        
        # Logo + brand
        # Navigation buttons
        # Stretch
        # User card
```

### **2. Top Bar**

**Requirements:**
- Fixed height: 72px
- Search input (360px width, rounded, icon prefix)
- Right side: notification icon, help icon, user avatar
- Horizontal divider between sections

**Code Pattern:**
```python
class TopBar(QWidget):
    search_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(72)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        
        # Search input
        # Stretch
        # Icon buttons
        # Divider
        # User info
```

### **3. Stat Card (KPI Card)**

**Requirements:**
- Minimum height: 132px
- Card background with border
- Label (uppercase, small, muted)
- Large value (30px, bold)
- Icon bubble (40x40, circular, accent color with 12% opacity)
- Optional trend subtext

**Code Pattern:**
```python
class StatCard(QFrame):
    def __init__(self, label: str, value: str, icon: str, accent: str):
        super().__init__()
        self.setObjectName("stat_card")
        # Top row: label + icon bubble
        # Value (large)
        # Optional subtext
        
    def set_value(self, value: str) -> None:
        self._value_label.setText(value)
```

### **4. Page Header**

**Requirements:**
- Large title (32px)
- Subtitle (14px, muted)
- Optional count pill (rounded, bordered)
- Action buttons slot on right

**Code Pattern:**
```python
class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str = ""):
        super().__init__()
        
        layout = QHBoxLayout(self)
        # Left: title + subtitle stacked
        # Right: actions container
```

### **5. Table Widget**

**Requirements:**
- Alternating row colors
- No vertical grid lines
- Header: uppercase, bold, elevated background
- Rounded corners (14px)
- Hover state on rows

**Styling:**
```python
QTableWidget {
    background-color: BG_CARD;
    alternate-background-color: BG_ELEVATED;
    border: 1px solid BORDER_SUBTLE;
    border-radius: 14px;
    selection-background-color: BG_HOVER;
    gridline-color: transparent;
}

QTableWidget::item {
    padding: 12px 8px;
    border-bottom: 1px solid BORDER_SUBTLE;
}

QHeaderView::section {
    background-color: BG_ELEVATED;
    color: TEXT_PRIMARY;
    padding: 12px 8px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
}
```

### **6. Buttons**

**Primary Button:**
```python
QPushButton {
    background-color: ACCENT_PRIMARY;
    color: TEXT_INVERSE;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 13px;
}

QPushButton:hover {
    background-color: ACCENT_PRIMARY_HOVER;
}
```

**Secondary Button:**
```python
QPushButton#secondary {
    background-color: transparent;
    color: TEXT_PRIMARY;
    border: 1px solid BORDER_SUBTLE;
}

QPushButton#secondary:hover {
    background-color: BG_HOVER;
    border: 1px solid ACCENT_PRIMARY;
    color: ACCENT_PRIMARY_LIGHT;
}
```

**Ghost Button:**
```python
QPushButton#ghost {
    background-color: transparent;
    color: TEXT_SECONDARY;
    border: none;
}

QPushButton#ghost:hover {
    background-color: BG_HOVER;
    color: TEXT_PRIMARY;
}
```

### **7. Input Fields**

**Requirements:**
- Background: `BG_ELEVATED`
- Border: 1px `BORDER_SUBTLE`
- Border radius: 10px
- Padding: 9px 14px
- Focus state: border becomes `BORDER_FOCUS`, background `BG_CARD`

```python
QLineEdit, QTextEdit, QComboBox {
    background-color: BG_ELEVATED;
    border: 1px solid BORDER_SUBTLE;
    border-radius: 10px;
    padding: 9px 14px;
    color: TEXT_PRIMARY;
}

QLineEdit:focus {
    border: 1px solid BORDER_FOCUS;
    background-color: BG_CARD;
}

QLineEdit::placeholder {
    color: TEXT_MUTED;
}
```

### **8. Cards**

**Standard Card:**
```python
.card {
    background-color: BG_CARD;
    border: 1px solid BORDER_SUBTLE;
    border-radius: 14px;
    padding: 22px;
}
```

**Animated Card (with hover effect):**
```python
class AnimatedCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "card")
        
    def enterEvent(self, event):
        # Change border to ACCENT_PRIMARY
        
    def leaveEvent(self, event):
        # Restore original border
```

### **9. Status Pills**

**Requirements:**
- Pill-shaped (border-radius: 999px)
- Padding: 4px 12px
- Colored dot + text
- 12% opacity background of accent color

```python
class StatusPill(QWidget):
    def __init__(self, text: str, color: str):
        super().__init__()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        
        # Colored dot
        # Status text
        
        # Background with 12% opacity of color
```

---

## 🎬 Animations

### **Staggered Fade-In (for card rows)**

```python
class StaggeredFadeIn:
    def __init__(self, widgets: list, delay_ms: int = 100, duration_ms: int = 400):
        self._widgets = widgets
        self._effects = []
        
        for widget in widgets:
            effect = QGraphicsOpacityEffect(widget)
            effect.setOpacity(0.0)
            widget.setGraphicsEffect(effect)
            self._effects.append(effect)
    
    def start(self):
        for i, effect in enumerate(self._effects):
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(self._duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            QTimer.singleShot(i * self._delay, anim.start)
```

### **Gradient Progress Bar**

```python
class GradientBar(QWidget):
    def __init__(self, value: float, max_value: float, 
                 color_start: str, color_end: str, height: int = 8):
        super().__init__()
        self.setFixedHeight(height)
        self._value = value
        self._max_value = max_value
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background track
        # Draw gradient fill based on value/max_value ratio
```

### **Button Scale Animation**

```python
class AnimatedButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self._scale = 1.0
        self._scale_anim = QPropertyAnimation(self, b"buttonScale")
        
    def enterEvent(self, event):
        # Scale to 1.03
        
    def leaveEvent(self, event):
        # Scale back to 1.0
        
    def mousePressEvent(self, event):
        # Scale to 0.96
```

---

## 📐 Layout Best Practices

### **Page Layout Template**

Every page should follow this structure:

```python
class SomePage(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)  # Consistent margins
        layout.setSpacing(28)  # Consistent spacing
        
        # 1. Page Header
        self._build_header(layout)
        
        # 2. Stats/KPI Cards (if applicable)
        self._build_stats(layout)
        
        # 3. Main Content
        self._build_content(layout)
        
        # 4. Data Table (if applicable)
        self._build_table(layout)
        
        # Initialize data
        self.refresh()
    
    def _build_header(self, parent_layout):
        """Page title and actions"""
        pass
    
    def refresh(self):
        """Reload data from database"""
        pass
```

### **Responsive Layouts**

- Use `QHBoxLayout` and `QVBoxLayout` with stretch factors
- Set `setSizePolicy()` appropriately:
  - `Expanding` for flexible widgets
  - `Fixed` for sidebars, buttons
  - `Preferred` for cards
- Set minimum sizes, not fixed sizes (except sidebar)

```python
card = QWidget()
card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
card.setMinimumHeight(280)  # Minimum, not fixed
```

---

## 🎯 Accessibility & UX

### **Keyboard Navigation**
- All buttons must be focusable
- Tab order should be logical
- Enter key should trigger primary actions

### **Visual Feedback**
- Hover states on all interactive elements
- Disabled states clearly visible
- Loading states when fetching data
- Empty states with helpful messages

### **Error Handling**
- Graceful fallbacks if data fails to load
- User-friendly error messages
- Don't crash the app on errors

```python
try:
    data = self.repo.get_all()
except Exception as e:
    # Show empty state or error message
    # Don't crash
    pass
```

---

## 🚀 Advanced Features

### **Search Functionality**

```python
class TopBar(QWidget):
    search_changed = Signal(str)
    
    def __init__(self):
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍   Search...")
        self.search.textChanged.connect(self.search_changed.emit)
```

### **Page Navigation**

```python
class MainWindow(QMainWindow):
    def __init__(self):
        self.stack = QStackedWidget()
        self.pages = {}
        
    def show_page(self, page_id: str):
        if page_id in self.pages:
            self.stack.setCurrentWidget(self.pages[page_id])
            if hasattr(self.pages[page_id], "refresh"):
                self.pages[page_id].refresh()
```

### **Form Layouts**

Use `QFormLayout` for clean, aligned forms:

```python
form = QFormLayout()
form.setSpacing(16)
form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

form.addRow("Client Name:", name_input)
form.addRow("Email:", email_input)
form.addRow("Phone:", phone_input)
```

### **Dialogs**

```python
class AddClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Client")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Form fields
        # Button row (Cancel + Save)
        
    def get_data(self) -> dict:
        """Return form data as dictionary"""
        return {...}
```

---

## 📦 Complete Example: Dashboard Page

```python
class DashboardPage(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(28)
        
        # Header
        header = PageHeader(
            title="Dashboard",
            subtitle="Overview of your business"
        )
        layout.addWidget(header)
        
        # KPI Cards Row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(22)
        
        self.card_revenue = StatCard(
            "Total Revenue", 
            "$0", 
            icon="💰",
            accent=Colors.ACCENT_SUCCESS
        )
        self.card_clients = StatCard(
            "Active Clients",
            "0",
            icon="👥",
            accent=Colors.ACCENT_PRIMARY
        )
        
        cards_row.addWidget(self.card_revenue)
        cards_row.addWidget(self.card_clients)
        layout.addLayout(cards_row)
        
        # Recent Items Table
        table_label = QLabel("Recent Activity")
        table_label.setStyleSheet("font-size: 17px; font-weight: 700;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Status", "Date"])
        layout.addWidget(self.table)
        
        # Load data
        self.refresh()
    
    def refresh(self):
        # Update KPI cards
        # Populate table
        pass
```

---

## ✅ Checklist

When building your PySide6 UI, ensure:

- [ ] All colors from the palette are used consistently
- [ ] Spacing follows the 4px base unit system
- [ ] Border radius is consistent (8px, 10px, 14px, 20px)
- [ ] Typography scale is followed
- [ ] All interactive elements have hover states
- [ ] Buttons have consistent height and padding
- [ ] Cards use `AnimatedCard` with hover effect
- [ ] Tables have no vertical grid lines
- [ ] Input fields have focus states
- [ ] Icons/emoji are used appropriately
- [ ] Layouts use proper stretch factors
- [ ] Minimum sizes set, not fixed sizes
- [ ] Code is organized into logical methods
- [ ] Docstrings explain each component
- [ ] `refresh()` method reloads data
- [ ] Error handling prevents crashes
- [ ] Empty states are handled gracefully

---

## 🎨 Design Philosophy

**Modern Minimalism Principles:**

1. **Less is More**: Remove visual clutter, focus on content
2. **Hierarchy**: Use size, weight, color to establish importance
3. **Whitespace**: Generous spacing makes UI breathe
4. **Consistency**: Same spacing, colors, typography everywhere
5. **Feedback**: Every interaction has visual feedback
6. **Depth**: Subtle shadows via borders, not drop-shadows
7. **Performance**: Smooth 60fps animations, no lag
8. **Accessibility**: High contrast text, clear focus states

---

## 📚 Additional Resources

**PySide6 Documentation:**
- Widgets: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/
- Layouts: https://doc.qt.io/qtforpython-6/overviews/layout.html
- Stylesheets: https://doc.qt.io/qt-6/stylesheet-reference.html

**Design Inspiration:**
- Linear (linear.app)
- Notion (notion.so)
- Figma (figma.com)
- VS Code (code.visualstudio.com)

---

## 🚀 Usage

Copy this entire prompt and paste it when asking an AI to build your PySide6 application. Include specific requirements like:

- "Build a client management page with add/edit/delete"
- "Create an invoice generator with PDF export"
- "Make a dashboard with revenue charts"

The AI will follow these exact guidelines to create a consistent, professional UI.
