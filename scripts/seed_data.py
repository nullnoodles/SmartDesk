"""Seed the SmartDesk database with realistic sample data for demo/testing.

Usage:
    python scripts/seed_data.py

This populates the database with:
- 8 clients
- 12 projects (various statuses)
- 15 invoices (mix of paid, unpaid, overdue)
- Payments for paid invoices
- 40+ time log entries
- A few tasks per project
"""
from __future__ import annotations

import sys
import random
from pathlib import Path
from datetime import date, datetime, timedelta

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import DB_PATH, GST_RATE
from app.data.database import Database

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

CLIENTS = [
    ("Priya Sharma", "priya@designstudio.in", "9876543210", "Mumbai, Maharashtra", "Priya Design Studio", "Regular client, prefers minimal design"),
    ("Rahul Verma", "rahul@techventures.com", "9812345678", "Bangalore, Karnataka", "TechVentures Pvt Ltd", "Startup founder, fast turnaround needed"),
    ("Ananya Iyer", "ananya@contentfirst.in", "9845671234", "Chennai, Tamil Nadu", "ContentFirst Media", "Content agency, bulk projects"),
    ("Vikram Singh", "vikram@buildright.co", "9901234567", "Delhi, NCR", "BuildRight Construction", "Needs branding and marketing materials"),
    ("Meera Patel", "meera@greenleaf.org", "9867890123", "Ahmedabad, Gujarat", "GreenLeaf Foundation", "Non-profit, budget-conscious"),
    ("Arjun Nair", "arjun@soundwave.in", "9834567890", "Kochi, Kerala", "SoundWave Productions", "Music and audio projects"),
    ("Kavitha Reddy", "kavitha@fashionhub.com", "9878901234", "Hyderabad, Telangana", "FashionHub", "E-commerce fashion brand"),
    ("Sanjay Gupta", "sanjay@edulearn.in", "9856789012", "Pune, Maharashtra", "EduLearn Academy", "Online education platform"),
]

PROJECT_TYPES = ["Design", "Video", "Writing", "Music", "Development"]

PROJECTS = [
    # (client_idx, name, type, description, status, deadline_offset_days, budget)
    (0, "Brand Identity Redesign", "Design", "Complete brand overhaul including logo, colors, typography", "Completed", -30, 45000),
    (0, "Social Media Kit", "Design", "Instagram and LinkedIn post templates", "In Progress", 15, 12000),
    (1, "MVP Landing Page", "Development", "Single-page React landing for product launch", "Completed", -45, 35000),
    (1, "Explainer Video", "Video", "2-minute animated product explainer", "In Progress", 20, 28000),
    (2, "Blog Content Series", "Writing", "12 SEO-optimized blog posts for tech niche", "In Progress", 30, 18000),
    (2, "Newsletter Redesign", "Design", "Email newsletter template design", "Completed", -60, 8000),
    (3, "Corporate Brochure", "Design", "16-page company profile brochure", "Not Started", 45, 22000),
    (4, "Annual Report Design", "Design", "40-page annual report with infographics", "In Progress", 25, 32000),
    (5, "Podcast Intro Music", "Music", "30-second custom intro jingle", "Completed", -20, 15000),
    (5, "Album Cover Art", "Design", "Cover artwork for indie album release", "Completed", -10, 10000),
    (6, "Product Photography Edit", "Design", "Retouching 50 product photos for catalog", "In Progress", 10, 20000),
    (7, "Course Promo Video", "Video", "3-minute promotional video for new course", "Not Started", 60, 40000),
]

TASK_TITLES = [
    "Initial concept sketches", "Client feedback round 1", "Revisions",
    "Final delivery", "Source file handover", "Invoice and close",
    "Research and planning", "First draft", "Review meeting",
    "Color correction", "Export final assets", "Upload to platform",
]

TIME_DESCRIPTIONS = [
    "Concept exploration and moodboard",
    "Wireframing and layout",
    "Design iteration",
    "Client call and feedback",
    "Revisions based on feedback",
    "Final polish and export",
    "Research and reference gathering",
    "Drafting content",
    "Editing and proofreading",
    "Animation keyframes",
    "Sound mixing",
    "Color grading",
]

PAYMENT_MODES = ["UPI", "Bank Transfer", "Cash", "Cheque"]


