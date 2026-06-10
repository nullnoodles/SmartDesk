Build a desktop app window with the following exact specifications:

WINDOW
- Title: SmartDesk - Projects
- Size: 1280 x 1024
- Theme: dark
- Background: #12131d
- Font: Inter
- Not resizable

---

LAYOUT
The window has 3 fixed regions:
1. SideNavBar — fixed left, 0,0, width 230, height 1024
2. TopAppBar — fixed top, x 230, y 0, width 1050, height 80
3. MainContent — scrollable, x 230, y 80, width 1050, height 944, padding 32, background #12131d

---

SIDEBAR
x 0, y 0, width 230, height 1024
background #12131a
padding-top 32, padding-bottom 32
layout vertical

LOGO BLOCK
margin-left 24, margin-right 24, margin-bottom 40
layout vertical

  Logo Row — layout horizontal, align center, gap 12
    Icon Box — width 32, height 32, border-radius 8, background #bcc2ff, shadow 0 0 15px rgba(188,194,255,0.4)
      Icon — fluid, size 20, color #061987, filled
    Text — "SmartDesk", Inter 24px Bold, color #bcc2ff

  Text — "Creative Workspace", Inter 11px Bold, color #9a9cb8, letter-spacing 0.05em, margin-left 44, margin-top 4

NAV ITEMS
layout vertical, full width

Each nav item:
  height 48, padding-left 24, padding-right 24
  layout horizontal, align center, gap 12
  icon size 24
  text Inter 14px Regular
  default: background transparent, text #9a9cb8, icon #9a9cb8
  hover: background #1a1b26, text #bcc2ff, icon #bcc2ff
  cursor pointer, transition 200ms

Nav item 1 — icon dashboard, label Dashboard, state default
Nav item 2 — icon group, label Clients, state default
Nav item 3 — icon folder_open, label Projects, state ACTIVE
  ACTIVE style: background rgba(188,194,255,0.10), text #bcc2ff, icon #bcc2ff, border-left 4px solid #bcc2ff, icon filled
Nav item 4 — icon receipt_long, label Invoices, state default
Nav item 5 — icon timer, label Time Log, state default
Nav item 6 — icon description, label Contracts, state default
Nav item 7 — icon analytics, label AI Analytics, state default
Nav item 8 — icon settings, label Settings, state default

---

TOP APP BAR
x 230, y 0, width 1050, height 80
background #12131d
padding-left 32, padding-right 32
layout horizontal, align center, justify space-between

SEARCH BAR
width 480, height 44
background #1a1b26
border 1px solid #454652
border-radius 12
padding-left 48, padding-right 16, padding-top 10, padding-bottom 10
placeholder "Search projects, tasks, or files..."
placeholder-color #9a9cb8
text Inter 14px Regular, color #e2e1f1
left icon: search, size 20, color #9a9cb8, positioned absolute left 16px vertically centered
focus state: border 1px solid #bcc2ff

RIGHT CLUSTER
layout horizontal, align center, gap 24

  Button — icon notifications, size 24, color #9a9cb8, width 40, height 40, border-radius 8, hover background #1e1f2a
  Button — icon help_outline, size 24, color #9a9cb8, width 40, height 40, border-radius 8, hover background #1e1f2a

  Divider — width 1, height 32, background #454652

  User Info — layout vertical, align flex-end
    Text "Alex Rivera" — Inter 13px Bold, color #e2e1f1
    Text "PRO ACCOUNT" — Inter 11px Bold, color #9a9cb8, letter-spacing 0.05em

  Avatar — width 40, height 40, border-radius 9999, border 1px solid #454652
    image url https://lh3.googleusercontent.com/aida-public/AB6AXuDzk6OUYLak-d4Efb1mKqtgC4doDiTZKjg55-s5DAn3VvG7_ntHJEmej1V3fX37_l60oiCZQkm7EH7OCZgLjjqOx0XpDvhwAz49Ovf7SYS0s-5OIxug4rdTsZWnsO8nk2purKo0XBiHNfIg0R8e59neWq5H02NVuh0Dv_8I-ct99tJ348FznaKfZKsbw9mPkECNEVej285LhyHHPjF5LcwCK6G8zyxfo8tZ2M790EZVIRLKP2iVr6B_DX95GAGERYXnDGwc88kpRU0
    object-fit cover

---

MAIN CONTENT
x 230, y 80, width 1050, height 944
background #12131d
padding 32
layout vertical, gap 32
overflow-y scroll
scrollbar width 6, track #12131a, thumb #2d2e42, thumb-hover #454652, thumb-border-radius 10

