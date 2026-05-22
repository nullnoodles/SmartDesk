# UI / UX Design Document
## SoloDash — Freelancer Management System

---

## 1. Design Philosophy

SoloDash follows three guiding principles:

1. **Calm productivity** — dark theme, no distracting animations, focused single-window layout
2. **Information density** — show what matters at a glance; never make users hunt for data
3. **Confident guidance** — when AI suggests something, show *why* (reasoning panels, confidence scores)

## 2. Visual Design System

### 2.1 Color Palette (Catppuccin Mocha-inspired)

| Role | Hex | Usage |
|------|-----|-------|
| Background (primary) | `#1e1e2e` | Main app background |
| Background (sidebar) | `#181825` | Sidebar, deeper elements |
| Surface | `#313244` | Cards, dialogs, inputs |
| Surface (hover) | `#45475a` | Hovered/selected states |
| Border | `#313244` | Dividers, table grid |
| Text (primary) | `#cdd6f4` | Body text |
| Text (secondary) | `#a6adc8` | Subtle/muted text |
| Accent (primary) | `#89b4fa` | Buttons, active states, links |
| Success | `#a6e3a1` | Paid invoices, on-time, low risk |
| Warning | `#f9e2af` | Pending, late, medium risk |
| Danger | `#f38ba8` | Overdue, very late, high risk |
| Info | `#cba6f7` | Highlights, AI insights |

### 2.2 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| App title (sidebar) | Segoe UI | 22px | Bold |
| Page heading | Segoe UI | 22px | Bold |
| Section heading | Segoe UI | 16px | Bold |
| Card value | Segoe UI | 24px | Bold |
| Body text | Segoe UI | 13px | Regular |
| Table cells | Segoe UI | 13px | Regular |
| Helper / muted | Segoe UI | 12px | Regular |

### 2.3 Spacing Scale

Based on 4px grid: `4, 8, 12, 16, 20, 24, 32, 48`

- Component padding: 16px
- Card padding: 20px
- Page margins: 30px
- Form row spacing: 12px
- Button padding: 10px vertical, 20px horizontal

### 2.4 Border Radius

- Buttons / Inputs: 8px
- Cards / Dialogs: 12px
- Sidebar buttons: 8px
- Table corners: 8px

### 2.5 Iconography

Emoji-based icons throughout sidebar and key actions for zero-asset overhead:
- 📊 Dashboard
- 👥 Clients
- 📁 Projects
- 🧾 Invoices
- ⏱️ Time Log
- 📝 Contracts
- 🤖 AI Analytics
- ▶ / ⏹ Start / Stop timer
- 📄 PDF upload
- 🔍 Analyze
- 💰 Pricing
- ⏰ Payment
- 📈 Forecast

## 3. Layout Structure

### 3.1 Application Shell

```
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────┬─────────────────────────────────────────────┐ │
│  │         │                                             │ │
│  │ Sidebar │         Page Content (Stacked Widget)       │ │
│  │ 220 px  │              fills remaining space          │ │
│  │  fixed  │                                             │ │
│  │         │                                             │ │
│  │  • Nav  │                                             │ │
│  │  • Logo │                                             │ │
│  │         │                                             │ │
│  └─────────┴─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
   Min size: 1200 × 750 px
```

### 3.2 Sidebar

- Width: 220px (fixed)
- Background: `#181825`
- Top: App name "SoloDash" + tagline "Freelancer Hub"
- Below: 7 navigation buttons stacked vertically
- Active state: filled background `#45475a`, accent text `#89b4fa`
- Hover state: subtle background `#313244`
- Buttons left-aligned with 12px padding, 8px between buttons

## 4. Page Designs

### 4.1 Dashboard Page

