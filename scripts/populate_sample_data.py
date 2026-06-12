"""Populate SmartDesk with realistic sample data for testing and demonstration."""
from __future__ import annotations

import sys
import random
import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.payment_repo import PaymentRepository
from app.data.repositories.time_log_repo import TimeLogRepository
from app.data.repositories.task_repo import TaskRepository
from app.data.repositories.contract_repo import ContractRepository

# Sample data pools
FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Arjun", "Kavya",
    "Rohan", "Ishita", "Karan", "Meera", "Siddharth", "Nisha", "Aditya",
    "Pooja", "Rahul", "Divya", "Varun", "Riya", "Nikhil", "Shreya"
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Reddy", "Iyer", "Nair",
    "Malhotra", "Chopra", "Mehta", "Verma", "Shah", "Desai", "Rao",
    "Joshi", "Kapoor", "Agarwal", "Bansal", "Mishra"
]

COMPANIES = [
    "TechStart Solutions", "Digital Horizon", "Creative Minds Studio", "Innovate Labs",
    "BlueOcean Ventures", "Pixel Perfect Design", "CloudNine Technologies", "NextGen Systems",
    "Quantum Innovations", "BrightPath Consulting", "Spectrum Digital", "Velocity Studios",
    "Fusion Enterprises", "EcoTech Solutions", "Urban Designs Co", "Zenith Creatives",
    "Pinnacle Software", "Cascade Media", "Horizon Web Services", "Stellar Apps",
    "Phoenix Digital", "Momentum Marketing", "Apex Development", "Nova Creatives"
]

PROJECT_TYPES = [
    "Website Development", "Mobile App", "Logo Design", "Brand Identity",
    "Video Editing", "Content Writing", "UI/UX Design", "Digital Marketing",
    "E-commerce Store", "Custom Software", "Social Media Campaign", "SEO Optimization"
]

PROJECT_NAMES = [
    "Corporate Website Redesign", "Mobile App Development", "Brand Identity Package",
    "E-commerce Platform", "Marketing Campaign Q4", "Product Launch Video",
    "Annual Report Design", "Social Media Strategy", "Custom CRM System",
    "Restaurant Booking App", "Portfolio Website", "Event Management System",
    "Inventory Management", "Customer Dashboard", "Email Marketing Campaign",
    "Promotional Video Series", "Content Calendar Creation", "SEO Audit & Optimization",
    "Company Presentation Deck", "Trade Show Booth Design", "Product Photography",
    "Explainer Video Animation", "Website Maintenance", "Mobile App UI Redesign"
]

TASK_TITLES = [
    "Initial client meeting", "Research & discovery", "Wireframe creation",
    "Design mockups", "Client review", "Development setup", "Frontend implementation",
    "Backend integration", "Testing phase", "Bug fixes", "Final review",
    "Deployment", "Documentation", "Training session", "Feedback incorporation"
]

CONTRACT_TYPES = ["Fixed Price", "Hourly Rate", "Monthly Retainer", "Milestone-based"]

PAYMENT_METHODS = ["Bank Transfer", "UPI", "Cash", "Credit Card", "Cheque"]

def random_date(start_days_ago: int, end_days_ago: int) -> str:
    """Generate random date between start and end days ago."""
    days_ago = random.randint(end_days_ago, start_days_ago)
    date = datetime.date.today() - datetime.timedelta(days=days_ago)
    return date.isoformat()

def random_phone() -> str:
    """Generate random Indian phone number."""
    return f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}"

def random_email(first_name: str, last_name: str, company: str) -> str:
    """Generate email from name and company."""
    company_domain = company.lower().replace(" ", "").replace(".", "")[:15]
    return f"{first_name.lower()}.{last_name.lower()}@{company_domain}.com"

def populate_clients(repo: ClientRepository, count: int = 25) -> list[int]:
    """Create sample clients."""
    print(f"Creating {count} clients...")
    client_ids = []
    
    used_companies = set()
    
    for i in range(count):
        # Ensure unique company names
        company = random.choice(COMPANIES)
        while company in used_companies:
            company = random.choice(COMPANIES)
        used_companies.add(company)
        
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        name = f"{first_name} {last_name}"
        email = random_email(first_name, last_name, company)
        phone = random_phone()
        address = f"{random.randint(1, 999)} {random.choice(['MG Road', 'Brigade Road', 'Residency Road', 'Whitefield', 'Koramangala', 'Indiranagar'])}, Bangalore, Karnataka - {random.randint(560001, 560100)}"
        notes = random.choice([
            "Long-term client with monthly retainer",
            "Referred by previous client",
            "Met at networking event",
            "Prefers email communication",
            "Quick decision maker",
            "Detail-oriented client",
            ""
        ])
        
        client_id = repo.add(name, email, phone, address, company, notes)
        client_ids.append(client_id)
    
    print(f"✓ Created {len(client_ids)} clients")
    return client_ids