---

PAGE HEADER
layout horizontal, justify space-between, align flex-end

LEFT BLOCK
layout vertical, gap 4

  Title Row — layout horizontal, align center, gap 12
    Text "Projects" — Inter 32px Bold, color #e2e4f0, letter-spacing -0.02em, line-height 40px
    Badge "12 Total" — background #282935, border 1px solid #454652, border-radius 9999, padding 2px 10px, Inter 14px Medium, color #9a9cb8

  Text "Manage and track your active production pipeline." — Inter 14px Regular, color #9a9cb8, line-height 20px

RIGHT BLOCK
  Button — layout horizontal, align center, gap 8, height 40, background #7c8af4, border-radius 8, padding-left 24, padding-right 24
    Icon add_circle, size 20, color #061987
    Text "New Project" — Inter 16px Bold, color #061987
    hover brightness 1.10
    press scale 0.98
    shadow 0 8px 24px rgba(188,194,255,0.10)
    cursor pointer

---

STATS ROW
layout horizontal, gap 24, align stretch

LEFT STATS GROUP
layout horizontal, gap 24, flex 8

STAT CARD TEMPLATE
background #1a1b26
border 1px solid rgba(69,70,82,0.30)
border-radius 12
padding 24
flex 1
layout vertical, gap 16
hover background #282935
cursor default

  STAT CARD 1
    Row 1 — layout horizontal, justify space-between, align center
      Icon Box — width 40, height 40, border-radius 8, background rgba(125,211,227,0.10)
        Icon rocket_launch, size 24, color #7dd3e3
      Text "+12%" — Inter 14px Medium, color #82d8ac
    Text "ACTIVE VELOCITY" — Inter 11px Bold, color #9a9cb8, letter-spacing 0.05em, uppercase
    Text "8 Current" — Inter 24px Bold, color #e2e4f0

  STAT CARD 2
    Row 1 — layout horizontal, justify space-between, align center
      Icon Box — width 40, height 40, border-radius 8, background rgba(240,200,120,0.10)
        Icon hourglass_empty, size 24, color #f0c878
      Text "2 Late" — Inter 14px Medium, color #e87c8a
    Text "UPCOMING DEADLINES" — Inter 11px Bold, color #9a9cb8, letter-spacing 0.05em, uppercase
    Text "48 Hours" — Inter 24px Bold, color #e2e4f0

  STAT CARD 3
    Row 1 — layout horizontal, justify space-between, align center
      Icon Box — width 40, height 40, border-radius 8, background rgba(188,194,255,0.10)
        Icon payments, size 24, color #bcc2ff
      Text "$12.4k" — Inter 14px Medium, color #82d8ac
    Text "PIPELINE VALUE" — Inter 11px Bold, color #9a9cb8, letter-spacing 0.05em, uppercase
    Text "$42,800" — Inter 24px Bold, color #e2e4f0

INSIGHT CARD
flex 4
background #1a1b26
border 1px solid rgba(69,70,82,0.30)
border-radius 12
padding 24
layout vertical, gap 12
overflow hidden
position relative

  Decorative Glow — circle, width 160, height 160, background rgba(188,194,255,0.05), blur 30, position absolute bottom -40 right -40, hover background rgba(188,194,255,0.10), transition 700ms

  Text "Workspace Insight" — Inter 16px Medium, color #e2e4f0

  Text — Inter 13px Regular, color #9a9cb8, line-height 18px
    content: "You're currently at 85% capacity. AI suggests shifting the "
    then BOLD "Apex Mobile"
    then " deadline to avoid burnout."

  CTA Row — layout horizontal, align center, gap 4, cursor pointer, hover underline
    Text "OPTIMIZE SCHEDULE" — Inter 11px Bold, color #bcc2ff, letter-spacing 0.05em
    Icon arrow_forward, size 16, color #bcc2ff

---

PROJECTS TABLE
background #1a1b26
border 1px solid rgba(69,70,82,0.30)
border-radius 12
overflow hidden
layout vertical

TABLE HEADER
background rgba(26,27,38,0.50)
padding 16px 24px
border-bottom 1px solid rgba(69,70,82,0.20)
layout horizontal, align center

