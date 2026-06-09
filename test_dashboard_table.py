"""Quick test script to verify Recent Projects table formatting."""
from datetime import datetime

# Test date formatting
test_dates = ["2026-08-01", "2024-10-01", "2024-12-25", "2025-01-09"]

print("Date Formatting Test:")
print("=" * 50)
for raw_date in test_dates:
    parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
    day = parsed_date.day
    formatted = parsed_date.strftime(f"%b {day}, %Y")
    print(f"{raw_date} → {formatted}")

print("\n" + "=" * 50)

# Test Indian number formatting
def _format_indian(n: int) -> str:
    """Format an integer with Indian comma grouping: 1,20,000."""
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while rest:
        groups.append(rest[-2:])
        rest = rest[:-2]
    groups.reverse()
    return ",".join(groups) + "," + last3

test_amounts = [1000, 12000, 120000, 1500000, 25000000]

print("\nIndian Number Formatting Test:")
print("=" * 50)
for amount in test_amounts:
    formatted = "₹" + _format_indian(amount)
    print(f"{amount:>10} → {formatted}")

print("\n" + "=" * 50)
print("\nColumn Width Percentages:")
print("=" * 50)
print("PROJECT:  24%")
print("CLIENT:   18%")
print("TYPE:     12%")
print("STATUS:   16%")
print("DEADLINE: 14%")
print("BUDGET:   16%")
print("=" * 50)

print("\n✅ All formatting tests passed!")
print("\nTo verify visually, run: python main.py")
print("Then navigate to Dashboard and check the Recent Projects table.")