def seed():
    """Insert sample data into the database."""
    db = Database(DB_PATH)
    db.initialize()

    # Check if data already exists
    existing = db.execute("SELECT COUNT(*) as cnt FROM clients")
    if existing and existing[0]["cnt"] > 0:
        print("Database already has data. To re-seed, delete data/smartdesk.db first.")
        print(f"  DB path: {DB_PATH}")
        return

    print("Seeding SmartDesk database with sample data...\n")

    # --- Clients ---
    print(f"  Adding {len(CLIENTS)} clients...")
    client_ids = []
    for name, email, phone, address, company, notes in CLIENTS:
        cid = db.execute_returning_id(
            "INSERT INTO clients (name, email, phone, address, company, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, address, company, notes),
        )
        client_ids.append(cid)

    # --- Projects ---
    print(f"  Adding {len(PROJECTS)} projects...")
    project_ids = []
    today = date.today()
    for client_idx, name, ptype, desc, status, deadline_offset, budget in PROJECTS:
        deadline = (today + timedelta(days=deadline_offset)).isoformat()
        pid = db.execute_returning_id(
            "INSERT INTO projects (client_id, name, type, description, status, deadline, budget) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (client_ids[client_idx], name, ptype, desc, status, deadline, budget),
        )
        project_ids.append(pid)

    # --- Invoices ---
    print("  Adding invoices...")
    invoice_ids = []
    invoice_data = []

    # Create invoices for completed and in-progress projects
    inv_num = 1
    for i, (client_idx, name, ptype, desc, status, deadline_offset, budget) in enumerate(PROJECTS):
        if status in ("Completed", "In Progress"):
            amount = budget * random.uniform(0.8, 1.0)
            amount = round(amount, 2)
            tax = round(amount * GST_RATE, 2)
            total = round(amount + tax, 2)
            inv_number = f"INV-2026-{inv_num:04d}"
            days_ago = random.randint(5, 90)
            date_issued = (today - timedelta(days=days_ago)).isoformat()
            due_date = (today - timedelta(days=days_ago - 14)).isoformat()

            if status == "Completed":
                inv_status = "Paid"
            elif deadline_offset < 0:
                inv_status = random.choice(["Paid", "Unpaid"])
            else:
                inv_status = "Unpaid"

            iid = db.execute_returning_id(
                """INSERT INTO invoices (project_id, invoice_number, amount, tax, total, date_issued, due_date, status, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (project_ids[i], inv_number, amount, tax, total, date_issued, due_date, inv_status, ""),
            )
            invoice_ids.append(iid)
            invoice_data.append((iid, total, inv_status))
            inv_num += 1

    print(f"    Created {len(invoice_ids)} invoices")

    # --- Payments for paid invoices ---
    print("  Adding payments...")
    payment_count = 0
    for iid, total, status in invoice_data:
        if status == "Paid":
            mode = random.choice(PAYMENT_MODES)
            ref = f"TXN{random.randint(100000, 999999)}"
            days_ago = random.randint(1, 30)
            pay_date = (today - timedelta(days=days_ago)).isoformat()
            db.execute_returning_id(
                "INSERT INTO payments (invoice_id, amount_paid, payment_date, payment_mode, reference) VALUES (?, ?, ?, ?, ?)",
                (iid, total, pay_date, mode, ref),
            )
            payment_count += 1
    print(f"    Created {payment_count} payments")

    # --- Time Logs ---
    print("  Adding time logs...")
    time_count = 0
    for i, pid in enumerate(project_ids):
        status = PROJECTS[i][4]
        if status == "Not Started":
            continue
        # 3-6 time entries per active project
        num_entries = random.randint(3, 6)
        for j in range(num_entries):
            days_ago = random.randint(1, 60)
            hour_start = random.randint(9, 17)
            duration = round(random.uniform(0.5, 4.0), 2)
            start_dt = datetime(today.year, today.month, today.day, hour_start, 0) - timedelta(days=days_ago)
            end_dt = start_dt + timedelta(hours=duration)
            desc = random.choice(TIME_DESCRIPTIONS)

            db.execute_returning_id(
                "INSERT INTO time_logs (project_id, start_time, end_time, duration_hours, description) VALUES (?, ?, ?, ?, ?)",
                (pid, start_dt.isoformat(), end_dt.isoformat(), duration, desc),
            )
            time_count += 1
    print(f"    Created {time_count} time log entries")

    # --- Tasks ---
    print("  Adding tasks...")
    task_count = 0
    for i, pid in enumerate(project_ids):
        status = PROJECTS[i][4]
        num_tasks = random.randint(3, 5)
        tasks = random.sample(TASK_TITLES, num_tasks)
        for t_idx, title in enumerate(tasks):
            is_completed = 1 if (status == "Completed") or (t_idx < num_tasks // 2 and status == "In Progress") else 0
            due = (today + timedelta(days=random.randint(-10, 30))).isoformat()
            db.execute_returning_id(
                "INSERT INTO tasks (project_id, title, due_date, is_completed) VALUES (?, ?, ?, ?)",
                (pid, title, due, is_completed),
            )
            task_count += 1
    print(f"    Created {task_count} tasks")

    print("\n✓ Database seeded successfully!")
    print(f"  DB path: {DB_PATH}")
    print("\n  Run 'python main.py' to see the app with data.")


if __name__ == "__main__":
    seed()
