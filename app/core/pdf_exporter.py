"""PDF invoice export using ReportLab."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.config import CURRENCY_SYMBOL, EXPORTS_DIR


class PDFExporter:
    """Generates professional A4 PDF invoices."""

    def export_invoice(self, invoice_data: dict, output_path: Path | None = None) -> Path:
        """
        Export an invoice dict to PDF.

        invoice_data keys: invoice_number, client_name, client_email,
                           project_name, amount, tax, total, date_issued, due_date
        """
        if output_path is None:
            output_path = EXPORTS_DIR / f"{invoice_data['invoice_number']}.pdf"

        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(Paragraph(f"<b>INVOICE — {invoice_data['invoice_number']}</b>", styles["Title"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Client info
        elements.append(Paragraph(f"Bill To: <b>{invoice_data['client_name']}</b>", styles["Normal"]))
        if invoice_data.get("client_email"):
            elements.append(Paragraph(f"Email: {invoice_data['client_email']}", styles["Normal"]))
        elements.append(Paragraph(
            f"Project: {invoice_data['project_name']} | Due: {invoice_data['due_date']}",
            styles["Normal"],
        ))
        elements.append(Spacer(1, 0.3 * inch))

        # Table
        data = [
            ["Description", f"Amount ({CURRENCY_SYMBOL})"],
            [invoice_data["project_name"], f"{CURRENCY_SYMBOL}{invoice_data['amount']:,.2f}"],
            ["GST (18%)", f"{CURRENCY_SYMBOL}{invoice_data['tax']:,.2f}"],
            ["TOTAL", f"{CURRENCY_SYMBOL}{invoice_data['total']:,.2f}"],
        ]
        table = Table(data, colWidths=[4 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ]))
        elements.append(table)

        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(
            f"Date Issued: {invoice_data['date_issued']}",
            styles["Normal"],
        ))

        doc.build(elements)
        return output_path
