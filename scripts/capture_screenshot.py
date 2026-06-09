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
    
    # Force first run settings to false so welcome dialog doesn't block
    db.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('first_run', '0')")
    
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    
    window = MainWindow(db)
    window.resize(1280, 1024)
    window.show_page("clients")
    window.show()
    
    def save_pixmap():
        QApplication.processEvents()
        
        pixmap = window.grab()
        
        output_dir = Path("C:/Users/nirma/.gemini/antigravity-ide/brain/af53334f-84e0-4f32-a27f-41cb2b3cd43f")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pixmap.save(str(output_dir / "clients_screenshot.png"))
        print("Clients main screenshot saved.")
        
        # Find the specific QScrollArea for the clients page
        scroll_area = None
        from PySide6.QtWidgets import QScrollArea
        for sa in window.findChildren(QScrollArea):
            if sa.widget() and sa.widget().objectName() == "clients_content":
                scroll_area = sa
                break
                
        if scroll_area:
            scroll_area.widget().adjustSize()
            QApplication.processEvents()
            max_val = scroll_area.verticalScrollBar().maximum()
            print(f"Scrolling clients scroll area to maximum: {max_val}")
            scroll_area.verticalScrollBar().setValue(max_val)
            QApplication.processEvents()
            QTimer.singleShot(800, save_scrolled_pixmap)
        else:
            print("Clients QScrollArea not found!")
            app.quit()

    def save_scrolled_pixmap():
        QApplication.processEvents()
        pixmap = window.grab()
        output_dir = Path("C:/Users/nirma/.gemini/antigravity-ide/brain/af53334f-84e0-4f32-a27f-41cb2b3cd43f")
        pixmap.save(str(output_dir / "clients_scrolled_screenshot.png"))
        print("Clients scrolled screenshot saved.")
        app.quit()
        
    QTimer.singleShot(2000, save_pixmap)
    sys.exit(app.exec())

if __name__ == "__main__":
    capture()
