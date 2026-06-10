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
    window.show_page("projects")
    window.show()
    
    def save_pixmap():
        QApplication.processEvents()
        pixmap = window.grab()
        
        output_dir = Path("C:/Users/nirma/.gemini/antigravity-ide/brain/3cde02ce-9235-45cd-b4a5-92254dfba3df")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pixmap.save(str(output_dir / "projects_screenshot.png"))
        print("Projects page screenshot saved.")
        app.quit()
        
    QTimer.singleShot(1000, save_pixmap)
    sys.exit(app.exec())

if __name__ == "__main__":
    capture()
