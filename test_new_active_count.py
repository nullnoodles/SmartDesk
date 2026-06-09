"""Test the new Active Projects query."""
from app.data.database import Database

db = Database()
db.initialize()

# Test the new query
result = db.execute("SELECT COUNT(*) as cnt FROM projects WHERE status IN ('In Progress', 'Review', 'Not Started')")
new_count = result[0]["cnt"]

# Show breakdown
breakdown = db.execute("""
    SELECT status, COUNT(*) as count 
    FROM projects 
    WHERE status IN ('In Progress', 'Review', 'Not Started') 
    GROUP BY status
""")

print(f"New Active Projects count: {new_count}")
print("\nBreakdown:")
for row in breakdown:
    print(f"  {row['status']}: {row['count']}")

print(f"\nOld query (just 'In Progress'): 2")
print(f"New query (In Progress + Review + Not Started): {new_count}")
print(f"Increase: +{new_count - 2} projects")