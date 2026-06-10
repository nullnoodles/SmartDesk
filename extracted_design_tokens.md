# EXTRACTED DESIGN TOKENS FROM HTML

## COLORS

### Background Colors
- #12131d - main background (surface-dim, background, surface)
- #12131a - bg-deep, scrollbar track
- #1a1b26 - surface-container-low, hover states
- #1e1f2a - surface-container
- #282935 - surface-container-high, badge background
- #333440 - surface-container-highest, surface-variant
- #383844 - surface-bright
- #0c0d18 - surface-container-lowest

### Text Colors
- #e2e1f1 - on-background, on-surface, body text
- #e2e4f0 - text-primary, on-surface-variant (table headers)
- #9a9cb8 - text-secondary, muted text, placeholders
- #6b6d85 - text-muted
- #c6c5d5 - on-surface-variant (archived text)

### Primary Colors
- #bcc2ff - primary, primary-fixed-dim, active text
- #7c8af4 - primary-container, button background
- #061987 - on-primary-container, button text
- #0f208b - on-primary
- #000c61 - on-primary-fixed
- #4654bb - inverse-primary
- #dfe0ff - primary-fixed

### Secondary Colors
- #82d8ac - secondary, secondary-fixed-dim, success/completed
- #006a47 - secondary-container
- #003824 - on-secondary
- #002113 - on-secondary-fixed
- #005236 - on-secondary-fixed-variant
- #9df4c7 - secondary-fixed
- #90e6ba - on-secondary-container

### Tertiary Colors
- #7dd3e3 - tertiary, tertiary-fixed-dim, active status
- #459fad - tertiary-container
- #00363d - on-tertiary
- #001f24 - on-tertiary-fixed
- #004f58 - on-tertiary-fixed-variant
- #003138 - on-tertiary-container
- #9bf0ff - tertiary-fixed

### Status Colors
- #e87c8a - status-danger, error, delayed
- #f0c878 - status-warning, revision
- #ffb4ab - error
- #690005 - on-error
- #ffdad6 - on-error-container
- #93000a - error-container

### Border/Outline Colors
- #454652 - outline-variant, borders
- #908f9e - outline
- #2d2e42 - scrollbar thumb
- #2f303b - inverse-on-surface

### Special Effects
- rgba(188,194,255,0.4) - primary shadow
- rgba(188,194,255,0.10) - primary active background
- rgba(188,194,255,0.05) - decorative glow start
- rgba(188,194,255,0.10) - decorative glow hover
- rgba(69,70,82,0.30) - card border opacity
- rgba(69,70,82,0.20) - table divider
- rgba(26,27,38,0.20) - alternating row background
- rgba(26,27,38,0.50) - table header background

### Avatar/Badge Backgrounds
- rgba(125,211,227,0.30) - tertiary avatar (MP)
- rgba(124,138,244,0.30) - primary avatar (SC)
- rgba(232,124,138,0.30) - danger avatar (DK)

## FONT SIZES & WEIGHTS

### Display/Headlines
- 40px / 48px line-height / -0.02em / 700 weight - display
- 32px / 40px line-height / -0.02em / 700 weight - headline-xl (Projects title)
- 24px / 32px line-height / -0.01em / 700 weight - headline-lg (stat card values)
- 24px / 30px line-height / -0.01em / 700 weight - headline-lg-mobile
- 18px / 24px line-height / 0em / 600 weight - title-md

### Body Text
- 16px / 24px line-height / 500 weight - body-lg (button text, insight title)
- 14px / 20px line-height / 400 weight - body-md (nav items, table rows)
- 13px / 18px line-height / 400 weight - body-sm (user name, insight text, footer buttons)

### Labels
- 14px / 20px line-height / 500 weight - tabular-nums (badge, dates, ID column)
- 12px / 16px line-height / 0.05em / 600 weight - label-sm
- 11px / 16px line-height / 0.05em / 700 weight - label-caps (stat card labels, table headers, PRO ACCOUNT)

### Special
- 11px - project subtitle text
- 10px - avatar initials
- 20px - icon sizes (action buttons)
- 24px - icon sizes (nav, header)

## SPACING VALUES

### Layout Spacing
- 32px - main-padding (content padding)
- 24px - card-gap (gap between cards)
- 16px - gutter (general gap)
- 12px - sm (small gap)
- 8px - xs (extra small gap)
- 4px - base (minimum spacing)

