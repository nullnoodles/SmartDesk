# Extract Stitch Design System → PySide6 QSS + Layout Rebuild

Rebuild the SmartDesk PySide6 UI to **exactly** match the "Studio Graphite" design system extracted from the Stitch MCP project, moving all styling into a `.qss` file and fixing layouts to conform to the design spec.

## Design System Extracted from Stitch

### Colors (Studio Graphite Palette)
| Token | Hex | Usage |
|---|---|---|
| `bg-deep` / Level 0 | `#12131a` | Sidebar background |
| `surface-container-low` / Level 1 | `#1a1b26` | Main canvas |
| `bg-surface` / Level 2 | `#222336` | Cards, inputs |
| `surface-container` | `#1e1f2a` | Table headers, elevated inputs |
| `surface-container-high` | `#282935` | Hover overlays |
| `surface-container-lowest` | `#0c0d18` | Sub-card / deepest |
| `border-subtle` | `#2d2e42` | Card borders |
| `outline-variant` | `#454652` | Default borders |
| `primary-container` | `#7c8af4` | Primary buttons (lavender-blue) |
| `primary` | `#bcc2ff` | Active text/icons |
| `secondary` | `#82d8ac` | Success (mint) |
| `status-warning` | `#f0c878` | Warning (amber) |
| `status-danger` | `#e87c8a` | Danger (rose) |
| `tertiary` | `#7dd3e3` | Info (teal) |
| `text-primary` | `#e2e4f0` | Body text |
| `text-secondary` | `#9a9cb8` | Muted text |
| `text-muted` | `#6b6d85` | Tertiary text |
| `on-primary` | `#0f208b` | Text on primary buttons |

### Typography (All Inter)
| Role | Size | Weight | Line Height | Letter Spacing |
|---|---|---|---|---|
| `headline-xl` | 32px | 700 | 40px | -0.02em |
| `headline-lg` | 24px | 700 | 32px | -0.01em |
| `body-lg` | 16px | 500 | 24px | — |
| `body-md` | 14px | 400 | 20px | — |
| `body-sm` | 13px | 400 | 18px | — |
| `label-caps` | 11px | 700 | 16px | 0.05em |
| `tabular-nums` | 14px | 500 | 20px | — |

### Spacing
| Token | Value |
|---|---|
| `sidebar-width` | 230px |
| `main-padding` | 32px |
| `gutter` | 16px |
| `row-padding` | 10px |
| `card-gap` | 24px |

### Shapes
| Element | Radius |
|---|---|
| Cards | 14px |
| Buttons & Inputs | 10px |
| Sidebar container | 14px |

### Component Specs (from Stitch design)
- **Primary Button**: `#7c8af4` bg, `#0f208b` text, 10px radius, `padding: 10px 22px`, min-height 38px
- **Ghost Button**: transparent bg, `#2d2e42` 1px border, `#e2e4f0` text
- **Cards**: `#222336` bg, `#2d2e42` 1px border, 14px radius, 24px internal padding
- **Inputs**: `#1e1f2a` bg, `#2d2e42` 1px border, focus = `#7c8af4` 1px border
- **Sidebar nav active**: 3px left `#7c8af4` bar, `rgba(124,138,244,0.10)` bg, `#bcc2ff` text
- **Tables**: no vertical grid, `#e2e4f0` header text (11px caps), alternating row bg `#1e1f2a`

### Screens (Desktop, 1280×1024+)
From Stitch: Dashboard, Clients, Projects, Invoices, Time Log, Contracts, AI Analytics, Settings

---

## Proposed Changes

### 1. New QSS Stylesheet File

#### [NEW] [style.qss](file:///d:/Code/Tool/Smartdesk/app/ui/styles/style.qss)

A standalone `.qss` file containing **all** styling, directly translating every design token above. This replaces inline `setStyleSheet()` calls throughout the codebase. The file will contain sections for:

- Global widget defaults (colors, font-family)
- Sidebar (`#sidebar`) — fixed 230px, `#12131a` bg, 14px radius
- Top bar (`#top_bar`) — `#12131a` bg, 80px height
- Cards (`.card`, `#stat_card`) — `#222336` bg, `#2d2e42` border, 14px radius, 24px padding
- Buttons (primary, secondary, ghost, danger, success, icon)
- Inputs (QLineEdit, QTextEdit, QComboBox, etc.)
- Tables (clean style, alternating rows, caps headers)
- Labels (heading, heading-lg, subheading, card_title, card_value, caps)
- Scrollbars (8px, rounded, subtle)
- Tab widget, progress bars, menus, tooltips, dialogs, group boxes
- Status bar

---

### 2. Theme Loader Rewrite

#### [MODIFY] [theme.py](file:///d:/Code/Tool/Smartdesk/app/ui/styles/theme.py)

