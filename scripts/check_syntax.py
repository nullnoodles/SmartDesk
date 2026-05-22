"""Quick syntax check for all Python files in the project."""
import ast
from pathlib import Path

errors = []
for f in Path("app").rglob("*.py"):
    try:
        ast.parse(f.read_text(encoding="utf-8"))
    except SyntaxError as e:
        errors.append(f"{f}: {e}")

for f in [Path("main.py")]:
    try:
        ast.parse(f.read_text(encoding="utf-8"))
    except SyntaxError as e:
        errors.append(f"{f}: {e}")

if errors:
    print("SYNTAX ERRORS:")
    for err in errors:
        print(f"  {err}")
else:
    print(f"All Python files parse OK ({len(list(Path('app').rglob('*.py'))) + 1} files)")