### Component Spacing
- 230px - sidebar-width
- 80px (20 * 4px) - top app bar height
- 44px - tap-target-min (button height)
- 40px - New Project button height
- 40px - icon box (stat cards)
- 32px (8 * 4px) - logo icon size
- 24px - avatar size (table rows)
- 20px - safe-area-inset

### Padding Values
- px-6 (24px) - table cell horizontal padding
- py-4 (16px) - table header vertical padding
- py-row-padding (10px) - table row vertical padding
- p-6 (24px) - stat card padding
- px-main-padding (32px) - header horizontal padding
- py-main-padding (32px) - sidebar vertical padding
- px-2.5 (10px) - badge horizontal padding
- py-0.5 (2px) - badge vertical padding
- px-3 (12px) - status badge horizontal padding
- py-1 (4px) - status badge vertical padding
- px-4 (16px) - footer button horizontal padding
- py-2 (8px) - footer button, search input vertical padding
- p-2 (8px) - icon button padding

### Margins
- mb-10 (40px) - logo block bottom margin
- mb-8 (32px) - header section bottom margin
- mb-4 (16px) - stat card row 1 bottom margin
- mb-1 (4px) - title row bottom margin, stat card label bottom margin
- mt-1 (4px) - Creative Workspace top margin
- mt-auto - nav push to bottom
- gap-3 (12px) - logo row, title row, user info
- gap-2 (8px) - client avatar row, action buttons
- gap-1 (4px) - pagination buttons, CTA row
- gap-4 (16px) - header icons, footer actions
- gap-6 (24px) - header right cluster

## BORDER RADIUS

- 0.25rem (4px) - DEFAULT border-radius
- 0.5rem (8px) - lg (buttons, cards, icon boxes)
- 0.75rem (12px) - xl (main cards, table container, search input, toast)
- 9999px - full (circular badges, avatars, status pills)
- 10px - scrollbar thumb border-radius

## COMPONENT DIMENSIONS

### Window
- 1280px width
- 1024px height
- Not resizable

### Layout Regions
- Sidebar: 0,0, 230px width, 1024px height
- TopAppBar: 230px x, 0 y, 1050px width, 80px height
- MainContent: 230px x, 80px y, 1050px width, 944px height

### Buttons
- 40px height (New Project button, icon buttons in header)
- 32px height (pagination chevron buttons)
- min 44px - tap target minimum

### Icons
- 24px - navigation icons, header icons
- 20px - action icons (edit, delete)
- 16px - small icons (CTA arrow, footer button icons)
- 32px - logo icon box

### Avatars
- 40px - user avatar (top bar)
- 24px - client avatars (table rows)
- 6px - avatar initials

### Stat Cards
- 40px × 40px - icon boxes
- Grid: col-span-8 (left 3 cards), col-span-4 (insight card)
- Grid: grid-cols-3 (3 stat cards)

### Table
- 52px - row height (py-row-padding × 2 + content)
- 6px - scrollbar width
- Column widths: ID (90px), PROJECT (240px), CLIENT (160px), TYPE (120px), STATUS (120px), DEADLINE (130px), ACTIONS (100px)

### Decorative Elements
- 160px × 160px - insight card glow circle
- 1px - divider width
- 4px - active nav border-left width

## TRANSITIONS & ANIMATIONS

- 200ms - standard transition (nav hover, stat card hover)
- 500ms - toast dismiss
- 700ms - decorative glow transition
- ease-out - toast appear
- ease-in - toast dismiss
- active:scale-[0.98] - button press
- active:scale-95 - footer button press
- hover:brightness-110 - New Project button
- opacity-0 to opacity-100 - action buttons on row hover
- translateY +16px to 0 - toast appear animation
- translateY 0 to +16px - toast dismiss animation

## SHADOWS

- shadow-lg - New Project button
- shadow-2xl - toast notification
- shadow-[0_0_15px_rgba(188,194,255,0.4)] - logo icon
- shadow-primary/10 - New Project button specific
- blur-3xl - decorative glow effect
- blur 30 - decorative glow (from spec)

## Z-INDEX

- z-50 - sidebar
- z-40 - top app bar
- z-[60] - toast container (floating action layer)
- z-10 - insight card content (relative to glow)
