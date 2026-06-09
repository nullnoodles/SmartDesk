"""Test script to check what data is in the projects table."""
from app.data.database import Database

db = Database()
db.initialize()

print("=" * 80)
print("PROJECTS TABLE DATA")
print("=" * 80)

projects = db.execute("""
    SELECT p.name, c.name as client_name, p.type, p.status, p.deadline, p.budget
    FROM projects p
    LEFT JOIN clients c ON p.client_id = c.id
    ORDER BY p.created_date DESC
    LIMIT 10
""")

if not projects:
    print("No projects found in database!")
else:
    print(f"\nFound {len(projects)} projects:\n")
    for i, proj in enumerate(projects, 1):
        print(f"{i}. {proj['name']}")
        print(f"   Client: {proj['client_name']}")
        print(f"   Type: '{proj['type']}'")
        print(f"   Status: {proj['status']}")
        print(f"   Deadline: {proj['deadline']}")
        print(f"   Budget: {proj['budget']}")
        print()

print("=" * 80)