```
┌──────────────────────────────────────────────────────────┐
│ Dashboard                                                │
│                                                          │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────┐│
│ │TOTAL EARNED│ │  PENDING   │ │ ACTIVE     │ │ CLIENTS ││
│ │  ₹ X,XX,XXX│ │  ₹ XX,XXX  │ │ PROJECTS   │ │   XX    ││
│ │            │ │            │ │     X      │ │         ││
│ └────────────┘ └────────────┘ └────────────┘ └─────────┘│
│                                                          │
│ Recent Projects                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ Project    │ Client    │ Status   │ Deadline │ Budget││
│ │ ────────────────────────────────────────────────────││
│ │ ...                                                  ││
│ └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

**Interaction:**
- Cards refresh on page entry
- Recent projects table shows top 10
- (Future) Click a row to jump to project detail

### 4.2 Clients Page

```
┌──────────────────────────────────────────────────────────┐
│ Clients                            [Search...] [+ Add]   │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ ID │ Name │ Email │ Phone │ Company │ Created       ││
│ │ ────────────────────────────────────────────────────││
│ │ ...                                                  ││
│ └──────────────────────────────────────────────────────┘│
│                                          [Edit] [Delete]│
└──────────────────────────────────────────────────────────┘
```

**Interaction:**
- Search filters as you type
- Double-click row to edit
- Single-click row + Edit / Delete buttons
- Add opens modal dialog

### 4.3 Projects Page

```
┌──────────────────────────────────────────────────────────┐
│ Projects                              [+ New Project]    │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ ID │ Project │ Client │ Type │ Status │ Deadline    ││
│ │ ────────────────────────────────────────────────────││
│ │ ...                                                  ││
│ └──────────────────────────────────────────────────────┘│
│                                          [Edit] [Delete]│
└──────────────────────────────────────────────────────────┘
```

**Status Color Coding:**
- Not Started: gray
- In Progress: blue
- On Hold: yellow
- Completed: green
- Cancelled: red

### 4.4 Invoices Page

```
┌──────────────────────────────────────────────────────────┐
│ Invoices                              [+ Create Invoice] │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ # │ Inv No │ Client │ Project │ Total │ Due │ Status││
│ │ ────────────────────────────────────────────────────││
│ │ ...                                                  ││
│ └──────────────────────────────────────────────────────┘│
│                                  [Export PDF] [Mark Paid]│
└──────────────────────────────────────────────────────────┘
```

**Status Pill Colors:**
- Paid: green pill
- Unpaid: yellow pill
- Overdue: red pill
- Cancelled: gray pill

### 4.5 Time Log Page

```
┌──────────────────────────────────────────────────────────┐
│ Time Tracking                                            │
│                                                          │
│ Project: [▼ Dropdown]  [Description...] 00:00:00 [▶]    │
│ Manual:  [1.0 hrs ▼]  [+ Add Entry]                      │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ Project │ Start │ End │ Hours │ Description          ││
│ │ ────────────────────────────────────────────────────││
│ │ ...                                                  ││
│ └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

**Timer Display:**
- HH:MM:SS format, ticks every second
- Green color when running, gray when stopped
- Button toggles between ▶ Start and ⏹ Stop

### 4.6 Contracts Page

```
┌──────────────────────────────────────────────────────────┐
│ Contract Risk Analyzer                                   │
│                                                          │
│ ┌─ Upload & Analyze Contract ──────────────────────────┐│
│ │ [Filename]                            [📄 Upload PDF]││
│ │ Project:        [▼ Dropdown]                         ││
│ │ Hourly Rate:    [₹ 500.00]                           ││
│ │ Revisions:      [2]                                  ││
│ │ Timeline:       [14 days]                            ││
│ │ Type:           [▼ Design]                           ││
│ │ ┌──────────────────────────────────────────────────┐││
│ │ │ Contract text appears here after upload...      │││
│ │ │                                                  │││
│ │ └──────────────────────────────────────────────────┘││
│ │                              [🔍 Analyze Risk]       ││
│ └──────────────────────────────────────────────────────┘│
│                                                          │
│ ┌─ Analysis Results ──────────────────────────────────┐ │
│ │ Risk Level: HIGH                                    │ │
│ │ ████████████████░░░░░░░░░  Score: 65/100           │ │
│ │                                                     │ │
│ │ ┌─────────────────────────────────────────────────┐│ │
│ │ │ Check    │ Finding                  │ Score    ││ │
│ │ │ ─────────────────────────────────────────────── ││ │
│ │ │ Rate     │ Rate severely below mkt  │ 25       ││ │
│ │ │ Clause   │ Unlimited revisions      │ 30       ││ │
│ │ │ Clause   │ Full IP rights transfer  │ 25       ││ │
│ │ └─────────────────────────────────────────────────┘│ │
│ └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**Risk Level Color Mapping:**
- LOW: green text + green progress bar fill
- MEDIUM: yellow text + yellow progress bar fill
- HIGH: red text + red progress bar fill

### 4.7 AI Analytics Page

```
┌──────────────────────────────────────────────────────────┐
│ AI Analytics & Predictions                               │
│                                                          │
│ ┌──────────────┬──────────────┬─────────────┐           │
│ │💰 Smart      │⏰ Payment    │📈 Income    │  (Tabs)   │
│ │ Pricing      │  Predictor   │  Forecast   │           │
│ └──────────────┴──────────────┴─────────────┘           │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │  [Currently Active Tab Content]                      ││
│ │                                                      ││
│ │  Form inputs ↑                                       ││
│ │  [Get Suggestion / Predict / Forecast Button]        ││
│ │                                                      ││
│ │  ┌────────────────────────────────────────────────┐ ││
│ │  │ Result Panel                                   │ ││
│ │  │  • Headline value (large, colored)             │ ││
│ │  │  • Reasoning / confidence breakdown            │ ││
│ │  └────────────────────────────────────────────────┘ ││
│ └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

