"""Quick verification script for QSS migration."""
from pathlib import Path

def verify_qss_file():
    """Check QSS file exists and has content."""
    qss_path = Path("app/ui/styles/style.qss")
    if not qss_path.exists():
        print("❌ style.qss not found!")
        return False
    
    content = qss_path.read_text(encoding="utf-8")
    lines = len(content.split('\n'))
    size_kb = len(content) / 1024
    
    print(f"✅ style.qss found")
    print(f"   Lines: {lines}")
    print(f"   Size: {size_kb:.1f} KB")
    
    # Check for key selectors
    required = [
        "#sidebar",
        "#top_bar",
        ".card",
        "#animated_card",
        "#stat_card",
        "QPushButton[accent=\"primary\"]",
        "QLineEdit",
        "QTableWidget",
        "QScrollBar",
    ]
    
    missing = [sel for sel in required if sel not in content]
    if missing:
        print(f"❌ Missing selectors: {missing}")
        return False
    
    print(f"✅ All {len(required)} key selectors present")
    return True

def verify_theme_py():
    """Check theme.py loads QSS."""
    theme_path = Path("app/ui/styles/theme.py")
    if not theme_path.exists():
        print("❌ theme.py not found!")
        return False
    
    content = theme_path.read_text()
    
    checks = [
        ("_load_qss", "QSS loading function"),
        ("_load_inter_fonts", "Font loading function"),
        ("apply_dark_theme", "Theme application function"),
        ("style.qss", "QSS file reference"),
    ]
    
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc} present")
        else:
            print(f"❌ {desc} missing!")
            return False
    
    return True

def verify_sidebar_width():
    """Check sidebar width is 240px or 230px."""
    sidebar_path = Path("app/ui/widgets/sidebar.py")
    if not sidebar_path.exists():
        print("❌ sidebar.py not found!")
        return False
    
    content = sidebar_path.read_text(encoding="utf-8")
    
    if "setFixedWidth(240)" in content or "setFixedWidth(230)" in content:
        print("✅ Sidebar width is valid (240px or 230px)")
        return True
    elif "setFixedWidth(260)" in content:
        print("❌ Sidebar still at 260px - should be 240px/230px")
        return False
    else:
        print("⚠️  Could not verify sidebar width")
        return False

def main():
    print("=" * 60)
    print("SmartDesk QSS Migration Verification")
    print("=" * 60)
    print()
    
    results = []
    
    print("[1/3] Checking QSS stylesheet...")
    results.append(verify_qss_file())
    print()
    
    print("[2/3] Checking theme.py configuration...")
    results.append(verify_theme_py())
    print()
    
    print("[3/3] Checking sidebar width...")
    results.append(verify_sidebar_width())
    print()
    
    print("=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED - QSS migration successful!")
        print()
        print("Next steps:")
        print("1. Run: python main.py")
        print("2. Navigate through all pages")
        print("3. Verify colors match Studio Graphite palette")
        print("4. Check spacing (32px padding, 24px gaps)")
    else:
        print("❌ SOME CHECKS FAILED - review output above")
    print("=" * 60)

if __name__ == "__main__":
    main()
