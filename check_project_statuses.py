"""Check what project statuses exist and their counts."""
from app.data.database import Database

db = Database()
db.initialize()

print("PROJECT STATUS BREAKDOWN:")
print("=" * 40)

statuses = db.execute('SELECT status, COUNT(*) as count FROM projects GROUP BY status ORDER BY count DESC')
total = sum(s["count"] for s in statuses)

for status in statuses:
    print(f'{status["status"]}: {status["count"]} projects')

print(f"\nTotal: {total} projects")

# Current Active Projects query
current_active = db.execute("SELECT COUNT(*) as cnt FROM projects WHERE status='In Progress'")[0]["cnt"]
print(f"\nCurrent 'Active Projects' query result: {current_active}")

# What should be considered "active"?
active_statuses = ['In Progress', 'Review', 'On Hold']
active_query = f"SELECT COUNT(*) as cnt FROM projects WHERE status IN ({','.join(['?']*len(active_statuses))})"
suggested_active = db.execute(active_query, active_statuses)[0]["cnt"]
print(f"Suggested 'Active Projects' (In Progress + Review + On Hold): {suggested_active}")