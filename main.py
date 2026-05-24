"""SmartDesk — Freelancer Management System with Predictive Analytics.

Application entry point. Shows a splash screen, initializes the database,
applies the theme, and launches the main window.
"""
from __future__ import annotations

import sys
import traceback

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen

from app.config import (
    APP_NAME,
    APP_VERSION,
    ICON_PATH,
    ICON_PNG_PATH,
    SPLASH_PATH,
)
from app.core.settings_service import SettingsService
from app.data.database import Database
from app.ui.main_window import MainWindow
from app.ui.styles.theme import apply_dark_theme
from app.ui.widgets.welcome_dialog import WelcomeDialog
from app.utils.logger import get_logger, log_exception


def show_error(title: str, message: str) -> None:
    """Show a critical error dialog."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()


def _maybe_show_welcome(window: MainWindow, db: Database) -> None:
    """If this is the first run, greet the user and optionally seed sample data."""
    settings = SettingsService(db)
    if not settings.is_first_run():
        return

    dialog = WelcomeDialog(parent=window)
    dialog.exec()

    if dialog.load_sample_data:
        try:
            from scripts import seed_data  # type: ignore

            if hasattr(seed_data, "seed"):
                seed_data.seed()
            elif hasattr(seed_data, "main"):
                seed_data.main()
        except Exception:
            log_exception("Sample data seed failed")

    settings.mark_first_run_done()

    # Navigate to settings so the user can fill in business info immediately,
    # or refresh dashboard if they loaded sample data first.
    try:
        if dialog.load_sample_data:
            window.show_page("dashboard")
        else:
            window.show_page("settings")
    except Exception:
        pass


def main() -> int:
    logger = get_logger()
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("SmartDesk")

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
        if splash:
            splash.showMessage(
                "  Initializing database...",
                Qt.AlignBottom | Qt.AlignLeft,
                Qt.white,
            )
            app.processEvents()

        db = Database()
        db.initialize()

        if splash:
            splash.showMessage(
                "  Loading interface...",
                Qt.AlignBottom | Qt.AlignLeft,
                Qt.white,
            )
            app.processEvents()

        window = MainWindow(db)

        if splash:
            splash.finish(window)

        window.show()

        # Show welcome on first run (after window is up)
        QTimer.singleShot(150, lambda: _maybe_show_welcome(window, db))

    except Exception:
        if splash:
            splash.close()
        log_exception("Startup error")
        show_error(
            "Startup Error",
            f"Failed to start {APP_NAME}:\n\n{traceback.format_exc()}",
        )
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
