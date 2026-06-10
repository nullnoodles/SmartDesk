SIDEBAR:
- Logo: icon-box 32x32 bg #bcc2ff radius 8, text "SmartDesk" 24px Bold #bcc2ff
- Subtitle: "Creative Workspace" 11px Bold #9a9cb8
- Nav items: h48 px24, icon 24px, text 14px Regular
  default: bg transparent, color #9a9cb8
  hover: bg #1a1b26, color #bcc2ff
  active: bg rgba(188,194,255,0.10), color #bcc2ff, border-left 4px solid #bcc2ff
- Nav order: Dashboard, Clients, Projects(active), Invoices, Time Log, Contracts, AI Analytics, Settings

TOPBAR:
- Search: w480 h44 bg #1a1b26 border #454652 radius 12, focus border #bcc2ff
- Right: notifications icon, help icon (both 40x40 radius 8 hover bg #1e1f2a), divider, user name+role text, avatar 40x40

PRIMARY BUTTON:
bg #7c8af4, radius 8, px24 h40, icon+text color #061987, hover brightness 1.10, press scale 0.98

STAT CARDS:
bg #1a1b26, border rgba(69,70,82,0.30), radius 12, padding 24
Row1: icon-box 40x40 radius 8 + trend text
Label: 11px Bold uppercase #9a9cb8
Value: 24px Bold #e2e4f0
hover: bg #282935

STATUS BADGES (radius 9999, px12 py4, 12px Bold):
Active:    bg rgba(125,211,227,0.20) border rgba(69,159,173,0.30)  color #7dd3e3
Completed: bg rgba(130,216,172,0.20) border rgba(0,106,71,0.30)    color #82d8ac
Revision:  bg rgba(240,200,120,0.10) border rgba(240,200,120,0.30) color #f0c878
Delayed:   bg rgba(232,124,138,0.20) border rgba(232,124,138,0.30) color #e87c8a
Archived:  bg rgba(69,70,82,0.40)   border rgba(69,70,82,0.60)    color #c6c5d5

TABLE:
bg #1a1b26, radius 12, border rgba(69,70,82,0.30)
Header: 11px Bold #e2e4f0 uppercase, bg rgba(26,27,38,0.50), padding 16px 24px
Rows: h52 px24, divider rgba(69,70,82,0.20), even rows bg rgba(26,27,38,0.20)
hover: bg #1a1b26
Columns: ID 90, PROJECT 240, CLIENT 160, TYPE 120, STATUS 120, DEADLINE 130, ACTIONS 100
Actions: hidden by default, show on row hover, edit icon #9a9cb8→#bcc2ff, delete icon #9a9cb8→#e87c8a

AVATARS: 24x24 circle, initials 10px Regular centered

TOAST:
fixed bottom-right, bg #333440, border rgba(188,194,255,0.30), radius 12, px24 py12
animate in: opacity+translateY 200ms ease-out, auto-dismiss 3000ms

SCROLLBAR: width 6, track #12131a, thumb #2d2e42, hover #454652, radius 10