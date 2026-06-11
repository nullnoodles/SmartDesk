Redesign the SmartDesk Invoices page to match the Stitch design. Read invoices_page.py and style.qss first. Apply Studio Graphite design system (#12131d bg, #1a1b26 cards, #7c8af4 accent).
1. PAGE HEADER — remove:

'0 total' badge
'Track payments...' subtitle

2. STAT CARDS — replace 3 with 4 using existing StatCard widget:

TOTAL EARNED — SUM(amount) WHERE status='Paid', subtitle: ▲/→/▼ vs last month
PENDING — SUM(amount) WHERE status='Unpaid', subtitle: X awaiting payment (grey) or none (green)
OVERDUE — SUM(amount) WHERE due_date < today AND status='Unpaid', subtitle: X overdue (red) or all caught up (green)
TOTAL INVOICES — COUNT(*), subtitle: X this month

3. BELOW STAT CARDS — add full width Monthly Revenue bar chart:

Bar chart using matplotlib, showing paid invoice totals per month for last 6 months
X axis: month names, Y axis: ₹ amounts in short format
Bar color: #7c8af4, bg #1a1b26, card radius 12px
Title "Monthly Revenue" top left

4. SEARCH + FILTER ROW:

Search bar left — filters table by invoice no, client, project
Filter tabs: All, Paid, Unpaid, Overdue, Cancelled — same style as Projects page
+ Create Invoice button right — same style as + New Project

5. TABLE columns: #, INVOICE NO., CLIENT, PROJECT, TOTAL (right aligned), DUE DATE, STATUS (pill badge), ACTIONS:

Same table style as Projects and Clients pages
Status badges: Paid=#7dd3a8, Unpaid=#f0c878, Overdue=#e87c8a, Cancelled=#9a9cb8
DUE DATE red if overdue and status != Paid
ACTIONS: edit pencil + delete trash, same style as other pages
Empty state: 'No invoices yet — click Create Invoice to add one'

6. REMOVE bottom action bar (Export PDF, Email Invoice, Send Reminders, Mark Paid) — move these into the edit dialog instead
7. CREATE/EDIT INVOICE DIALOG fields:

Invoice No (auto-generated e.g. INV-001)
Client (dropdown from clients table)
Project (dropdown filtered by selected client)
Amount
Due Date (date picker)
Status (dropdown: Unpaid, Paid, Overdue, Cancelled)
Notes (optional textarea)
Same dialog style as Add Client dialog

8. All data dynamic from database, refresh on data_changed signal
9. Desktop only, QScrollArea, no pagination
10. Run app, verify no errors, commit 'rebuild: Invoices page with Stitch design'"
This chat has 89 of 100 images (including PDF pages). Consider starting a new chat.