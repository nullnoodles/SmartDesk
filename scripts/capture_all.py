import sys
import os
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.data.database import Database
from app.ui.main_window import MainWindow
from app.ui.styles.theme import apply_dark_theme

def capture():
    db = Database()
    db.initialize()
    
    # Ensure welcome dialog doesn't block
    db.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('first_run', '0')")
    
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    
    window = MainWindow(db)
    window.resize(1280, 1024)
    
    output_dir = Path("C:/Users/nirma/.gemini/antigravity-ide/brain/a09c17ae-7b6d-477c-9d55-f858a0594cea")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_dashboard():
        window.show_page("dashboard")
        QApplication.processEvents()
        pixmap = window.grab()
        pixmap.save(str(output_dir / "dashboard_screenshot.png"))
        print("Dashboard screenshot saved.")
        
        QTimer.singleShot(1000, save_clients)
        
    def save_clients():
        window.show_page("clients")
        QApplication.processEvents()
        pixmap = window.grab()
        pixmap.save(str(output_dir / "clients_screenshot.png"))
        print("Clients screenshot saved.")
        app.quit()
        
    QTimer.singleShot(1000, save_dashboard)
    sys.exit(app.exec())

if __name__ == "__main__":
    capture()
