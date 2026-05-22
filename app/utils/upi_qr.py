"""UPI QR code generator for invoices.

WOW Feature: Generate UPI payment links and QR codes directly on invoices.
"""
from __future__ import annotations

from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def generate_upi_qr(
    upi_id: str,
    payee_name: str,
    amount: float,
    note: str = "Invoice Payment",
    output_path: Path | str | None = None,
) -> Path:
    """
    Generate a UPI QR code image.

    Args:
        upi_id: UPI ID (e.g., "name@upi")
        payee_name: Display name of payee
        amount: Amount in INR
        note: Transaction note
        output_path: Where to save the QR image

    Returns:
        Path to the generated QR code image.
    """
    # UPI deep link format
    upi_url = (
        f"upi://pay?pa={upi_id}"
        f"&pn={payee_name}"
        f"&am={amount:.2f}"
        f"&cu=INR"
        f"&tn={note}"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if output_path is None:
        from app.config import EXPORTS_DIR
        output_path = EXPORTS_DIR / "upi_qr.png"

    img.save(str(output_path))
    return Path(output_path)
