"""SmartDesk — Freelancer Management System with Predictive Analytics.

Application entry point. Shows a splash screen, initializes the database,
applies the theme, and launches the main window.
"""
from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QTimer

from app.config import APP_NAME, APP_VERSION, ICON_PATH, ICON_PNG_PATH, SPLASH_PATH
from app.data.database import Database
from app.ui.main_window import MainWindow
from app.ui.styles.theme import apply_dark_theme


def show_error(title: str, message: str) -> None:
    """Show a critical error dialog."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()


def main() -> int:
    # High DPI support
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("SmartDesk")

    # Set application icon
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    elif ICON_PNG_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PNG_PATH)))

    apply_dark_theme(app)

    # Splash screen
    splash = None
    if SPLASH_PATH.exists():
        pixmap = QPixmap(str(SPLASH_PATH))
        splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()

    try:
        # Initialize DB
        if splash:
            splash.showMessage(
                "  Initializing database...",
                Qt.AlignBottom | Qt.AlignLeft,
                Qt.white,
            )
            app.processEvents()

        db = Database()
        db.initialize()

        # Load main window
        if splash:
            splash.showMessage(
                "  Loading interface...",
                Qt.AlignBottom | Qt.AlignLeft,
                Qt.white,
            )
            app.processEvents()

        window = MainWindow(db)

        # Close splash and show window
        if splash:
            splash.finish(window)

        window.show()

    except Exception as e:
        if splash:
            splash.close()
        show_error("Startup Error", f"Failed to start SmartDesk:\n\n{traceback.format_exc()}")
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
