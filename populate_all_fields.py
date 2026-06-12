# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
populate_all_fields.py
----------------------
Wipes and re-populates the SmartDesk database with rich, realistic seed data
covering every column in every table:
  clients, projects, invoices, payments, time_logs, tasks, contracts, ml_predictions
Run from the project root:
    python populate_all_fields.py
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta, date

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from app.data.database import Database

# ─── Helpers ──────────────────────────────────────────────────────────────────

def days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()

def days_from_now(n: int) -> str:
    return (date.today() + timedelta(days=n)).isoformat()

def dt_ago(days: int, hour: int = 9, minute: int = 0) -> str:
    return (datetime.now() - timedelta(days=days)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ).strftime("%Y-%m-%d %H:%M:%S")

def dt_offset(base_dt_str: str, hours: float) -> str:
    base = datetime.strptime(base_dt_str, "%Y-%m-%d %H:%M:%S")
    return (base + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

# ─── Database setup ───────────────────────────────────────────────────────────

db = Database()
db.initialize()

print("=" * 60)
print("  SmartDesk — Full-field seed data loader")
print("=" * 60)

# ─── WIPE existing data (preserves schema) ────────────────────────────────────

for tbl in ["ml_predictions", "contracts", "tasks", "time_logs",
            "payments", "invoices", "projects", "clients"]:
    db.execute(f"DELETE FROM {tbl}")
    # Reset auto-increment counter
    db.execute(f"DELETE FROM sqlite_sequence WHERE name='{tbl}'")

print("[OK] Cleared all tables")

# ─── 1. CLIENTS ───────────────────────────────────────────────────────────────

clients_data = [
    # (name, email, phone, address, company, notes)
    ("Arjun Sharma",    "arjun.sharma@techvista.in",    "+91-98101-23456",
     "42, Connaught Place, New Delhi - 110001",
     "TechVista Solutions Pvt. Ltd.",
     "Long-term client since 2023. Prefers WhatsApp for quick updates. Budget-conscious but pays on time."),

    ("Priya Nair",      "priya.nair@nexusdesign.io",   "+91-94470-87654",
     "201, MG Road, Kochi - 682016",
     "Nexus Design Studio",
     "Creative director. Loves bold design language. Usually needs 2 revision rounds."),

    ("Rahul Mehta",     "r.mehta@cloudbridge.co",      "+91-99300-11223",
     "Floor 5, Cyber City, Gurugram - 122002",
     "CloudBridge Technologies",
     "Startup founder. Fast-paced projects, tight deadlines. Prefers fixed-price contracts."),

    ("Sneha Iyer",      "sneha@brightbrandco.com",     "+91-80001-55667",
     "78, Brigade Road, Bengaluru - 560025",
     "BrightBrand Co.",
     "Marketing head. Always wants analytics and performance metrics in deliverables."),

    ("Vikram Patel",    "vikram.patel@infranode.net",  "+91-97272-44889",
     "Plot 12, GIDC Industrial Estate, Surat - 395010",
     "InfraNode Networks",
     "Conservative client. Very detail-oriented. Requires sign-off at every milestone."),

    ("Ananya Reddy",    "ananya.r@melodymedia.in",     "+91-88008-33211",
     "15, Film Nagar, Hyderabad - 500033",
     "Melody Media Productions",
     "Music production company. Projects often have tight turnarounds around release dates."),

    ("Karthik Suresh",  "karthik@zenithapps.co.in",   "+91-76543-21098",
     "3rd Floor, Tidel Park, Chennai - 600113",
     "Zenith App Developers",
     "Technical client — communicates in specs and wireframes. Very structured workflow."),

    ("Deepika Joshi",   "deepika@urbanroots.org",      "+91-91234-78901",
     "22, Civil Lines, Jaipur - 302006",
     "Urban Roots NGO",
     "Non-profit. Budget is limited but the mission is meaningful. Flexible on timelines."),
]

client_ids = []
for c in clients_data:
    cid = db.execute_returning_id(
        "INSERT INTO clients (name, email, phone, address, company, notes) VALUES (?, ?, ?, ?, ?, ?)", c
    )
    client_ids.append(cid)

print(f"[OK] Inserted {len(client_ids)} clients")

# ─── 2. PROJECTS ──────────────────────────────────────────────────────────────

PROJECT_TYPES = ["Design", "Development", "Video", "Writing", "Music", "General"]
PROJECT_STATUSES = ["Not Started", "In Progress", "On Hold", "Completed", "Cancelled"]

projects_data = [
    # (client_idx, name, type, description, status, deadline_offset, budget)
    (0, "TechVista Corporate Website Redesign", "Design",
     "Full redesign of TechVista's 12-page corporate website including new brand identity, responsive layouts, and CMS integration. Includes SEO audit and on-page optimization.",
     "In Progress", 45, 185000),

    (0, "Annual Report Infographic Pack", "Design",
     "Design 20 custom data-driven infographics for TechVista's 2025 annual report. Includes data visualisation, icon library, and print-ready exports.",
     "Completed", -10, 72000),

    (1, "Nexus Brand Identity System", "Design",
     "Create a comprehensive brand identity for Nexus Design Studio: logo, color palette, typography guidelines, business card, letterhead, and social media templates.",
     "Completed", -30, 95000),

    (1, "Product Packaging Design — Skincare Range", "Design",
     "Design packaging for 8 SKUs in a new skincare range. Includes dieline creation, print spec sheets, and 3D mockups for client presentations.",
     "In Progress", 20, 120000),

    (2, "CloudBridge SaaS Dashboard UI", "Development",
     "Design and front-end development of a multi-tenant analytics dashboard in React. Includes data tables, chart components, role-based views, and dark-mode support.",
     "In Progress", 60, 320000),

    (2, "Startup Landing Page + Email Funnels", "Development",
     "High-converting landing page with A/B testing hooks, integrated with Mailchimp. Includes 5-email drip campaign copy and HTML templates.",
     "Completed", -20, 58000),

    (3, "BrightBrand Social Media Campaign", "Design",
     "30-day social media content calendar: 60 posts (static + reel covers) for Instagram, LinkedIn, and Twitter. Includes branded templates in Canva and Figma.",
     "In Progress", 15, 45000),

    (3, "Q3 Performance Marketing Report", "Writing",
     "Comprehensive 40-page marketing performance analysis report covering paid ads, organic, and email channels. Includes executive summary and recommendations.",
     "Completed", -5, 38000),

    (4, "InfraNode Network Topology Documentation", "Writing",
     "Technical documentation for InfraNode's new multi-region network topology. Includes architecture diagrams, runbooks, and disaster-recovery playbooks.",
     "On Hold", 90, 110000),

    (4, "Security Audit Report", "Writing",
     "Penetration testing summary report and remediation roadmap based on third-party audit findings. Written for both technical and executive audiences.",
     "Not Started", 120, 85000),

    (5, "Melody Media — Album Promo Video", "Video",
     "3-minute promotional video for upcoming album release. Includes concept, storyboarding, B-roll direction notes, motion graphics, and colour grading.",
     "In Progress", 10, 145000),

    (5, "Podcast Intro & Outro Jingles", "Music",
     "Compose and produce 3 unique podcast jingle sets (intro 15s, outro 10s, transition 5s) with full licensing for commercial use.",
     "Completed", -15, 42000),

    (6, "Zenith Fitness App — Full UI/UX", "Design",
     "End-to-end UX research, wireframing, and high-fidelity UI design for iOS and Android fitness tracking app. Includes 48 screens, component library, and prototype.",
     "In Progress", 75, 275000),

    (6, "API Integration Guide", "Writing",
     "Developer-facing documentation for Zenith's RESTful API: endpoint reference, authentication guide, rate-limiting policies, and code samples in 3 languages.",
     "Completed", -8, 55000),

    (7, "Urban Roots — Awareness Campaign Collateral", "Design",
     "Design a complete awareness campaign kit for Urban Roots' annual fundraiser: poster, digital banner set, email header, and donation page mockup.",
     "Not Started", 50, 28000),
]

project_ids = []
for (cidx, name, ptype, desc, status, deadline_off, budget) in projects_data:
    deadline = days_from_now(deadline_off) if deadline_off > 0 else days_ago(abs(deadline_off))
    pid = db.execute_returning_id(
        """INSERT INTO projects (client_id, name, type, description, status, deadline, budget)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (client_ids[cidx], name, ptype, desc, status, deadline, budget)
    )
    project_ids.append(pid)

print(f"[OK] Inserted {len(project_ids)} projects")

# ─── 3. INVOICES ──────────────────────────────────────────────────────────────

GST = 0.18

invoices_raw = [
    # (proj_idx, inv_num, amount, date_issued_ago, due_days_from_issue, status, notes)
    (0, "INV-2026-0001", 92500,  60, 30, "Paid",    "50% advance payment — Website Redesign Phase 1"),
    (0, "INV-2026-0002", 92500,  10, 30, "Unpaid",  "50% balance payment — Website Redesign Phase 2 delivery"),
    (1, "INV-2026-0003", 72000,  45, 30, "Paid",    "Full payment — Annual Report Infographic Pack"),
    (2, "INV-2026-0004", 95000,  90, 30, "Paid",    "Full payment — Nexus Brand Identity System"),
    (3, "INV-2026-0005", 60000,  15, 30, "Unpaid",  "50% advance — Product Packaging Design"),
    (3, "INV-2026-0006", 60000,  -5, 30, "Overdue", "50% balance — Product Packaging Design (overdue)"),
    (4, "INV-2026-0007", 160000, 30, 30, "Paid",    "Milestone 1 payment — SaaS Dashboard"),
    (4, "INV-2026-0008", 160000,  5, 30, "Unpaid",  "Milestone 2 payment — SaaS Dashboard"),
    (5, "INV-2026-0009", 58000,  55, 30, "Paid",    "Full payment — Landing Page + Email Funnels"),
    (6, "INV-2026-0010", 22500,   8, 14, "Unpaid",  "50% advance — Social Media Campaign"),
    (7, "INV-2026-0011", 38000,  12, 15, "Paid",    "Full payment — Q3 Performance Report"),
    (8, "INV-2026-0012", 55000,  20, 30, "Paid",    "Advance — Network Topology Documentation"),
    (10, "INV-2026-0013", 72500,  7, 14, "Unpaid",  "50% advance — Album Promo Video"),
    (11, "INV-2026-0014", 42000,  40, 30, "Paid",   "Full payment — Podcast Jingles"),
    (12, "INV-2026-0015", 137500, 20, 30, "Paid",   "Milestone 1 — Fitness App UI/UX"),
    (12, "INV-2026-0016", 137500,  2, 30, "Unpaid", "Milestone 2 — Fitness App UI/UX"),
    (13, "INV-2026-0017", 55000,  25, 15, "Paid",   "Full payment — API Integration Guide"),
]

invoice_ids = []
for (pidx, inv_num, amount, issued_ago, due_days, status, notes) in invoices_raw:
    tax = round(amount * GST, 2)
    total = round(amount + tax, 2)
    issued = days_ago(issued_ago) if issued_ago >= 0 else days_from_now(abs(issued_ago))
    issued_dt = date.today() - timedelta(days=issued_ago)
    due = (issued_dt + timedelta(days=due_days)).isoformat()
    iid = db.execute_returning_id(
        """INSERT INTO invoices (project_id, invoice_number, amount, tax, total,
                                 date_issued, due_date, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (project_ids[pidx], inv_num, amount, tax, total, issued, due, status, notes)
    )
    invoice_ids.append((iid, status, total))

print(f"[OK] Inserted {len(invoice_ids)} invoices")

# ─── 4. PAYMENTS ──────────────────────────────────────────────────────────────

PAYMENT_MODES = ["Bank Transfer", "UPI", "Cheque", "PayPal", "Razorpay"]
UPI_IDS = ["techvista@okaxis", "priya@ybl", "rahul.m@upi", "sneha@paytm",
           "vikrampatel@hdfcbank", "melodymedia@icici", "zenith@oksbi",
           "deepikangos@upi"]

payments_inserted = 0
for (iid, status, total) in invoice_ids:
    if status == "Paid":
        mode = random.choice(PAYMENT_MODES)
        ref = f"REF{random.randint(100000, 999999)}"
        db.execute(
            """INSERT INTO payments (invoice_id, amount_paid, payment_date, payment_mode, reference)
               VALUES (?, ?, ?, ?, ?)""",
            (iid, total, days_ago(random.randint(1, 20)), mode, ref)
        )
        payments_inserted += 1
    elif status == "Unpaid":
        # Partial payment on some unpaid invoices
        if random.random() < 0.4:
            partial = round(total * 0.5, 2)
            db.execute(
                """INSERT INTO payments (invoice_id, amount_paid, payment_date, payment_mode, reference)
                   VALUES (?, ?, ?, ?, ?)""",
                (iid, partial, days_ago(random.randint(5, 25)), "UPI", f"UPI{random.randint(100000,999999)}")
            )
            payments_inserted += 1

print(f"[OK] Inserted {payments_inserted} payment records")

# ─── 5. TIME LOGS ─────────────────────────────────────────────────────────────

time_log_descriptions = {
    "Design":      ["Initial concept exploration", "Wireframe creation", "High-fidelity mockups",
                    "Client review revisions", "Asset export and handoff", "Brand guideline documentation",
                    "Prototype building", "Icon design", "Typography selection", "Color palette refinement"],
    "Development": ["Architecture planning", "Component scaffolding", "API integration",
                    "Bug fixing", "Code review", "Unit testing", "Performance optimisation",
                    "Documentation writing", "Deployment pipeline setup", "Database schema design"],
    "Video":       ["Storyboard planning", "Script review", "B-roll coordination",
                    "Motion graphics", "Colour grading", "Audio sync", "Final render and export",
                    "Client feedback round", "Subtitle creation", "Thumbnail design"],
    "Writing":     ["Research and outline", "First draft", "Revision pass",
                    "Proofreading", "Formatting and layout", "Client feedback integration",
                    "SEO keyword integration", "Final QA check", "PDF export", "Submission"],
    "Music":       ["Reference listening", "Composition", "Arrangement",
                    "Recording", "Mixing", "Mastering", "Client review", "Stems export",
                    "Licensing documentation", "Delivery packaging"],
    "General":     ["Client call", "Project planning", "Requirement gathering",
                    "Progress update", "Documentation", "Research", "Internal review"],
}

tl_inserted = 0
for idx, (proj_row) in enumerate(projects_data):
    cidx, name, ptype, desc, status, deadline_off, budget = proj_row
    pid = project_ids[idx]
    descs = time_log_descriptions.get(ptype, time_log_descriptions["General"])

    # Number of time logs based on project status
    if status == "Completed":
        num_logs = random.randint(8, 14)
        max_ago = 90
    elif status == "In Progress":
        num_logs = random.randint(5, 10)
        max_ago = 45
    elif status == "On Hold":
        num_logs = random.randint(3, 6)
        max_ago = 60
    else:
        num_logs = random.randint(0, 2)
        max_ago = 10

    for _ in range(num_logs):
        start_ago = random.randint(1, max_ago)
        start_hour = random.randint(9, 17)
        duration = round(random.uniform(1.0, 7.5), 2)
        start = dt_ago(start_ago, start_hour, random.randint(0, 45))
        end   = dt_offset(start, duration)
        db.execute(
            """INSERT INTO time_logs (project_id, start_time, end_time, duration_hours, description)
               VALUES (?, ?, ?, ?, ?)""",
            (pid, start, end, duration, random.choice(descs))
        )
        tl_inserted += 1

print(f"[OK] Inserted {tl_inserted} time log entries")

# ─── 6. TASKS ─────────────────────────────────────────────────────────────────

tasks_by_type = {
    "Design": [
        ("Discovery call & brief sign-off", True),
        ("Competitor analysis", True),
        ("Mood board creation", True),
        ("Initial concepts (3 directions)", True),
        ("Client feedback round 1", False),
        ("Revised concepts", False),
        ("Final design files", False),
        ("Asset handoff package", False),
    ],
    "Development": [
        ("Requirement specification document", True),
        ("Tech stack finalisation", True),
        ("Repo & CI/CD setup", True),
        ("Core feature development", False),
        ("Integration testing", False),
        ("UAT with client", False),
        ("Bug fixes post-UAT", False),
        ("Production deployment", False),
        ("Post-launch monitoring", False),
    ],
    "Video": [
        ("Creative brief approval", True),
        ("Storyboard draft", True),
        ("Script finalisation", False),
        ("Shoot coordination", False),
        ("Rough cut review", False),
        ("Motion graphics integration", False),
        ("Colour & audio grade", False),
        ("Final export delivery", False),
    ],
    "Writing": [
        ("Research & source gathering", True),
        ("Outline approval", True),
        ("First draft submission", False),
        ("Client feedback integration", False),
        ("Second draft", False),
        ("Proofreading & QA", False),
        ("Final delivery", False),
    ],
    "Music": [
        ("Reference track analysis", True),
        ("Composition demo", True),
        ("Full arrangement", False),
        ("Recording session", False),
        ("Mix review", False),
        ("Master delivery", False),
        ("Licensing agreement signed", False),
    ],
    "General": [
        ("Initial scoping", True),
        ("Proposal sent", True),
        ("Contract signed", True),
        ("Kick-off meeting", False),
        ("Milestone 1 delivery", False),
        ("Final delivery", False),
    ],
}

tasks_inserted = 0
for idx, (proj_row) in enumerate(projects_data):
    cidx, name, ptype, desc, status, deadline_off, budget = proj_row
    pid = project_ids[idx]
    task_list = tasks_by_type.get(ptype, tasks_by_type["General"])

    # For completed projects, mark all tasks done
    for i, (title, default_done) in enumerate(task_list):
        if status == "Completed":
            is_done = 1
        elif status == "In Progress":
            # First half done, rest pending
            is_done = 1 if i < len(task_list) // 2 else 0
        elif status in ("Not Started", "Cancelled"):
            is_done = 0
        else:
            is_done = 1 if default_done else 0

        due = days_from_now(random.randint(5, 60)) if is_done == 0 else days_ago(random.randint(5, 30))
        db.execute(
            """INSERT INTO tasks (project_id, title, due_date, is_completed)
               VALUES (?, ?, ?, ?)""",
            (pid, title, due, is_done)
        )
        tasks_inserted += 1

print(f"[OK] Inserted {tasks_inserted} tasks")

# ─── 7. CONTRACTS ─────────────────────────────────────────────────────────────

CONTRACT_TEMPLATES = {
    "Design": """FREELANCE DESIGN SERVICES AGREEMENT

This Agreement is entered into between the freelancer ("Designer") and the Client for the provision of graphic/UI/UX design services as described in the attached Project Brief.

SCOPE OF WORK
The Designer agrees to deliver design assets as mutually agreed in writing prior to project commencement. Deliverables include high-fidelity mockups, source files (Figma/Adobe XD), and exported assets in agreed formats.

PAYMENT TERMS
The Client shall pay 50% of the total project fee as an advance before work commences. The remaining 50% is due upon delivery of final assets. Invoices are payable within 30 days of issuance.

REVISIONS
This agreement includes {revisions} rounds of revisions. Additional revision rounds will be billed at ₹{hourly_rate}/hour.

INTELLECTUAL PROPERTY
Upon receipt of full payment, all intellectual property rights in the deliverables shall transfer to the Client. Source files remain the property of the Designer until full payment is received.

TIMELINE
The project shall be completed within {timeline_days} calendar days from the date of advance payment receipt, subject to timely client feedback.

CONFIDENTIALITY
Both parties agree to keep all project-related information confidential during and after the project engagement.

GOVERNING LAW
This Agreement shall be governed by the laws of India.""",

    "Development": """FREELANCE SOFTWARE DEVELOPMENT AGREEMENT

PARTIES
This Agreement is between the freelance developer ("Developer") and the Client for the development of software as described herein.

SCOPE
Developer will design, develop, and deliver software features as outlined in the project specification document. Changes to scope must be agreed in writing and may affect timeline and cost.

PAYMENT
Total project fee is payable in milestones as agreed. Each milestone invoice is due within 15 days of approval. Late payments attract a 2% monthly interest charge.

HOURLY RATE
Out-of-scope work is billed at ₹{hourly_rate}/hour, invoiced bi-weekly.

REVISIONS
{revisions} revision cycles are included per milestone. Additional cycles billed at hourly rate.

TIMELINE
Estimated completion: {timeline_days} working days. Delays caused by client review periods do not count toward the timeline.

WARRANTY
Developer provides a 30-day bug-fix warranty post-delivery for defects attributable to the original code.

OWNERSHIP
All code becomes the exclusive property of the Client upon full payment.

GOVERNING LAW
Indian IT Act 2000 and associated regulations apply.""",

    "Video": """VIDEO PRODUCTION SERVICES AGREEMENT

This Video Production Agreement outlines the terms between the video producer ("Producer") and the Client.

DELIVERABLES
Producer shall deliver: storyboard, rough cut, final cut, and all agreed formats (MP4 4K, social media crops). Raw footage remains the property of the Producer unless separately licensed.

TIMELINE
Production will be completed within {timeline_days} days of project commencement, contingent on client approval at each stage.

REVISIONS
Client is entitled to {revisions} revision round(s) on the final cut. Music and voice-over changes after approval constitute additional work.

PAYMENT
50% advance upon agreement signing. Balance due within 14 days of final delivery. Failure to pay releases the Producer from all licensing obligations.

HOURLY RATE
Additional editing or reshoots: ₹{hourly_rate}/hour.

MUSIC LICENSING
Any licensed music used is subject to separate licensing terms. Client is responsible for publishing rights for third-party content.

GOVERNING LAW
This agreement is governed by the laws of India.""",

    "Writing": """FREELANCE WRITING & CONTENT SERVICES AGREEMENT

SCOPE
The Writer agrees to produce the content described in the project brief, including all drafts and final delivery in agreed formats.

ORIGINAL WORK
All content produced is original. The Writer guarantees work is free from plagiarism and will pass standard AI-detection thresholds if specified.

REVISIONS
Includes {revisions} revision round(s). Additional revisions charged at ₹{hourly_rate}/hour.

TIMELINE
First draft delivered within {timeline_days} days of project start. Subsequent revisions within 48 hours of feedback receipt.

PAYMENT
Full payment due within 15 days of final delivery. Projects over ₹50,000 require a 40% advance.

RIGHTS
Upon full payment, Client receives exclusive rights to published content. Writer retains the right to display the work in their portfolio unless otherwise agreed.

CONFIDENTIALITY
Both parties agree to maintain confidentiality of all proprietary information shared during the engagement.""",

    "Music": """MUSIC COMPOSITION & PRODUCTION AGREEMENT

SCOPE
Composer agrees to create original compositions as described in the creative brief, including all stems and mastered audio files.

TIMELINE
Compositions delivered within {timeline_days} days of brief approval. Each revision cycle adds up to 5 business days.

REVISIONS
{revisions} revision round(s) included. Further revisions at ₹{hourly_rate}/hour.

LICENSING
Client receives a perpetual, royalty-free license for the compositions in the agreed-upon contexts (podcast, commercial, film, etc.). Sync licensing for broadcast requires a separate agreement.

PAYMENT
50% on contract signing. 50% on final delivery. Work does not begin until advance is received.

OWNERSHIP
Composer retains master recording rights. Client owns the license for use as described above.""",

    "General": """FREELANCE SERVICES AGREEMENT

This Agreement governs the provision of services by the Freelancer to the Client.

SERVICES
As described in the attached project scope document.

PAYMENT
Fee payable as per the milestone schedule. Hourly work billed at ₹{hourly_rate}/hour. Invoices due within 30 days.

REVISIONS
{revisions} revision round(s) included in the quoted price.

TIMELINE
Estimated project duration: {timeline_days} calendar days.

TERMINATION
Either party may terminate this agreement with 14 days written notice. Work completed to that date is billable.

GOVERNING LAW
This Agreement shall be governed by the laws of India.""",
}

RISK_PROFILES = [
    # (risk_score, risk_level, findings_list)
    (12, "Low",    ["Standard payment terms", "Clear scope definition", "Reasonable revision limit", "IP transfer clause present"]),
    (28, "Medium", ["Vague deliverable definition", "Extended payment terms (60 days)", "Unlimited revisions clause", "No kill fee clause"]),
    (45, "High",   ["No advance payment clause", "Client retains copyright during project", "Force majeure clause missing", "Dispute resolution undefined", "Non-compete clause too broad"]),
    (18, "Low",    ["Clear milestone payments", "Defined revision rounds", "Confidentiality clause included", "Termination terms fair"]),
    (35, "Medium", ["Currency risk not addressed", "Late payment interest absent", "Scope creep risk", "Delivery format ambiguous"]),
]

contracts_inserted = 0
for idx, (proj_row) in enumerate(projects_data):
    cidx, name, ptype, desc, status, deadline_off, budget = proj_row
    pid = project_ids[idx]

    # Only add contracts for non-trivial projects
    if status in ("Not Started",) and random.random() < 0.5:
        continue

    template_key = ptype if ptype in CONTRACT_TEMPLATES else "General"
    hourly = random.choice([600, 700, 800, 900, 1000, 1200])
    revisions = random.randint(2, 4)
    timeline = random.randint(14, 90)

    contract_text = CONTRACT_TEMPLATES[template_key].format(
        hourly_rate=hourly,
        revisions=revisions,
        timeline_days=timeline,
    )

    profile = random.choice(RISK_PROFILES)
    findings_json = json.dumps(profile[2])

    db.execute(
        """INSERT INTO contracts (project_id, contract_text, hourly_rate, revision_rounds,
                                  timeline_days, risk_score, risk_level, findings)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (pid, contract_text, hourly, revisions, timeline, profile[0], profile[1], findings_json)
    )
    contracts_inserted += 1

print(f"[OK] Inserted {contracts_inserted} contracts")

# ─── 8. ML PREDICTIONS ────────────────────────────────────────────────────────

prediction_types = ["budget_overrun", "deadline_risk", "client_churn", "invoice_delay"]

ml_inserted = 0
for idx, pid in enumerate(project_ids):
    ptype_pred = random.choice(prediction_types)
    input_data = json.dumps({
        "project_id": pid,
        "budget": projects_data[idx][6],
        "status": projects_data[idx][4],
        "days_remaining": abs(projects_data[idx][5]),
    })
    result = json.dumps({
        "risk": random.choice(["Low", "Medium", "High"]),
        "recommendation": random.choice([
            "Schedule a progress check-in",
            "Request scope clarification from client",
            "Send payment reminder",
            "Update project timeline",
            "No action required",
        ])
    })
    confidence = round(random.uniform(0.62, 0.97), 4)
    db.execute(
        """INSERT INTO ml_predictions (project_id, prediction_type, input_data, result, confidence, model_version)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (pid, ptype_pred, input_data, result, confidence, "1.0.0")
    )
    ml_inserted += 1

print(f"[OK] Inserted {ml_inserted} ML prediction records")

# ─── Summary ──────────────────────────────────────────────────────────────────

print()
print("-" * 60)
print("  Database population complete!")
print("-" * 60)

rows = {
    "clients":        db.execute("SELECT COUNT(*) as n FROM clients")[0]["n"],
    "projects":       db.execute("SELECT COUNT(*) as n FROM projects")[0]["n"],
    "invoices":       db.execute("SELECT COUNT(*) as n FROM invoices")[0]["n"],
    "payments":       db.execute("SELECT COUNT(*) as n FROM payments")[0]["n"],
    "time_logs":      db.execute("SELECT COUNT(*) as n FROM time_logs")[0]["n"],
    "tasks":          db.execute("SELECT COUNT(*) as n FROM tasks")[0]["n"],
    "contracts":      db.execute("SELECT COUNT(*) as n FROM contracts")[0]["n"],
    "ml_predictions": db.execute("SELECT COUNT(*) as n FROM ml_predictions")[0]["n"],
}
for tbl, cnt in rows.items():
    print(f"  {tbl:<20} {cnt:>4} rows")

# Financial summary
paid   = db.execute("SELECT COALESCE(SUM(total),0) as t FROM invoices WHERE status='Paid'")[0]["t"]
unpaid = db.execute("SELECT COALESCE(SUM(total),0) as t FROM invoices WHERE status='Unpaid'")[0]["t"]
over   = db.execute("SELECT COALESCE(SUM(total),0) as t FROM invoices WHERE status='Overdue'")[0]["t"]
print()
print(f"  Revenue (Paid)     ₹{paid:>12,.0f}")
print(f"  Pending (Unpaid)   ₹{unpaid:>12,.0f}")
print(f"  Overdue            ₹{over:>12,.0f}")
print("-" * 60)
print("  Launch SmartDesk to see the populated data!")
print("-" * 60)