## 5. Component Library

### 5.1 Buttons

| Variant | Background | Text | Use Case |
|---------|-----------|------|----------|
| Primary | `#89b4fa` | Dark | Default actions (Save, Add, Submit) |
| Danger | `#f38ba8` | Dark | Destructive (Delete) |
| Sidebar nav | Transparent | Muted | Navigation |
| Sidebar active | `#45475a` | Accent | Selected page |

### 5.2 Form Inputs

- Background: `#313244`
- Border: 1px `#45475a`
- Border (focus): 1px `#89b4fa`
- Padding: 8px vertical, 12px horizontal
- Border radius: 8px
- Placeholder color: `#a6adc8`

### 5.3 Tables

- Header background: `#313244`
- Alternating rows: `#1e1e2e` and `#181825`
- Selected row: `#45475a`
- Cell padding: 8px
- Grid lines: `#313244`

### 5.4 Cards

- Background: `#313244`
- Border radius: 12px
- Padding: 20px
- Box shadow: subtle, optional

### 5.5 Dialogs

- Modal overlay (semi-transparent)
- Card-like centered panel
- OK / Cancel buttons bottom-right
- Min width: 400px

## 6. User Experience Flows

### 6.1 First-Run Experience

1. App launches → empty dashboard
2. User sees zero-state cards (₹0, 0 clients, etc.)
3. Hint: "Add your first client to get started"
4. User clicks Clients in sidebar → adds first client
5. Then Projects → first project linked to that client
6. Then Invoices → first invoice → exports PDF
7. By third use, user reaches AI Analytics page

### 6.2 Daily Use Pattern

1. Open app → Dashboard shows today's status
2. Start timer for current project (1 click in sidebar)
3. Stop timer when done → auto-logs hours
4. (End of week) Create invoices for completed milestones
5. (Monthly) Check AI Analytics for income forecast

### 6.3 Contract Review Flow (WOW moment)

1. Receive contract from client (email PDF)
2. Open SoloDash → Contracts page
3. Click "Upload PDF" → select file
4. Text auto-extracts into preview
5. Fill in rate / revisions / timeline
6. Click "Analyze Risk"
7. See risk level + per-clause findings
8. Decide: sign, negotiate, or decline

## 7. Accessibility Considerations

- High contrast color choices (WCAG AA minimum)
- Keyboard navigation: Tab order through forms; Enter submits
- Font sizes never smaller than 12px
- Buttons minimum 32px tall (touch-friendly)
- Form labels always paired with inputs (QFormLayout)
- Error messages descriptive and action-oriented

## 8. Responsive Behavior

- Minimum window size: 1200 × 750 px
- Sidebar fixed at 220px
- Page content fills remaining space
- Tables horizontally scroll if too narrow
- Dialogs centered, fixed width

## 9. Empty States

| Page | Empty State Message |
|------|---------------------|
| Dashboard | "Welcome to SoloDash. Start by adding a client." |
| Clients | "No clients yet. Click + Add Client to begin." |
| Projects | "No projects yet. Add a client first, then create a project." |
| Invoices | "No invoices yet. Create one from the Invoices page." |
| Time Log | "No time logged. Start the timer or add a manual entry." |
| Analytics | "Need at least 5 paid invoices for ML predictions to work." |

## 10. Future Design Improvements

- Custom SVG icons (replace emoji) for consistent rendering
- Light theme toggle
- Compact / comfortable layout setting
- Customizable dashboard widgets
- Animated chart transitions
- Toast notifications for background operations (PDF export complete, etc.)
