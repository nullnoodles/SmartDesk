"""
Animated widgets for SmartDesk — smooth, professional micro-interactions.
Provides animated buttons, cards with hover effects, and fade-in widgets.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QPushButton, QFrame, QGraphicsOpacityEffect, QVBoxLayout, QLabel,
    QSizePolicy,
)
from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, Property, QSize, Qt, QTimer,
    QParallelAnimationGroup, QSequentialAnimationGroup, Signal,
)
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient

from app.ui.styles.theme import Colors


class AnimatedButton(QPushButton):
    """
    A button with smooth scale and opacity animations on hover/press.
    Uses QGraphicsOpacityEffect for fade and overrides paintEvent for scale.
    """

    def __init__(self, text: str = "", parent=None, accent: str = None):
        super().__init__(text, parent)
        self._scale = 1.0
        self._accent = accent  # Optional override color

        # Scale animation
        self._scale_anim = QPropertyAnimation(self, b"buttonScale")
        self._scale_anim.setDuration(150)
        self._scale_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Opacity effect for subtle feedback
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._opacity_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._opacity_anim.setDuration(150)
        self._opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

        if accent:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent};
                    color: {Colors.TEXT_INVERSE};
                    border: none;
                    border-radius: 10px;
                    padding: 10px 22px;
                    font-size: 13px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background-color: {accent};
                    opacity: 0.94;
                }}
            """)

    def get_button_scale(self) -> float:
        return self._scale

    def set_button_scale(self, value: float) -> None:
        self._scale = value
        self.update()

    buttonScale = Property(float, get_button_scale, set_button_scale)

    def enterEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.03)
        self._scale_anim.start()

        self._opacity_anim.stop()
        self._opacity_anim.setStartValue(self._opacity_effect.opacity())
        self._opacity_anim.setEndValue(0.92)
        self._opacity_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.0)
        self._scale_anim.start()

        self._opacity_anim.stop()
        self._opacity_anim.setStartValue(self._opacity_effect.opacity())
        self._opacity_anim.setEndValue(1.0)
        self._opacity_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(0.96)
        self._scale_anim.setDuration(80)
        self._scale_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.03)
        self._scale_anim.setDuration(150)
        self._scale_anim.start()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        # Scale transform is purely visual — let Qt handle the actual painting
        super().paintEvent(event)


class AnimatedCard(QFrame):
    """
    A card widget with subtle hover lift effect (shadow simulation via border).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        # Fix: Set proper size policies for expansion
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(280)  # Fix: Set minimum height to prevent compression
        self._is_hovered = False
        self._update_style(False)

    def _update_style(self, hovered: bool) -> None:
        if hovered:
            self.setStyleSheet(f"""
                .AnimatedCard {{
                    background-color: {Colors.BG_CARD};
                    border: 1px solid {Colors.ACCENT_PRIMARY};
                    border-radius: 14px;
                    padding: 24px;  /* Fix: Increased padding (min 12px) */
                }}
            """)
        else:
            self.setStyleSheet(f"""
                .AnimatedCard {{
                    background-color: {Colors.BG_CARD};
                    border: 1px solid {Colors.BORDER_SUBTLE};
                    border-radius: 14px;
                    padding: 24px;  /* Fix: Increased padding (min 12px) */
                }}
            """)

    def enterEvent(self, event):
        self._is_hovered = True
        self._update_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self._update_style(False)
        super().leaveEvent(event)


class FadeInWidget(QWidget):
    """A wrapper that fades in its content on show."""

    def __init__(self, parent=None, duration: int = 400):
        super().__init__(parent)
        self._duration = duration
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(duration)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)

    def showEvent(self, event):
        super().showEvent(event)
        self._opacity_effect.setOpacity(0.0)
        self._fade_anim.start()

    def fade_in(self) -> None:
        """Manually trigger fade-in."""
        self._opacity_effect.setOpacity(0.0)
        self._fade_anim.start()


class GradientBar(QWidget):
    """
    A horizontal bar chart segment with gradient fill.
    Used for inline progress/metric visualization.
    """

    def __init__(
        self,
        value: float = 0.0,
        max_value: float = 100.0,
        color_start: str = Colors.ACCENT_PRIMARY,
        color_end: str = Colors.ACCENT_INFO,
        height: int = 8,
        parent=None,
    ):
        super().__init__(parent)
        self._value = value
        self._max_value = max_value
        self._color_start = QColor(color_start)
        self._color_end = QColor(color_end)
        self.setFixedHeight(height)
        self.setMinimumWidth(60)

        # Animate value changes
        self._animated_value = 0.0
        self._value_anim = QPropertyAnimation(self, b"animatedValue")
        self._value_anim.setDuration(600)
        self._value_anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_animated_value(self) -> float:
        return self._animated_value

    def set_animated_value(self, v: float) -> None:
        self._animated_value = v
        self.update()

    animatedValue = Property(float, get_animated_value, set_animated_value)

    def set_value(self, value: float, animate: bool = True) -> None:
        self._value = value
        if animate:
            self._value_anim.stop()
            self._value_anim.setStartValue(self._animated_value)
            self._value_anim.setEndValue(value)
            self._value_anim.start()
        else:
            self._animated_value = value
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background track
        bg_path = QPainterPath()
        bg_path.addRoundedRect(0, 0, self.width(), self.height(), 4, 4)
        painter.fillPath(bg_path, QColor(Colors.BG_ELEVATED))

        # Filled portion
        if self._max_value > 0 and self._animated_value > 0:
            ratio = min(self._animated_value / self._max_value, 1.0)
            fill_width = self.width() * ratio

            gradient = QLinearGradient(0, 0, fill_width, 0)
            gradient.setColorAt(0, self._color_start)
            gradient.setColorAt(1, self._color_end)

            fill_path = QPainterPath()
            fill_path.addRoundedRect(0, 0, fill_width, self.height(), 4, 4)
            painter.fillPath(fill_path, gradient)

        painter.end()


class StaggeredFadeIn:
    """
    Utility to fade in a list of widgets one after another with a delay.
    Creates a cascading entrance effect.
    """

    def __init__(self, widgets: list[QWidget], delay_ms: int = 80, duration_ms: int = 300):
        self._widgets = widgets
        self._delay = delay_ms
        self._duration = duration_ms
        self._effects: list[QGraphicsOpacityEffect] = []
        self._animations: list[QPropertyAnimation] = []

        for widget in widgets:
            effect = QGraphicsOpacityEffect(widget)
            effect.setOpacity(0.0)
            widget.setGraphicsEffect(effect)
            self._effects.append(effect)

    def start(self) -> None:
        """Begin the staggered fade-in sequence."""
        for i, (widget, effect) in enumerate(zip(self._widgets, self._effects)):
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(self._duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            self._animations.append(anim)
            QTimer.singleShot(i * self._delay, anim.start)