Columns:
  ID        width 90   Inter 11px Bold, color #e2e4f0, uppercase, letter-spacing 0.05em
  PROJECT   width 240  Inter 11px Bold, color #e2e4f0, uppercase, letter-spacing 0.05em
  CLIENT    width 160  Inter 11px Bold, color #e2e4f0, uppercase, letter-spacing 0.05em
  TYPE      width 120  Inter 11px Bold, color #e2e4f0, uppercase, letter-spacing 0.05em
  STATUS    width 120  Inter 11px Bold, color #e2e4f0, uppercase, letter-spacing 0.05em
  DEADLINE  width 130  Inter 11px Bold, color #e2e4f0, uppercase, letter-spacing 0.05em
  ACTIONS   width 100  Inter 11px Bold, color #e2e4f0, uppercase, letter-spacing 0.05em, align right

TABLE ROWS
row height 52
row padding 10px 24px
row divider 1px solid rgba(69,70,82,0.20)
odd rows background transparent
even rows background rgba(26,27,38,0.20)
hover background #1a1b26

ACTION BUTTONS (inside every row, right side)
hidden by default, visible on row hover
layout horizontal, align center, justify flex-end, gap 8

  Edit button — icon edit_note, size 20, color #9a9cb8, hover color #bcc2ff, padding 8, border-radius 8, hover background #1e1f2a
  Delete button — icon delete_outline, size 20, color #9a9cb8, hover color #e87c8a, padding 8, border-radius 8, hover background #1e1f2a

STATUS BADGE TEMPLATE
border-radius 9999, padding 4px 12px, Inter 12px Bold

  Active    background rgba(125,211,227,0.20)  border 1px solid rgba(69,159,173,0.30)   color #7dd3e3
  Completed background rgba(130,216,172,0.20)  border 1px solid rgba(0,106,71,0.30)     color #82d8ac
  Revision  background rgba(240,200,120,0.10)  border 1px solid rgba(240,200,120,0.30)  color #f0c878
  Delayed   background rgba(232,124,138,0.20)  border 1px solid rgba(232,124,138,0.30)  color #e87c8a
  Archived  background rgba(69,70,82,0.40)     border 1px solid rgba(69,70,82,0.60)     color #c6c5d5

AVATAR TEMPLATE
width 24, height 24, border-radius 9999
type initials: centered text Inter 10px Regular
type image: object-fit cover

ROW 1
background transparent
  ID — "SD-012" — Inter 14px Medium, color #9a9cb8
  Project — layout vertical, gap 2
    "Brand Identity Redesign" — Inter 14px Regular, color #e2e4f0
    "Creative Suite Expansion" — Inter 11px Regular, color #9a9cb8
  Client — layout horizontal, align center, gap 8
    Avatar initials "MP" background rgba(69,159,173,0.30) text-color #7dd3e3
    "Meera Patel" — Inter 14px Regular, color #9a9cb8
  Type — "Branding" — Inter 13px Regular, color #9a9cb8
  Status — Badge Active
  Deadline — "Oct 24, 2023" — Inter 14px Medium, color #9a9cb8
  Actions — edit + delete buttons, hidden until row hover

ROW 2
background rgba(26,27,38,0.20)
  ID — "SD-011" — Inter 14px Medium, color #9a9cb8
  Project — layout vertical, gap 2
    "Solaris Dashboard UI" — Inter 14px Regular, color #e2e4f0
    "High-Fidelity Prototyping" — Inter 11px Regular, color #9a9cb8
  Client — layout horizontal, align center, gap 8
    Avatar image url https://lh3.googleusercontent.com/aida-public/AB6AXuAsYojMTspVxsjx-B-am8wuxGoqMwAcbx7H7eWBnQd40VLJ-PgFa7Ceph-p9P0x_9VsDkY6M_1LgoPDREiSfL74eXQh5eBtCnfa7VmrR2pI9_3BRZUvo4byKh_c2hVgXiujPtijUkeyPIsldLRQNGDXcZqvMp_Yr-5myinUssKRIGLbTvsHBAYewibtNBDRnnwWhHzDx8tSRp8acAXGCIG_-aL4DETXDIYdfRsWx-jIWG6Pu1P7lAXChcml_6649zWZoyI-J5sD6K4
    "Marcus Chen" — Inter 14px Regular, color #9a9cb8
  Type — "Product Design" — Inter 13px Regular, color #9a9cb8
  Status — Badge Completed
  Deadline — "Oct 12, 2023" — Inter 14px Medium, color #9a9cb8
  Actions — edit + delete buttons, hidden until row hover

