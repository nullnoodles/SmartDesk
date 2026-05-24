"""Build script for SmartDesk — creates a standalone .exe distribution.

Usage:
    python scripts/build.py

This script:
1. Generates the icon (if missing)
2. Trains the ML model (if missing)
3. Runs PyInstaller to create the .exe
4. Copies necessary runtime files to the dist folder
"""
import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist" / "SmartDesk"


def run(cmd: list[str], cwd: Path = ROOT) -> bool:
    """Run a command and return success status."""
    print(f"  → {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ Failed: {result.stderr[:500]}")
        return False
    return True


def main():
    print("=" * 60)
    print("  SmartDesk Build Script")
    print("=" * 60)

    python = sys.executable

    # Step 1: Generate icon if missing
    icon_path = ROOT / "assets" / "icon.ico"
    if not icon_path.exists():
        print("\n[1/4] Generating application icon...")
        if not run([python, "scripts/generate_icon.py"]):
            print("  ⚠ Icon generation failed, continuing without custom icon")
    else:
        print("\n[1/4] Icon already exists ✓")

    # Step 2: Train ML model if missing
    model_path = ROOT / "app" / "ml" / "models" / "clause_classifier.pkl"
    if not model_path.exists():
        print("\n[2/4] Training clause classifier model...")
        if not run([python, "scripts/train_clause_model.py"]):
            print("  ⚠ Model training failed, app will work without NLP features")
    else:
        print("\n[2/4] ML model already trained ✓")

    # Step 3: Run PyInstaller
    print("\n[3/4] Building executable with PyInstaller...")
    print("  This may take 2-5 minutes...")

    # Prefer smartdesk.spec, fall back to legacy solodash.spec for compatibility
    spec_file = "smartdesk.spec" if (ROOT / "smartdesk.spec").exists() else "solodash.spec"

    result = subprocess.run(
        [python, "-m", "PyInstaller", spec_file, "--noconfirm", "--clean"],
        cwd=str(ROOT),
        capture_output=False,
    )
    if result.returncode != 0:
        print("\n  ✗ PyInstaller build failed!")
        print("  Make sure PyInstaller is installed: pip install pyinstaller")
        return 1

    # Step 4: Copy runtime data to dist
    print("\n[4/4] Setting up distribution folder...")

    # Create data and exports directories in dist
    (DIST_DIR / "data").mkdir(exist_ok=True)
    (DIST_DIR / "exports").mkdir(exist_ok=True)

    # Copy .gitkeep files
    (DIST_DIR / "data" / ".gitkeep").touch()
    (DIST_DIR / "exports" / ".gitkeep").touch()

    print("\n" + "=" * 60)
    print("  BUILD COMPLETE ✓")
    print("=" * 60)
    print(f"\n  Output: {DIST_DIR}")
    print(f"  Executable: {DIST_DIR / 'SmartDesk.exe'}")
    print(f"\n  To run: double-click SmartDesk.exe")
    print(f"  To distribute: zip the entire 'SmartDesk' folder")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
