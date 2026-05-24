"""PDF invoice export using ReportLab.

Renders a professional A4 invoice with:
  - Sender (business) info from settings
  - Client/bill-to block
  - Line items table with GST
  - Optional UPI QR code for payment
  - Optional logo (PNG/JPG)
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.config import CURRENCY_SYMBOL, EXPORTS_DIR


class PDFExporter:
    """Generates professional A4 PDF invoices."""

    def export_invoice(
        self,
        invoice_data: dict,
        output_path: Path | None = None,
        business: Optional[dict] = None,
    ) -> Path:
        """
        Export an invoice dict to PDF.

        invoice_data keys: invoice_number, client_name, client_email,
                           project_name, amount, tax, total, date_issued, due_date

        business keys (optional): name, email, phone, address, gstin, logo_path,
                                  upi_id, upi_name
        """
        if output_path is None:
            output_path = EXPORTS_DIR / f"{invoice_data['invoice_number']}.pdf"

        business = business or {}

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
        )
        styles = getSampleStyleSheet()
        muted = ParagraphStyle(
            "muted",
            parent=styles["Normal"],
            textColor=colors.HexColor("#6b6d85"),
            fontSize=9,
        )
        emphasis = ParagraphStyle(
            "emphasis",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
        )

        elements: list = []

        # ─── Header: business block + invoice meta ────────────────────────
        elements.append(self._header(invoice_data, business, styles, emphasis, muted))
        elements.append(Spacer(1, 0.25 * inch))

        # ─── Bill To ──────────────────────────────────────────────────────
        elements.append(Paragraph("<b>BILL TO</b>", muted))
        elements.append(
            Paragraph(f"<b>{invoice_data['client_name']}</b>", emphasis)
        )
        if invoice_data.get("client_email"):
            elements.append(Paragraph(invoice_data["client_email"], styles["Normal"]))
        elements.append(Spacer(1, 0.18 * inch))

        # ─── Line items table ─────────────────────────────────────────────
        data = [
            ["Description", f"Amount ({CURRENCY_SYMBOL})"],
            [
                invoice_data["project_name"],
                f"{CURRENCY_SYMBOL}{invoice_data['amount']:,.2f}",
            ],
            ["GST (18%)", f"{CURRENCY_SYMBOL}{invoice_data['tax']:,.2f}"],
            ["TOTAL", f"{CURRENCY_SYMBOL}{invoice_data['total']:,.2f}"],
        ]
        table = Table(data, colWidths=[4.6 * inch, 2.0 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F0F4FA")),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.grey),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        # ─── Payment block: UPI QR if configured ──────────────────────────
        upi_block = self._upi_block(invoice_data, business, muted)
        if upi_block is not None:
            elements.append(upi_block)
            elements.append(Spacer(1, 0.25 * inch))

        # ─── Footer ───────────────────────────────────────────────────────
        elements.append(
            Paragraph(
                f"Date Issued: {invoice_data['date_issued']}    "
                f"Due Date: {invoice_data.get('due_date', '—')}",
                muted,
            )
        )
        if business.get("name"):
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(
                Paragraph(
                    f"Thank you for your business — {business['name']}",
                    muted,
                )
            )

        doc.build(elements)
        return output_path

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _header(self, invoice_data: dict, business: dict, styles, emphasis, muted) -> Table:
        # Left column: logo + business name + address
        left_cells = []

        logo_path = business.get("logo_path") or ""
        if logo_path and Path(logo_path).exists():
            try:
                left_cells.append(Image(logo_path, width=1.2 * inch, height=1.2 * inch))
                left_cells.append(Spacer(1, 0.05 * inch))
            except Exception:
                pass

        if business.get("name"):
            left_cells.append(Paragraph(f"<b>{business['name']}</b>", emphasis))
        else:
            left_cells.append(Paragraph("<b>SmartDesk</b>", emphasis))

        if business.get("address"):
            left_cells.append(Paragraph(business["address"].replace("\n", "<br/>"), muted))
        contact_bits = []
        if business.get("email"):
            contact_bits.append(business["email"])
        if business.get("phone"):
            contact_bits.append(business["phone"])
        if contact_bits:
            left_cells.append(Paragraph(" · ".join(contact_bits), muted))
        if business.get("gstin"):
            left_cells.append(Paragraph(f"GSTIN: {business['gstin']}", muted))

        # Right column: invoice meta
        right_cells = [
            Paragraph(
                f"<font size=18 color='#2E75B6'><b>INVOICE</b></font>",
                styles["Normal"],
            ),
            Spacer(1, 0.05 * inch),
            Paragraph(f"<b>{invoice_data['invoice_number']}</b>", emphasis),
            Spacer(1, 0.05 * inch),
            Paragraph(f"Date: {invoice_data['date_issued']}", muted),
            Paragraph(f"Due: {invoice_data.get('due_date', '—')}", muted),
        ]

        # Two-column table layout
        return Table(
            [[left_cells, right_cells]],
            colWidths=[4.0 * inch, 2.6 * inch],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            ),
        )

    def _upi_block(self, invoice_data: dict, business: dict, muted) -> Optional[Table]:
        upi_id = (business.get("upi_id") or "").strip()
        if not upi_id:
            return None

        try:
            from app.utils.upi_qr import generate_upi_qr

            qr_path = generate_upi_qr(
                upi_id=upi_id,
                payee_name=business.get("upi_name") or business.get("name") or "Payee",
                amount=float(invoice_data["total"]),
                note=f"Invoice {invoice_data['invoice_number']}",
                output_path=EXPORTS_DIR / f".qr-{invoice_data['invoice_number']}.png",
            )
        except Exception:
            return None

        info_cells = [
            Paragraph("<b>SCAN TO PAY VIA UPI</b>", muted),
            Spacer(1, 0.05 * inch),
            Paragraph(f"UPI ID: {upi_id}", muted),
            Paragraph(
                f"Amount: {CURRENCY_SYMBOL}{invoice_data['total']:,.2f}",
                muted,
            ),
        ]

        return Table(
            [[Image(str(qr_path), width=1.4 * inch, height=1.4 * inch), info_cells]],
            colWidths=[1.7 * inch, 4.9 * inch],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F8FB")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DAE5")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            ),
        )
