"""Contracts page — Studio Graphite redesign."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
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


class ContractsPage(QWidget):
    """Contract analysis with PDF upload and risk scoring."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.contract_repo = ContractRepository(db)
        self._risk_analyzer = None
        self._contract_parser = None

        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
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
        
        # Content layout - standardized spacing
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(28)
        layout.setAlignment(Qt.AlignTop)

        header = PageHeader(
            title="Contract Risk Analyzer",
            subtitle="Upload a contract PDF or paste text — get a risk score plus flagged clauses",
        )
        layout.addWidget(header)

        # ─── Inputs card ─────────────────────────────────────────────────
        upload_card = AnimatedCard()
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(24, 22, 24, 22)
        upload_layout.setSpacing(16)

        # File row
        file_row = QHBoxLayout()
        self.file_label = QLabel("📄  No file selected")
        self.file_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; font-size: 13px;"
        )
        file_row.addWidget(self.file_label, 1)

        upload_btn = AnimatedButton("Upload PDF", accent=Colors.ACCENT_INFO)
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.clicked.connect(self._upload_pdf)
        file_row.addWidget(upload_btn)
        upload_layout.addLayout(file_row)

        # Parameters
        params_layout = QFormLayout()
        params_layout.setSpacing(12)

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

        params_layout.addRow("Project", self.project_combo)
        params_layout.addRow("Hourly Rate", self.rate_input)
        params_layout.addRow("Revision Rounds", self.revisions_input)
        params_layout.addRow("Timeline", self.timeline_input)
        params_layout.addRow("Project Type", self.type_combo)
        upload_layout.addLayout(params_layout)

        # Contract text
        self.contract_text = QTextEdit()
        self.contract_text.setPlaceholderText("Paste contract text here, or upload a PDF above...")
        self.contract_text.setMaximumHeight(140)
        upload_layout.addWidget(self.contract_text)

        # Analyze button (full width)
        analyze_btn = AnimatedButton("🔍  Analyze Risk", accent=Colors.ACCENT_PRIMARY)
        analyze_btn.setCursor(Qt.PointingHandCursor)
        analyze_btn.clicked.connect(self._analyze)
        upload_layout.addWidget(analyze_btn)

        layout.addWidget(upload_card)

        # ─── Results card ────────────────────────────────────────────────
        results_card = AnimatedCard()
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(24, 22, 24, 22)
        results_layout.setSpacing(16)

        results_header = QLabel("Analysis Results")
        results_header.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 16px; font-weight: 700;"
        )
        results_layout.addWidget(results_header)

        risk_row = QHBoxLayout()
        self.risk_label = QLabel("Risk Level: —")
        self.risk_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; "
            f"font-size: 18px; font-weight: 700;"
        )
        risk_row.addWidget(self.risk_label)
        risk_row.addStretch()

        self.score_label = QLabel("Score: 0/100")
        self.score_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; font-size: 14px;"
        )
        risk_row.addWidget(self.score_label)
        results_layout.addLayout(risk_row)

        self.risk_bar = GradientBar(
            value=0,
            max_value=100,
            color_start=Colors.ACCENT_SUCCESS,
            color_end=Colors.ACCENT_DANGER,
            height=10,
        )
        results_layout.addWidget(self.risk_bar)

        self.findings_table = QTableWidget()
        self.findings_table.setColumnCount(3)
        self.findings_table.setHorizontalHeaderLabels(["Check", "Finding", "Score"])
        self.findings_table.horizontalHeader().setStretchLastSection(True)
        self.findings_table.verticalHeader().setVisible(False)
        self.findings_table.setShowGrid(False)
        self.findings_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.findings_table)

        layout.addWidget(results_card)

        # Set scroll area widget and add to page
        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

    # ------------------------------------------------------------------
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
        self.file_label.setText(f"📄  {filename}")
        self.file_label.setStyleSheet(
            f"color: {Colors.ACCENT_SUCCESS}; background: transparent; font-size: 13px;"
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
                "Missing Text",
                "Please paste contract text or upload a PDF before analyzing.",
            )
            return

        try:
            result = self.risk_analyzer.full_analysis(
                hourly_rate=self.rate_input.value(),
                revisions=self.revisions_input.value(),
                timeline_days=self.timeline_input.value(),
                project_type=self.type_combo.currentText(),
                contract_text=self.contract_text.toPlainText(),
            )
        except Exception as e:
            QMessageBox.critical(self, "Analysis Failed", f"Error: {e}")
            return

        level = result["risk_level"]
        level_colors = {
            "LOW": Colors.ACCENT_SUCCESS,
            "MEDIUM": Colors.ACCENT_WARNING,
            "HIGH": Colors.ACCENT_DANGER,
        }
        color = level_colors.get(level, Colors.TEXT_SECONDARY)

        self.risk_label.setText(f"Risk Level: {level}")
        self.risk_label.setStyleSheet(
            f"color: {color}; background: transparent; "
            f"font-size: 18px; font-weight: 700;"
        )

        score = min(result["total_score"], 100)
        self.score_label.setText(f"Score: {score}/100")
        self.risk_bar.set_value(score, animate=True)

        findings = result["findings"]
        self.findings_table.setRowCount(len(findings))
        for i, f in enumerate(findings):
            self.findings_table.setItem(i, 0, QTableWidgetItem(f["check"]))
            self.findings_table.setItem(i, 1, QTableWidgetItem(f["result"]))

            score_item = QTableWidgetItem(str(f["score"]))
            if f["score"] >= 15:
                score_item.setForeground(QColor(Colors.ACCENT_DANGER))
            elif f["score"] >= 8:
                score_item.setForeground(QColor(Colors.ACCENT_WARNING))
            else:
                score_item.setForeground(QColor(Colors.ACCENT_SUCCESS))
            self.findings_table.setItem(i, 2, score_item)

        # Save
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
                QMessageBox.warning(
                    self, "Save Failed", f"Analysis succeeded but could not save: {e}"
                )
