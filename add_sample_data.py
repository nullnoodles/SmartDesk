"""Add sample invoice and time log data for dashboard testing."""
from app.data.database import Database
from datetime import datetime, timedelta
import random

db = Database()
db.initialize()

print("Adding sample data for dashboard testing...")

# Get existing projects
projects = db.execute("SELECT id, name, budget FROM projects LIMIT 10")

if not projects:
    print("No projects found - please add some projects first!")
    exit()

print(f"Found {len(projects)} projects to work with")

# Add sample invoices
invoice_data = []
for i, project in enumerate(projects[:6]):  # Use first 6 projects
    # Create 1-2 invoices per project
    for inv_num in range(1, random.randint(2, 3)):
        invoice_number = f"INV-2026-{str(i*10 + inv_num).zfill(4)}"
        amount = project["budget"] * 0.5 if project["budget"] else random.randint(15000, 50000)
        tax = amount * 0.18  # 18% GST
        total = amount + tax
        
        # Random date in last 3 months
        date_issued = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Random status - 70% Paid, 20% Unpaid, 10% Overdue
        rand = random.random()
        if rand < 0.7:
            status = "Paid"
        elif rand < 0.9:
            status = "Unpaid" 
        else:
            status = "Overdue"
            
        invoice_data.append((
            project["id"], invoice_number, amount, tax, total,
            date_issued, due_date, status, f"Invoice for {project['name']}"
        ))

print(f"Adding {len(invoice_data)} sample invoices...")
for inv in invoice_data:
    db.execute("""
        INSERT INTO invoices (project_id, invoice_number, amount, tax, total, date_issued, due_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, inv)

# Add sample time logs
time_log_data = []
for project in projects[:8]:  # Use first 8 projects
    # Add 3-8 time logs per project
    for day_offset in range(random.randint(3, 8)):
        start_time = (datetime.now() - timedelta(days=day_offset, hours=random.randint(9, 16)))
        duration = random.uniform(1.5, 8.5)  # 1.5 to 8.5 hours
        end_time = start_time + timedelta(hours=duration)
        
        descriptions = [
            "Design work", "Client meeting", "Development", "Bug fixes", 
            "Research", "Code review", "Testing", "Documentation"
        ]
        
        time_log_data.append((
            project["id"],
            start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time.strftime('%Y-%m-%d %H:%M:%S'),
            duration,
            random.choice(descriptions)
        ))

print(f"Adding {len(time_log_data)} sample time logs...")
for log in time_log_data:
    db.execute("""
        INSERT INTO time_logs (project_id, start_time, end_time, duration_hours, description)
        VALUES (?, ?, ?, ?, ?)
    """, log)

print("Sample data added successfully!")

# Verify the data was added
invoices_count = db.execute("SELECT COUNT(*) as count FROM invoices")[0]["count"]
time_logs_count = db.execute("SELECT COUNT(*) as count FROM time_logs")[0]["count"]

print(f"Total invoices in database: {invoices_count}")
print(f"Total time logs in database: {time_logs_count}")

# Show some sample data
print("\nSample invoice data:")
sample_invoices = db.execute("SELECT invoice_number, amount, status FROM invoices LIMIT 5")
for inv in sample_invoices:
    print(f"  {inv['invoice_number']}: ₹{inv['amount']:,.0f} ({inv['status']})")

print("\nSample time log data:")
sample_logs = db.execute("SELECT duration_hours, description FROM time_logs LIMIT 5") 
for log in sample_logs:
    print(f"  {log['duration_hours']:.1f}h - {log['description']}")

print("\nNow run the app to see the dashboard with data!")