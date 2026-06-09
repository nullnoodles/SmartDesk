"""Enhanced Contracts page — Modern Risk Analyzer UI with 5 Critical Areas."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.data.database import Database
from app.data.repositories.contract_repo import ContractRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton, AnimatedCard, GradientBar
from app.ui.widgets.page_header import PageHeader


class RiskCriteriaCard(AnimatedCard):
    """Card showing individual risk criterion with icon and score."""
    
    def __init__(self, title: str, icon: str, description: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.score = 0
        self.risk_level = "LOW"
        self.findings = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        
        # Header row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            f"font-size: 32px; background: transparent;"
        )
        header_row.addWidget(icon_label)
        
        # Title column
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        title_col.addWidget(self.title_label)
        
        self.desc_label = QLabel(description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(
            f"font-size: 11px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )
        title_col.addWidget(self.desc_label)
        
        header_row.addLayout(title_col, 1)
        header_row.addStretch()
        
        # Score badge
        self.score_badge = QLabel("—")
        self.score_badge.setAlignment(Qt.AlignCenter)
        self.score_badge.setFixedSize(50, 50)
        self.score_badge.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 2px solid {Colors.BORDER_SUBTLE}; "
            f"border-radius: 25px; "
            f"font-size: 16px; font-weight: 700; "
            f"color: {Colors.TEXT_SECONDARY};"
        )
        header_row.addWidget(self.score_badge)
        
        layout.addLayout(header_row)
        
        # Progress bar
        self.progress_bar = GradientBar(
            value=0,
            max_value=40,
            color_start=Colors.ACCENT_SUCCESS,
            color_end=Colors.ACCENT_DANGER,
            height=6,
        )
        layout.addWidget(self.progress_bar)
        
        # Findings list (hidden initially)
        self.findings_widget = QWidget()
        findings_layout = QVBoxLayout(self.findings_widget)
        findings_layout.setContentsMargins(0, 8, 0, 0)
        findings_layout.setSpacing(6)
        
        self.findings_container = QVBoxLayout()
        findings_layout.addLayout(self.findings_container)
        
        layout.addWidget(self.findings_widget)
        self.findings_widget.hide()
        
        self.setMinimumHeight(120)
    
    def set_result(self, score: int, risk_level: str, findings: list[str]):
        """Update card with analysis results."""
        self.score = score
        self.risk_level = risk_level
        self.findings = findings
        
        # Update score badge
        self.score_badge.setText(str(score))
        
        # Color based on risk level
        risk_colors = {
            "CRITICAL": Colors.ACCENT_DANGER,
            "HIGH": Colors.ACCENT_WARNING,
            "MEDIUM": Colors.ACCENT_INFO,
            "LOW": Colors.ACCENT_SUCCESS,
        }
        color = risk_colors.get(risk_level, Colors.TEXT_SECONDARY)
        
        self.score_badge.setStyleSheet(
            f"background-color: {color}; "
            f"border: 2px solid {color}; "
            f"border-radius: 25px; "
            f"font-size: 16px; font-weight: 700; "
            f"color: #FFFFFF;"
        )
        
        # Update progress bar
        self.progress_bar.set_value(min(score, 40), animate=True)
        
        # Show findings
        if findings:
            self.findings_widget.show()
            
            # Clear old findings
            for i in reversed(range(self.findings_container.count())):
                self.findings_container.itemAt(i).widget().deleteLater()
            
            # Add new findings
            for finding in findings:
                finding_label = QLabel(finding)
                finding_label.setWordWrap(True)
                finding_label.setStyleSheet(
                    f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; "
                    f"background: transparent; padding: 4px 0;"
                )
                self.findings_container.addWidget(finding_label)
        else:
            self.findings_widget.hide()


class ContractsPage(QWidget):
    """Enhanced contract analysis with visual risk breakdown."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.contract_repo = ContractRepository(db)
        self._risk_analyzer = None
        self._contract_parser = None
        
        # Risk criterion cards
        self.risk_cards = {}

        self._build_ui()
        self.refresh()

    @property
    def risk_analyzer(self):
        if self._risk_analyzer is None:
            from app.ml.risk_analyzer import RiskAnalyzer
            self._risk_analyzer = RiskAnalyzer()
        return self._risk_analyzer

    @property
    def contract_parser(self):
        if self._contract_parser is None:
            from app.ml.contract_parser import ContractParser
            self._contract_parser = ContractParser()
        return self._contract_parser

    def _build_ui(self) -> None:
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
        
        # Content layout
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(28)
        layout.setAlignment(Qt.AlignTop)

        # Header
        header = PageHeader(
            title="Contract Risk Analyzer",
            subtitle="AI-powered analysis of 55+ dangerous contract clauses",
        )
        
        # Badge
        badge = QLabel("🛡️ 5 Core Risks")
        badge.setStyleSheet(
            f"background-color: rgba(130, 216, 172, 0.15); "
            f"color: {Colors.ACCENT_SUCCESS}; "
            f"border: 1px solid {Colors.ACCENT_SUCCESS}; "
            f"border-radius: 999px; padding: 6px 14px; "
            f"font-size: 12px; font-weight: 700;"
        )
        header.add_action(badge)
        layout.addWidget(header)

        # ─── Input Section ────────────────────────────────────────────────
        input_card = AnimatedCard()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(28, 24, 28, 24)
        input_layout.setSpacing(20)

        # Section title
        upload_title = QLabel("📄 Contract Upload")
        upload_title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        input_layout.addWidget(upload_title)

        # File upload row
        file_row = QHBoxLayout()
        file_row.setSpacing(16)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; font-size: 13px;"
        )
        file_row.addWidget(self.file_label, 1)

        upload_btn = AnimatedButton("📤 Upload PDF", accent=Colors.ACCENT_INFO)
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.clicked.connect(self._upload_pdf)
        upload_btn.setFixedHeight(42)
        file_row.addWidget(upload_btn)
        
        input_layout.addLayout(file_row)

        # Contract text
        text_label = QLabel("Or paste contract text:")
        text_label.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        input_layout.addWidget(text_label)
        
        self.contract_text = QTextEdit()
        self.contract_text.setPlaceholderText(
            "Paste your contract here...\n\n"
            "The analyzer will scan for:\n"
            "• Unlimited liability clauses\n"
            "• Extended payment terms (Net-60/90)\n"
            "• IP transfer before payment\n"
            "• Termination without compensation\n"
            "• Unlimited revision requirements"
        )
        self.contract_text.setMinimumHeight(160)
        input_layout.addWidget(self.contract_text)

        # Parameters section
        params_title = QLabel("⚙️ Project Details (Optional)")
        params_title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent; margin-top: 12px;"
        )
        input_layout.addWidget(params_title)

        params_grid = QGridLayout()
        params_grid.setSpacing(16)
        params_grid.setColumnStretch(1, 1)
        params_grid.setColumnStretch(3, 1)

        self.project_combo = QComboBox()
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0, 100000)
        self.rate_input.setPrefix("₹ ")
        self.rate_input.setValue(500)
        
        self.revisions_input = QSpinBox()
        self.revisions_input.setRange(0, 20)
        self.revisions_input.setValue(2)
        
        self.timeline_input = QSpinBox()
        self.timeline_input.setRange(1, 365)
        self.timeline_input.setValue(14)
        self.timeline_input.setSuffix(" days")
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Design", "Video", "Writing", "Music", "Development", "General"])

        params_grid.addWidget(QLabel("Project:"), 0, 0)
        params_grid.addWidget(self.project_combo, 0, 1)
        params_grid.addWidget(QLabel("Hourly Rate:"), 0, 2)
        params_grid.addWidget(self.rate_input, 0, 3)
        
        params_grid.addWidget(QLabel("Revision Rounds:"), 1, 0)
        params_grid.addWidget(self.revisions_input, 1, 1)
        params_grid.addWidget(QLabel("Timeline:"), 1, 2)
        params_grid.addWidget(self.timeline_input, 1, 3)
        
        params_grid.addWidget(QLabel("Project Type:"), 2, 0)
        params_grid.addWidget(self.type_combo, 2, 1, 1, 3)

        input_layout.addLayout(params_grid)

        # Analyze button
        analyze_btn = AnimatedButton("🔍 Analyze Contract Risk", accent=Colors.ACCENT_PRIMARY)
        analyze_btn.setCursor(Qt.PointingHandCursor)
        analyze_btn.clicked.connect(self._analyze)
        analyze_btn.setFixedHeight(48)
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Bold)
        analyze_btn.setFont(font)
        input_layout.addWidget(analyze_btn)

        layout.addWidget(input_card)

        # ─── Overall Risk Score ───────────────────────────────────────────
        self.overall_card = AnimatedCard()
        overall_layout = QVBoxLayout(self.overall_card)
        overall_layout.setContentsMargins(32, 28, 32, 28)
        overall_layout.setSpacing(16)

        overall_title = QLabel("📊 Overall Risk Assessment")
        overall_title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        overall_layout.addWidget(overall_title)

        # Big risk level display
        risk_display = QHBoxLayout()
        risk_display.setSpacing(24)
        
        # Left: Score circle
        score_container = QVBoxLayout()
        score_container.setAlignment(Qt.AlignCenter)
        
        self.score_circle = QLabel("—")
        self.score_circle.setAlignment(Qt.AlignCenter)
        self.score_circle.setFixedSize(100, 100)
        self.score_circle.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 4px solid {Colors.BORDER_SUBTLE}; "
            f"border-radius: 50px; "
            f"font-size: 32px; font-weight: 700; "
            f"color: {Colors.TEXT_PRIMARY};"
        )
        score_container.addWidget(self.score_circle)
        
        score_label = QLabel("Risk Score")
        score_label.setAlignment(Qt.AlignCenter)
        score_label.setStyleSheet(
            f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )
        score_container.addWidget(score_label)
        
        risk_display.addLayout(score_container)
        
        # Right: Level and recommendation
        level_container = QVBoxLayout()
        level_container.setAlignment(Qt.AlignLeft)
        level_container.setSpacing(8)
        
        self.risk_level_label = QLabel("Risk Level: Not Analyzed")
        self.risk_level_label.setStyleSheet(
            f"font-size: 24px; font-weight: 700; color: {Colors.TEXT_SECONDARY}; "
            f"background: transparent;"
        )
        level_container.addWidget(self.risk_level_label)
        
        self.recommendation_label = QLabel("Upload a contract to begin analysis")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet(
            f"font-size: 14px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )
        level_container.addWidget(self.recommendation_label)
        
        risk_display.addLayout(level_container, 1)
        overall_layout.addLayout(risk_display)

        # Progress bar
        self.overall_progress = GradientBar(
            value=0,
            max_value=150,
            color_start=Colors.ACCENT_SUCCESS,
            color_end=Colors.ACCENT_DANGER,
            height=12,
        )
        overall_layout.addWidget(self.overall_progress)

        layout.addWidget(self.overall_card)
        self.overall_card.hide()

        # ─── 5 Critical Risk Areas ───────────────────────────────────────
        criteria_title = QLabel("🎯 5 Critical Risk Areas")
        criteria_title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        layout.addWidget(criteria_title)
        self.criteria_title = criteria_title
        criteria_title.hide()

        # Grid of risk cards
        criteria_grid = QGridLayout()
        criteria_grid.setSpacing(24)
        
        # Define 5 critical areas
        criteria_defs = [
            ("indemnity", "⚖️", "Indemnity Clause", "Unlimited liability exposure"),
            ("payment_terms", "💰", "Payment Terms", "Extended payment delays"),
            ("ip_transfer", "🎨", "IP Transfer", "Loss of ownership rights"),
            ("termination", "🚫", "Termination", "Cancellation without payment"),
            ("revision_scope", "🔄", "Revision Scope", "Unlimited work requirements"),
        ]
        
        for idx, (key, icon, title, desc) in enumerate(criteria_defs):
            card = RiskCriteriaCard(title, icon, desc)
            self.risk_cards[key] = card
            row = idx // 2
            col = idx % 2
            criteria_grid.addWidget(card, row, col)
            card.hide()
        
        layout.addLayout(criteria_grid)

        # ─── Detailed Findings ────────────────────────────────────────────
        findings_title = QLabel("📋 Detailed Findings")
        findings_title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        layout.addWidget(findings_title)
        self.findings_title = findings_title
        findings_title.hide()

        self.findings_table = QTableWidget()
        self.findings_table.setColumnCount(3)
        self.findings_table.setHorizontalHeaderLabels(["Category", "Finding", "Score"])
        self.findings_table.horizontalHeader().setStretchLastSection(True)
        self.findings_table.verticalHeader().setVisible(False)
        self.findings_table.setShowGrid(False)
        self.findings_table.setAlternatingRowColors(True)
        self.findings_table.setMinimumHeight(200)
        layout.addWidget(self.findings_table)
        self.findings_table.hide()

        # Set scroll area
        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

    def refresh(self) -> None:
        try:
            self.project_combo.clear()
            for p in self.project_repo.get_all():
                self.project_combo.addItem(p["name"], p["id"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load projects: {e}")

    def _upload_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Contract PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        filename = path.replace("\\", "/").split("/")[-1]
        self.file_label.setText(f"✅ {filename}")
        self.file_label.setStyleSheet(
            f"color: {Colors.ACCENT_SUCCESS}; background: transparent; font-size: 13px; font-weight: 600;"
        )
        try:
            text = self.contract_parser.extract_text(path)
            self.contract_text.setPlainText(text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not read PDF: {e}")

    def _analyze(self) -> None:
        if not self.contract_text.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Missing Contract",
                "Please paste contract text or upload a PDF before analyzing.",
            )
            return

        # Show results sections
        self.overall_card.show()
        self.criteria_title.show()
        for card in self.risk_cards.values():
            card.show()
        self.findings_title.show()
        self.findings_table.show()

        try:
            # Run full analysis
            result = self.risk_analyzer.full_analysis(
                hourly_rate=self.rate_input.value(),
                revisions=self.revisions_input.value(),
                timeline_days=self.timeline_input.value(),
                project_type=self.type_combo.currentText(),
                contract_text=self.contract_text.toPlainText(),
            )
            
            # Run critical clause analysis
            critical = self.risk_analyzer.analyze_critical_clauses(
                self.contract_text.toPlainText()
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Analysis Failed", f"Error: {e}")
            return

        # Update overall score
        total_score = result["total_score"]
        level = result["risk_level"]
        
        self.score_circle.setText(str(total_score))
        
        level_colors = {
            "LOW": Colors.ACCENT_SUCCESS,
            "MEDIUM": Colors.ACCENT_WARNING,
            "HIGH": Colors.ACCENT_DANGER,
            "CRITICAL": Colors.ACCENT_DANGER,
        }
        color = level_colors.get(level, Colors.TEXT_SECONDARY)
        
        self.score_circle.setStyleSheet(
            f"background-color: {color}; "
            f"border: 4px solid {color}; "
            f"border-radius: 50px; "
            f"font-size: 32px; font-weight: 700; "
            f"color: #FFFFFF;"
        )
        
        self.risk_level_label.setText(f"Risk Level: {level}")
        self.risk_level_label.setStyleSheet(
            f"font-size: 24px; font-weight: 700; color: {color}; background: transparent;"
        )
        
        # Recommendation
        recommendations = {
            "LOW": "✅ Acceptable risk - proceed with standard caution",
            "MEDIUM": "⚠️ Review carefully and negotiate weak points",
            "HIGH": "🚨 Serious concerns - negotiate heavily or walk away",
            "CRITICAL": "❌ DO NOT SIGN - extremely dangerous contract",
        }
        self.recommendation_label.setText(recommendations.get(level, ""))
        
        self.overall_progress.set_value(min(total_score, 150), animate=True)

        # Update 5 critical area cards
        for key, card in self.risk_cards.items():
            if key in critical:
                data = critical[key]
                card.set_result(
                    score=data["score"],
                    risk_level=data["risk"],
                    findings=data["findings"]
                )

        # Update findings table
        findings = result["findings"]
        self.findings_table.setRowCount(len(findings))
        for i, f in enumerate(findings):
            # Category
            cat_item = QTableWidgetItem(f["check"])
            cat_item.setFont(QFont("Inter", 11, QFont.Bold))
            self.findings_table.setItem(i, 0, cat_item)
            
            # Finding
            self.findings_table.setItem(i, 1, QTableWidgetItem(f["result"]))

            # Score
            score_item = QTableWidgetItem(str(f["score"]))
            score_item.setFont(QFont("Inter", 11, QFont.Bold))
            if f["score"] >= 25:
                score_item.setForeground(QColor(Colors.ACCENT_DANGER))
            elif f["score"] >= 15:
                score_item.setForeground(QColor(Colors.ACCENT_WARNING))
            elif f["score"] >= 8:
                score_item.setForeground(QColor(Colors.ACCENT_INFO))
            else:
                score_item.setForeground(QColor(Colors.ACCENT_SUCCESS))
            self.findings_table.setItem(i, 2, score_item)

        # Save to database
        project_id = self.project_combo.currentData()
        if project_id:
            try:
                import json
                self.contract_repo.add(
                    project_id=project_id,
                    contract_text=self.contract_text.toPlainText()[:5000],
                    hourly_rate=self.rate_input.value(),
                    revision_rounds=self.revisions_input.value(),
                    timeline_days=self.timeline_input.value(),
                    risk_score=result["total_score"],
                    risk_level=level,
                    findings=json.dumps(findings),
                )
            except Exception as e:
                pass  # Silent fail for save