- Keep the `Colors` class (Python code still needs color constants for charts/dynamic widgets)
- Remove the `DARK_STYLESHEET` string entirely
- Rewrite `apply_dark_theme()` to:
  1. Load `Inter` font via `QFontDatabase.addApplicationFont()` (from Google Fonts TTF bundled in `assets/fonts/`)
  2. Read `style.qss` from disk
  3. Apply via `app.setStyleSheet()`

---

### 3. Main Window Layout Fix

#### [MODIFY] [main_window.py](file:///d:/Code/Tool/Smartdesk/app/ui/main_window.py)

- Wrap the entire right-column content area inside `QScrollArea(widgetResizable=True)`
- Set `setMinimumWidth(1280)` on the main window (already done)
- Remove all inline `setStyleSheet()` calls — rely on QSS object names
- Ensure spacing: root margins `12px`, sidebar fixed `230px` (down from 260), `card-gap=24px`

---

### 4. Sidebar Width Fix

#### [MODIFY] [sidebar.py](file:///d:/Code/Tool/Smartdesk/app/ui/widgets/sidebar.py)

- Change `setFixedWidth(260)` → `setFixedWidth(230)` to match design spec
- Remove all inline `setStyleSheet()` calls — assign object names and let QSS handle it
- Keep signal/slot logic, button group, and nav structure identical

---

### 5. Widget Inline Style Cleanup

#### [MODIFY] [top_bar.py](file:///d:/Code/Tool/Smartdesk/app/ui/widgets/top_bar.py)
- Remove inline styles, use object names (`#top_bar`, `#search_input`, `#mode_pill`, etc.)

#### [MODIFY] [stat_card.py](file:///d:/Code/Tool/Smartdesk/app/ui/widgets/stat_card.py)
- Remove inline styles, use object names
- Ensure `setMinimumHeight(150)` and `setMinimumWidth(200)` remain

#### [MODIFY] [page_header.py](file:///d:/Code/Tool/Smartdesk/app/ui/widgets/page_header.py)
- Remove inline styles, reference QSS via object names

#### [MODIFY] [status_pill.py](file:///d:/Code/Tool/Smartdesk/app/ui/widgets/status_pill.py)
- Keep dynamic color logic (status pills need per-instance accent colors)

#### [MODIFY] [animated.py](file:///d:/Code/Tool/Smartdesk/app/ui/widgets/animated.py)
- Remove inline card styling, let `#animated_card` QSS rule handle it

---

### 6. Page Layout Fixes (All Pages)

Every page file will be updated to:
- Wrap content in `QScrollArea(widgetResizable=True)` (dashboard already does this)
- Use `QVBoxLayout` / `QHBoxLayout` with spacing `24px` (card-gap) and margins `32px` (main-padding)
- Remove inline `setStyleSheet()` calls
- Set `setMinimumHeight` / `setMinimumWidth` on all cards and buttons
- Desktop-only layout: multi-column grids, **no** single-column stacks

Files:
- [dashboard_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/dashboard_page.py)
- [clients_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/clients_page.py)
- [projects_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/projects_page.py)
- [invoices_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/invoices_page.py)
- [time_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/time_page.py)
- [contracts_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/contracts_page.py)
- [analytics_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/analytics_page.py)
- [settings_page.py](file:///d:/Code/Tool/Smartdesk/app/ui/pages/settings_page.py)

---

### 7. Font Bundle

#### [NEW] `assets/fonts/Inter-Regular.ttf`, `Inter-Medium.ttf`, `Inter-Bold.ttf`
Download Inter font family TTF files and load them via `QFontDatabase` in `theme.py`.

---

## User Review Required

> [!IMPORTANT]
> **Inline styles that MUST remain inline**: Certain widgets need per-instance dynamic colors (e.g., `StatusPill` gets a color based on status, `StatCard` icon bubble accent varies, chart colors). These will keep minimal inline styling for the dynamic parts only, while structural styles (padding, radius, sizing) move to QSS.

> [!IMPORTANT]
> **Sidebar width change**: The Stitch design spec says 230px but the current code uses 260px. This plan changes it to 230px per spec. If you prefer 260px, let me know.

## Open Questions

1. **Font files**: Should I download Inter TTF files from Google Fonts and bundle them in `assets/fonts/`, or rely on system-installed Inter? Bundling guarantees the correct font regardless of system.

## Verification Plan

### Automated Tests
- Run `python main.py` and visually verify all 8 pages render correctly
- Confirm QSS loads without errors
- Check sidebar width = 230px, card borders visible, correct colors

### Manual Verification
- Compare each page against the Stitch screen screenshots
- Verify scroll behavior on all pages
- Confirm no inline styles remain (grep for `setStyleSheet`)
