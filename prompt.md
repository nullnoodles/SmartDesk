"Apply these design tokens to the existing SmartDesk Invoices page in PySide6. Do NOT change any layout, components, or functionality — only update visual styling.

Background Colors
page-background: #12131d
sidebar-background: #1a1b26
card-background: #1a1b26
card-hover-background: #282935 (surface-container-high)
table-background: #1a1b26
table-row-alternate: rgba(26, 27, 38, 0.3) (surface-container-low/30)
table-row-hover: rgba(124, 138, 244, 0.04)
button-primary: #7c8af4
button-secondary-background: transparent
filter-active-background: #333440 (surface-container-highest)
filter-inactive-background: transparent
filter-hover-background: #1e1f2a (surface-container)
input-background: #1a1b26
scrollbar-track: #12131d
scrollbar-thumb: #2d2e42
Text Colors
primary-text: #e2e1f1
secondary-text: #9a9cb8
muted-text: #6b6d85
link-text: #7c8af4
link-hover: #7c8af4 (with underline)
error-text: #e87c8a (status-danger)
warning-text: #f0c878 (status-warning)
success-text: #82d8ac (secondary)
Border Colors
card-border: rgba(69, 70, 82, 0.3) (outline-variant/30)
input-border: rgba(69, 70, 82, 0.3) (outline-variant/30)
table-header-border: rgba(69, 70, 82, 0.3) (outline-variant/30)
table-row-border: rgba(69, 70, 82, 0.1) (outline-variant/10)
button-border: #908f9e (outline-variant)
divider: rgba(69, 70, 82, 0.3) (outline-variant/30)
active-tab-border: #7c8af4
Border Widths
default: 1px
active-tab-left: 4px
Border Radius
cards: 8px
buttons: 8px
inputs: 8px
badges-full: 9999px (full)
chart-bars-top: 4px
avatar: 9999px (full)
icon-buttons: 9999px (full)
status-badges: 9999px (full)
Font Sizes
page-title (headline-xl): 32px
section-title (headline-lg): 24px
card-value (headline-lg): 24px
body-lg: 16px
body-md: 14px
body-sm: 13px
table-header (label-caps): 11px
status-badge: 10px
tabular-nums: 14px
Font Weights
page-title: 700
section-title: 700
card-value: 700
card-label: 700 (label-caps)
table-header: 700
body-lg: 500
body-md: 400
body-sm: 400
button-primary: 700 (bold)
tabular-nums: 500
Padding
cards: 24px
table-rows: 16px 24px (py-4 px-6)
table-header: 16px 24px (py-4 px-6)
buttons-medium: 8px 16px (py-2 px-4)
buttons-large: 10px 24px (py-2.5 px-6)
status-badge: 4px 10px (py-1 px-2.5)
sidebar-nav-items: 12px 24px (py-3 px-[24px])
main-content: 32px
Button Colors
primary-button-bg: #7c8af4
primary-button-text: #12131d
primary-button-hover: opacity 0.9
secondary-button-bg: transparent
secondary-button-border: #908f9e (outline-variant)
secondary-button-text: #e2e1f1
secondary-button-hover-bg: #1e1f2a (surface-container)
action-button-bg: rgba(130, 216, 172, 0.2) (secondary-container/20)
action-button-border: rgba(130, 216, 172, 0.3) (secondary/30)
action-button-text: #82d8ac (secondary)
action-button-hover-bg: rgba(130, 216, 172, 0.3) (secondary-container/30)
Status Badge Colors
Paid (Success)
background: rgba(130, 216, 172, 0.2) (secondary-container/20)
text: #82d8ac (secondary)
dot: #82d8ac (secondary)
Unpaid (Warning)
background: rgba(240, 200, 120, 0.1) (status-warning/10)
text: #f0c878 (status-warning)
dot: #f0c878 (status-warning)
Overdue (Danger)
background: rgba(232, 124, 138, 0.1) (status-danger/10)
text: #e87c8a (status-danger)
dot: #e87c8a (status-danger)
Hover States
card-hover: #282935 (surface-container-high)
table-row-hover: rgba(124, 138, 244, 0.04)
button-hover: opacity 0.9
nav-item-hover: #282935 (surface-container-high)
icon-button-hover-text: #7c8af4
chart-bar-hover: brightness(1.1)
Additional
selection-background: #7c8af4 (primary-container)
selection-text: #061987 (on-primary-container)
active-nav-background: rgba(124, 138, 244, 0.1) (#7c8af4/10)
avatar-dot-size: 6px (w-1.5 h-1.5)
scrollbar-width: 6px
scrollbar-border-radius: 10px

Apply in this order:
1. Page background color
2. Card backgrounds and borders
3. Stat card internal styling — label, value, subtitle colors and fonts
4. Table styling — background, header, rows, alternating rows, hover
5. Status badge colors per status
6. Button styles
7. Search bar style
8. Filter tab styles — default, active, hover
9. Set background: transparent and border: none on all QLabel children inside cards
Rules:

Set all styles directly in Python using setStyleSheet on individual widgets
Do not add any global QWidget or QFrame rules to style.qss
Do not change any database queries, layouts, or functionality
Run app after, verify no visual regressions, commit with message 'style: apply HTML design tokens to Invoices page'"