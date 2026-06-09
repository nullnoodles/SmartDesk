"""Add some unpaid invoices for better dashboard data."""
from app.data.database import Database
from datetime import datetime, timedelta

db = Database()
db.initialize()

# Add a few unpaid invoices
unpaid_invoices = [
    ("INV-2026-9001", 25000, 4500, 29500, "2026-05-15", "2026-06-14", "Unpaid"),
    ("INV-2026-9002", 40000, 7200, 47200, "2026-05-20", "2026-06-19", "Unpaid"),
    ("INV-2026-9003", 15000, 2700, 17700, "2026-04-10", "2026-05-10", "Overdue"),
]

# Get a project ID to associate with
projects = db.execute("SELECT id FROM projects LIMIT 1")
project_id = projects[0]["id"] if projects else 1

for inv_number, amount, tax, total, date_issued, due_date, status in unpaid_invoices:
    db.execute("""
        INSERT INTO invoices (project_id, invoice_number, amount, tax, total, date_issued, due_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, inv_number, amount, tax, total, date_issued, due_date, status, f"Sample {status.lower()} invoice"))

print("Added sample unpaid/overdue invoices!")

# Check results
unpaid_total = db.execute("SELECT SUM(amount) as total FROM invoices WHERE status='Unpaid'")[0]["total"]
print(f"Total unpaid invoices: ₹{unpaid_total:,.0f}")