def populate_projects(repo: ProjectRepository, client_ids: list[int], count: int = 30) -> list[int]:
    """Create sample projects."""
    print(f"Creating {count} projects...")
    project_ids = []
    
    for i in range(count):
        client_id = random.choice(client_ids)
        project_type = random.choice(PROJECT_TYPES)
        project_name = random.choice(PROJECT_NAMES)
        deadline = random_date(-15, -5)
        budget = random.choice([25000, 35000, 50000, 75000, 100000, 125000, 150000, 200000, 250000, 300000])
        description = f"Comprehensive {project_type.lower()} project including research, design, development, and deployment phases."
        
        # Schema: add(client_id, name, project_type, description, deadline, budget)
        project_id = repo.add(client_id, project_name, project_type, description, deadline, budget)
        
        # Update status separately
        statuses = ["Not Started", "In Progress", "In Progress", "Review", "On Hold", "Completed", "Completed", "Completed"]
        status = random.choice(statuses)
        repo.update_status(project_id, status)
        
        project_ids.append(project_id)
    
    print(f"✓ Created {len(project_ids)} projects")
    return project_ids

def populate_invoices(
    invoice_repo: InvoiceRepository,
    payment_repo: PaymentRepository,
    project_repo: ProjectRepository,
    project_ids: list[int],
    count: int = 35
) -> list[int]:
    """Create sample invoices and payments."""
    print(f"Creating {count} invoices...")
    invoice_ids = []
    
    invoice_number = 1001
    
    for i in range(count):
        project_id = random.choice(project_ids)
        project = project_repo.get_by_id(project_id)
        amount = project["budget"] * random.choice([0.25, 0.33, 0.5, 0.75, 1.0])
        
        # GST calculation
        tax = amount * 0.18
        total = amount + tax
        
        due_date = random_date(-15, -5)
        
        # Determine status
        today = datetime.date.today()
        due_date_obj = datetime.date.fromisoformat(due_date)
        
        if random.random() < 0.65:  # 65% paid
            status = "Paid"
        elif due_date_obj < today:
            status = "Unpaid"  # Will show as Overdue in UI
        else:
            status = "Unpaid"
        
        invoice_num = f"INV-2026-{invoice_number:04d}"
        notes = random.choice([
            "Payment terms: Net 30 days",
            "50% advance, 50% on completion",
            "Monthly retainer invoice",
            "Final project invoice",
            "",
            ""
        ])
        
        # Schema: add(project_id, invoice_number, amount, tax, total, due_date, status, notes)
        invoice_id = invoice_repo.add(project_id, invoice_num, amount, tax, total, due_date, status, notes)
        invoice_ids.append(invoice_id)
        invoice_number += 1
        
        # If paid, create payment record
        if status == "Paid":
            payment_date = due_date  # Simplify: use due date
            payment_mode = random.choice(PAYMENT_METHODS)
            reference = f"TXN{random.randint(100000, 999999)}"
            
            # Schema: add(invoice_id, amount_paid, payment_mode, reference)
            payment_repo.add(invoice_id, total, payment_mode, reference)
    
    print(f"✓ Created {len(invoice_ids)} invoices")
    return invoice_ids

def populate_time_logs(repo: TimeLogRepository, project_ids: list[int], count: int = 80) -> list[int]:
    """Create sample time logs."""
    print(f"Creating {count} time logs...")
    log_ids = []
    
    activities = [
        "Client meeting and requirements gathering",
        "Design mockup creation",
        "Frontend development",
        "Backend API development",
        "Code review and testing",
        "Bug fixing and debugging",
        "Documentation writing",
        "Client presentation and feedback",
        "Research and planning",
        "Design revisions",
        "Database optimization",
        "Performance testing"
    ]
    
    for i in range(count):
        project_id = random.choice(project_ids)
        date = random_date(90, 0)
        hours = random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0])
        description = random.choice(activities)
        
        # Create start and end times
        start_hour = random.randint(9, 16)
        start_time = f"{date} {start_hour:02d}:00:00"
        end_hour = start_hour + int(hours)
        end_minutes = int((hours % 1) * 60)
        end_time = f"{date} {end_hour:02d}:{end_minutes:02d}:00"
        
        # Schema: add(project_id, start_time, end_time, duration_hours, description)
        log_id = repo.add(project_id, start_time, end_time, hours, description)
        log_ids.append(log_id)
    
    print(f"✓ Created {len(log_ids)} time logs")
    return log_ids