ROW 3
background transparent
  ID — "SD-010" — Inter 14px Medium, color #9a9cb8
  Project — layout vertical, gap 2
    "Nexus Landing Page" — Inter 14px Regular, color #e2e4f0
    "Marketing Collateral" — Inter 11px Regular, color #9a9cb8
  Client — layout horizontal, align center, gap 8
    Avatar initials "SC" background rgba(124,138,244,0.30) text-color #bcc2ff
    "Sarah Connor" — Inter 14px Regular, color #9a9cb8
  Type — "Web Dev" — Inter 13px Regular, color #9a9cb8
  Status — Badge Revision
  Deadline — "Oct 30, 2023" — Inter 14px Medium, color #9a9cb8
  Actions — edit + delete buttons, hidden until row hover

ROW 4
background rgba(26,27,38,0.20)
  ID — "SD-009" — Inter 14px Medium, color #9a9cb8
  Project — layout vertical, gap 2
    "Apex Mobile App" — Inter 14px Regular, color #e2e4f0
    "iOS & Android MVP" — Inter 11px Regular, color #9a9cb8
  Client — layout horizontal, align center, gap 8
    Avatar initials "DK" background rgba(232,124,138,0.30) text-color #e87c8a
    "David Kim" — Inter 14px Regular, color #9a9cb8
  Type — "Development" — Inter 13px Regular, color #9a9cb8
  Status — Badge Delayed
  Deadline — "In 2 Days" — Inter 14px Medium, color #e87c8a
  Actions — edit + delete buttons, hidden until row hover

ROW 5
background transparent
  ID — "SD-008" — Inter 14px Medium, color #9a9cb8
  Project — layout vertical, gap 2
    "Cloud Architecture Audit" — Inter 14px Regular, color #e2e4f0
    "Consultancy" — Inter 11px Regular, color #9a9cb8
  Client — layout horizontal, align center, gap 8
    Avatar initials "GL" background #908f9e text-color #12131d
    "Global Logistics" — Inter 14px Regular, color #9a9cb8
  Type — "Consulting" — Inter 13px Regular, color #9a9cb8
  Status — Badge Archived
  Deadline — "Sept 28, 2023" — Inter 14px Medium, color #9a9cb8
  Actions — edit + delete buttons, hidden until row hover

---

TABLE FOOTER
background rgba(26,27,38,0.30)
border-top 1px solid rgba(69,70,82,0.20)
padding 16px 24px
layout horizontal, justify space-between, align center

LEFT — BATCH ACTIONS
layout horizontal, gap 16

  Button "Batch Edit"
    layout horizontal, align center, gap 8
    icon edit, size 16, color #9a9cb8
    text "Batch Edit" — Inter 13px Regular, color #9a9cb8
    background transparent
    border 1px solid #454652
    border-radius 8
    padding 8px 16px
    hover background #1e1f2a
    press scale 0.95
    cursor pointer

  Button "Delete Selection"
    layout horizontal, align center, gap 8
    icon delete, size 16, color #9a9cb8
    text "Delete Selection" — Inter 13px Regular, color #9a9cb8
    background transparent
    border 1px solid #454652
    border-radius 8
    padding 8px 16px
    hover text-color #e87c8a
    hover border-color #e87c8a
    press scale 0.95
    cursor pointer

RIGHT — PAGINATION
layout horizontal, align center, gap 16

  Text "Page 1 of 3" — Inter 13px Regular, color #9a9cb8

  Button Group — layout horizontal, gap 4

    Prev Button
      icon chevron_left, size 24, color #9a9cb8
      width 40, height 40
      border 1px solid #454652
      border-radius 8
      background transparent
      disabled true
      opacity 0.30

    Next Button
      icon chevron_right, size 24, color #9a9cb8
      width 40, height 40
      border 1px solid #454652
      border-radius 8
      background transparent
      hover background #1e1f2a
      disabled false
      cursor pointer

---

TOAST NOTIFICATION
position fixed, bottom 32, right 32
z-index top
layout vertical, gap 12

Toast Card
  background #333440
  border 1px solid rgba(188,194,255,0.30)
  border-radius 12
  padding 12px 24px
  shadow 0 8px 32px rgba(0,0,0,0.5)
  layout horizontal, align center, gap 12

  Icon info, size 24, color #bcc2ff
  Text "Action triggered for system processing." — Inter 13px Regular, color #e2e1f1

  appear animation: opacity 0 to 1, translateY +16px to 0, duration 200ms, easing ease-out
  dismiss animation: opacity 1 to 0, translateY 0 to +16px, duration 500ms, easing ease-in
  auto-dismiss after 3000ms
  trigger on every button click anywhere in the app