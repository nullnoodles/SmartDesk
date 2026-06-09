"""AI Analytics page — ML predictions, income forecast, pricing advisor — Studio Graphite."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QGroupBox, QFormLayout, QComboBox,
    QDoubleSpinBox, QSpinBox, QTextEdit, QMessageBox, QFrame,
    QScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt

from app.data.database import Database
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton, AnimatedCard, GradientBar
from app.ui.widgets.page_header import PageHeader


class AnalyticsPage(QWidget):
    """AI-powered analytics: pricing, payment prediction, income forecast."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._pricing_advisor = None
        self._payment_predictor = None
        self._income_forecaster = None

        # Main page layout with scroll area
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        # Content layout - standardized spacing
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(28)
        layout.setAlignment(Qt.AlignTop)

        # Header
        header = PageHeader(
            title="AI Analytics",
            subtitle="Predictions and recommendations powered by your data",
        )

        badge = QLabel("🤖 ML-Powered")
        badge.setStyleSheet(
            f"background-color: rgba(124, 138, 244, 0.10); "
            f"color: {Colors.ACCENT_PRIMARY_LIGHT}; "
            f"border: 1px solid {Colors.BORDER_SUBTLE}; "
            f"border-radius: 999px; padding: 6px 14px; "
            f"font-size: 12px; font-weight: 700;"
        )
        header.add_action(badge)
        layout.addWidget(header)

        # Tabs for different ML features
        tabs = QTabWidget()
        tabs.addTab(self._build_pricing_tab(), "💰 Smart Pricing")
        tabs.addTab(self._build_payment_tab(), "⏰ Payment Predictor")
        tabs.addTab(self._build_forecast_tab(), "📈 Income Forecast")
        layout.addWidget(tabs)

        # Set scroll area widget and add to page
        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

    def _build_pricing_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(16)

        # Input card
        input_card = AnimatedCard()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 18, 20, 18)
        input_layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.pricing_type = QComboBox()
        self.pricing_type.addItems(["Design", "Video", "Writing", "Music", "Development", "General"])
        self.pricing_hours = QDoubleSpinBox()
        self.pricing_hours.setRange(1, 500)
        self.pricing_hours.setValue(10)
        self.pricing_hours.setSuffix(" hrs")
        self.pricing_revisions = QSpinBox()
        self.pricing_revisions.setRange(0, 10)
        self.pricing_revisions.setValue(2)
        self.pricing_desc = QTextEdit()
        self.pricing_desc.setMaximumHeight(60)
        self.pricing_desc.setPlaceholderText("Brief project description (keywords affect pricing)...")

        form.addRow("Project Type", self.pricing_type)
        form.addRow("Estimated Hours", self.pricing_hours)
        form.addRow("Revision Rounds", self.pricing_revisions)
        form.addRow("Description", self.pricing_desc)
        input_layout.addLayout(form)

        btn = AnimatedButton("Get Price Suggestion", accent=Colors.ACCENT_PRIMARY)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._run_pricing)
        input_layout.addWidget(btn)
        layout.addWidget(input_card)

        # Result card
        self.pricing_result_card = AnimatedCard()
        result_layout = QVBoxLayout(self.pricing_result_card)
        result_layout.setContentsMargins(20, 18, 20, 18)

        self.pricing_result = QLabel("Enter details above and click to get a price range.")
        self.pricing_result.setWordWrap(True)
        self.pricing_result.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        result_layout.addWidget(self.pricing_result)
        layout.addWidget(self.pricing_result_card)

        layout.addStretch()
        return widget

    def _build_payment_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(16)

        # Input card
        input_card = AnimatedCard()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 18, 20, 18)
        input_layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.pay_amount = QDoubleSpinBox()
        self.pay_amount.setRange(100, 10_000_000)
        self.pay_amount.setPrefix("₹ ")
        self.pay_amount.setValue(10000)
        self.pay_days = QSpinBox()
        self.pay_days.setRange(1, 90)
        self.pay_days.setValue(14)
        self.pay_days.setSuffix(" days")
        self.pay_type = QComboBox()
        self.pay_type.addItems(["Design", "Video", "Writing", "Music", "Development", "General"])

        form.addRow("Invoice Amount", self.pay_amount)
        form.addRow("Days to Due", self.pay_days)
        form.addRow("Project Type", self.pay_type)
        input_layout.addLayout(form)

        btn = AnimatedButton("Predict Payment Timing", accent=Colors.ACCENT_PRIMARY)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._run_payment_prediction)
        input_layout.addWidget(btn)
        layout.addWidget(input_card)

        # Result card
        self.payment_result_card = AnimatedCard()
        result_layout = QVBoxLayout(self.payment_result_card)
        result_layout.setContentsMargins(20, 18, 20, 18)
        result_layout.setSpacing(10)

        self.payment_result = QLabel("Predicts whether this invoice will be paid on time, late, or very late.")
        self.payment_result.setWordWrap(True)
        self.payment_result.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        result_layout.addWidget(self.payment_result)

        # Probability bars
        self.prob_bars: dict[str, dict] = {}
        for label, color in [("On Time", Colors.ACCENT_SUCCESS), ("Late", Colors.ACCENT_WARNING), ("Very Late", Colors.ACCENT_DANGER)]:
            bar_row = QHBoxLayout()
            bar_label = QLabel(label)
            bar_label.setFixedWidth(70)
            bar_label.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
            bar_row.addWidget(bar_label)

            bar = GradientBar(value=0, max_value=100, color_start=color, color_end=color, height=8)
            bar_row.addWidget(bar, stretch=1)

            pct_label = QLabel("0%")
            pct_label.setFixedWidth(40)
            pct_label.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
            bar_row.addWidget(pct_label)

            result_layout.addLayout(bar_row)
            self.prob_bars[label] = {"bar": bar, "label": pct_label}

        layout.addWidget(self.payment_result_card)
        layout.addStretch()
        return widget

    def _build_forecast_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(16)

        # Action card
        action_card = AnimatedCard()
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(20, 18, 20, 18)
        action_layout.setSpacing(12)

        desc = QLabel("Generate a 3-month income forecast based on your payment history using ARIMA / moving average models.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        action_layout.addWidget(desc)

        btn = AnimatedButton("📈  Generate 3-Month Forecast", accent=Colors.ACCENT_PRIMARY)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._run_forecast)
        action_layout.addWidget(btn)
        layout.addWidget(action_card)

        # Result card
        self.forecast_result_card = AnimatedCard()
        result_layout = QVBoxLayout(self.forecast_result_card)
        result_layout.setContentsMargins(20, 18, 20, 18)
        result_layout.setSpacing(10)

        self.forecast_result = QLabel("Click above to forecast your income for the next 3 months.")
        self.forecast_result.setWordWrap(True)
        self.forecast_result.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        result_layout.addWidget(self.forecast_result)

        # Forecast bars
        self.forecast_bars: list[dict] = []
        for i in range(3):
            bar_row = QHBoxLayout()
            month_label = QLabel(f"Month {i+1}")
            month_label.setFixedWidth(70)
            month_label.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
            bar_row.addWidget(month_label)

            bar = GradientBar(
                value=0, max_value=100000,
                color_start=Colors.ACCENT_PRIMARY,
                color_end=Colors.ACCENT_INFO,
                height=10,
            )
            bar_row.addWidget(bar, stretch=1)

            amount_label = QLabel("—")
            amount_label.setFixedWidth(100)
            amount_label.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
            bar_row.addWidget(amount_label)

            result_layout.addLayout(bar_row)
            self.forecast_bars.append({"bar": bar, "month_label": month_label, "amount_label": amount_label})

        layout.addWidget(self.forecast_result_card)
        layout.addStretch()
        return widget

    # ------------------------------------------------------------------
    # Lazy-loaded ML modules (avoids heavy imports at startup)
    # ------------------------------------------------------------------

    @property
    def pricing_advisor(self):
        if self._pricing_advisor is None:
            from app.ml.pricing_advisor import PricingAdvisor
            self._pricing_advisor = PricingAdvisor(self.db)
        return self._pricing_advisor

    @property
    def payment_predictor(self):
        if self._payment_predictor is None:
            from app.ml.payment_predictor import PaymentPredictor
            self._payment_predictor = PaymentPredictor(self.db)
        return self._payment_predictor

    @property
    def income_forecaster(self):
        if self._income_forecaster is None:
            from app.ml.income_forecaster import IncomeForecaster
            self._income_forecaster = IncomeForecaster(self.db)
        return self._income_forecaster

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _run_pricing(self) -> None:
        result = self.pricing_advisor.suggest_price(
            project_type=self.pricing_type.currentText(),
            estimated_hours=self.pricing_hours.value(),
            description=self.pricing_desc.toPlainText(),
            revision_rounds=self.pricing_revisions.value(),
        )
        text = (
            f"<b style='color:{Colors.ACCENT_PRIMARY}'>Suggested Price Range</b><br><br>"
            f"<span style='font-size:20px; font-weight:700; color:{Colors.ACCENT_SUCCESS}'>₹{result['low']:,.0f}</span>"
            f" — "
            f"<span style='font-size:20px; font-weight:700; color:{Colors.ACCENT_PRIMARY}'>₹{result['mid']:,.0f}</span>"
            f" — "
            f"<span style='font-size:20px; font-weight:700; color:{Colors.ACCENT_WARNING}'>₹{result['high']:,.0f}</span>"
            f"<br><br>"
            f"<b>Effective Rate:</b> ₹{result['effective_hourly_rate']:,.0f}/hr<br><br>"
            f"<b>Reasoning:</b><br>{'<br>'.join(result['reasoning'])}"
        )
        self.pricing_result.setText(text)
        self.pricing_result.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_PRIMARY}; background: transparent;")

    def _run_payment_prediction(self) -> None:
        result = self.payment_predictor.predict(
            amount=self.pay_amount.value(),
            days_to_due=self.pay_days.value(),
            project_type=self.pay_type.currentText(),
        )
        if result["prediction"] == "unknown":
            self.payment_result.setText(f"⚠️ {result['message']}")
            self.payment_result.setStyleSheet(f"font-size: 14px; color: {Colors.ACCENT_WARNING}; background: transparent;")
        else:
            pred_colors = {"on_time": Colors.ACCENT_SUCCESS, "late": Colors.ACCENT_WARNING, "very_late": Colors.ACCENT_DANGER}
            color = pred_colors.get(result["prediction"], Colors.TEXT_PRIMARY)
            self.payment_result.setText(
                f"<span style='color:{color}; font-size:20px; font-weight:700;'>"
                f"{result['prediction'].replace('_', ' ').title()}</span><br>"
                f"<span style='color:{Colors.TEXT_SECONDARY}'>Confidence: {result['confidence']}%</span>"
            )
            self.payment_result.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_PRIMARY}; background: transparent;")

            # Update probability bars
            probs = result.get("probabilities", {})
            mapping = {"On Time": "on_time", "Late": "late", "Very Late": "very_late"}
            for label, key in mapping.items():
                pct = probs.get(key, 0)
                self.prob_bars[label]["bar"].set_value(pct, animate=True)
                self.prob_bars[label]["label"].setText(f"{pct}%")

    def _run_forecast(self) -> None:
        result = self.income_forecaster.forecast(months_ahead=3)
        if result.get("message"):
            self.forecast_result.setText(f"⚠️ {result['message']}")
            self.forecast_result.setStyleSheet(f"font-size: 14px; color: {Colors.ACCENT_WARNING}; background: transparent;")
        else:
            self.forecast_result.setText(
                f"<b style='color:{Colors.ACCENT_PRIMARY}'>Method:</b> {result['method']}"
            )
            self.forecast_result.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_PRIMARY}; background: transparent;")

            # Update forecast bars
            forecasts = result.get("forecast", [])
            max_val = max((f["predicted_income"] for f in forecasts), default=1)
            for i, f_data in enumerate(forecasts[:3]):
                self.forecast_bars[i]["month_label"].setText(f_data["month"])
                self.forecast_bars[i]["bar"]._max_value = max_val * 1.2
                self.forecast_bars[i]["bar"].set_value(f_data["predicted_income"], animate=True)
                self.forecast_bars[i]["amount_label"].setText(f"₹{f_data['predicted_income']:,.0f}")

    def refresh(self) -> None:
        pass  # Analytics page doesn't need refresh on switch