def populate_tasks(repo: TaskRepository, project_ids: list[int], count: int = 100) -> list[int]:
    """Create sample tasks."""
    print(f"Creating {count} tasks...")
    task_ids = []
    
    for i in range(count):
        project_id = random.choice(project_ids)
        title = random.choice(TASK_TITLES)
        due_date = random_date(30, -15) if random.random() < 0.7 else ""
        
        # Schema: add(project_id, title, due_date)
        task_id = repo.add(project_id, title, due_date)
        task_ids.append(task_id)
        
        # Mark some as completed
        if random.random() < 0.4:  # 40% completed
            repo.mark_complete(task_id)
    
    print(f"✓ Created {len(task_ids)} tasks")
    return task_ids

def populate_contracts(repo: ContractRepository, project_ids: list[int], count: int = 20) -> list[int]:
    """Create sample contracts."""
    print(f"Creating {count} contracts...")
    contract_ids = []
    
    for i in range(count):
        project_id = random.choice(project_ids)
        contract_type = random.choice(CONTRACT_TYPES)
        
        if contract_type == "Hourly Rate":
            hourly_rate = random.choice([1500, 2000, 2500, 3000, 3500, 4000])
        else:
            hourly_rate = 0
        
        revision_rounds = random.randint(1, 3)
        timeline_days = random.choice([30, 60, 90, 120, 180])
        risk_score = random.randint(1, 10)
        risk_level = "Low" if risk_score <= 3 else "Medium" if risk_score <= 6 else "High"
        
        contract_text = f"""
1. Scope of Work: {random.choice(PROJECT_TYPES)} services as detailed in proposal
2. Payment Terms: {contract_type}
3. Deliverables: As per project milestones and timeline
4. Revision Policy: Up to {revision_rounds} rounds of revisions included
5. Timeline: {timeline_days} days
6. Confidentiality: Both parties agree to maintain confidentiality
7. Intellectual Property: Rights transfer upon full payment
8. Termination: 30 days written notice required
9. Governing Law: Indian Contract Act, 1872
        """.strip()
        
        findings = f"Contract analysis: {risk_level} risk level detected. {random.choice(['Standard terms', 'Favorable terms', 'Review payment schedule', 'Check liability clauses'])}"
        
        # Schema: add(project_id, contract_text, hourly_rate, revision_rounds, timeline_days, risk_score, risk_level, findings)
        contract_id = repo.add(project_id, contract_text, hourly_rate, revision_rounds, timeline_days, risk_score, risk_level, findings)
        contract_ids.append(contract_id)
    
    print(f"✓ Created {len(contract_ids)} contracts")
    return contract_ids

def main():
    """Main function to populate all sample data."""
    print("=" * 60)
    print("SmartDesk Sample Data Population")
    print("=" * 60)
    print()
    
    # Initialize database
    db = Database()
    
    # Initialize repositories
    client_repo = ClientRepository(db)
    project_repo = ProjectRepository(db)
    invoice_repo = InvoiceRepository(db)
    payment_repo = PaymentRepository(db)
    time_log_repo = TimeLogRepository(db)
    task_repo = TaskRepository(db)
    contract_repo = ContractRepository(db)
    
    # Check if data already exists
    existing_clients = len(client_repo.get_all())
    if existing_clients > 0:
        response = input(f"\n⚠ Database already contains {existing_clients} clients. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        print()
    
    # Populate data
    try:
        client_ids = populate_clients(client_repo, count=25)
        project_ids = populate_projects(project_repo, client_ids, count=30)
        invoice_ids = populate_invoices(invoice_repo, payment_repo, project_repo, project_ids, count=40)
        time_log_ids = populate_time_logs(time_log_repo, project_ids, count=100)
        task_ids = populate_tasks(task_repo, project_ids, count=120)
        contract_ids = populate_contracts(contract_repo, project_ids, count=22)
        
        print()
        print("=" * 60)
        print("✓ Sample data population completed successfully!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  • Clients: {len(client_ids)}")
        print(f"  • Projects: {len(project_ids)}")
        print(f"  • Invoices: {len(invoice_ids)}")
        print(f"  • Time Logs: {len(time_log_ids)}")
        print(f"  • Tasks: {len(task_ids)}")
        print(f"  • Contracts: {len(contract_ids)}")
        print()
        print("Total records created: " + str(
            len(client_ids) + len(project_ids) + len(invoice_ids) +
            len(time_log_ids) + len(task_ids) + len(contract_ids)
        ))
        print()
        
    except Exception as e:
        print()
        print(f"✗ Error populating data: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
