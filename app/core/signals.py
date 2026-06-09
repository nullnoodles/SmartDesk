from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


class DataChangedSignal(QObject):
    """Global signal object — one instance lives on QApplication as app.data_changed."""
    signal = Signal()


def emit_data_changed() -> None:
    """Emit the global data_changed signal. Call this after any DB write."""
    app = QApplication.instance()
    if app and hasattr(app, "data_changed"):
        app.data_changed.signal.emit()
