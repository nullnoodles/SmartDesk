"""Receipt OCR — extract text and amount from a scanned receipt image.

Uses Tesseract via pytesseract. If Tesseract is not installed on the host,
the call returns a friendly error in the result dict instead of crashing.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


# Heuristic patterns to find a total / amount line on receipts
_TOTAL_PATTERNS = [
    re.compile(r"(?i)\btotal[^0-9₹\$]{0,15}([₹$]?\s*[\d,]+(?:\.\d{1,2})?)"),
    re.compile(r"(?i)\bgrand\s*total[^0-9₹\$]{0,15}([₹$]?\s*[\d,]+(?:\.\d{1,2})?)"),
    re.compile(r"(?i)\bamount\s*paid[^0-9₹\$]{0,15}([₹$]?\s*[\d,]+(?:\.\d{1,2})?)"),
    re.compile(r"(?i)\bnet\s*payable[^0-9₹\$]{0,15}([₹$]?\s*[\d,]+(?:\.\d{1,2})?)"),
]

_DATE_PATTERN = re.compile(
    r"\b("
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"           # 12/05/2026, 12-5-26
    r"|\d{4}[/-]\d{1,2}[/-]\d{1,2}"            # 2026-05-12
    r"|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}"      # 12 May 2026
    r")\b"
)


class ReceiptOCR:
    """Extracts text and a likely total amount from a receipt image."""

    def is_available(self) -> bool:
        """Quick check whether Tesseract is installed and reachable."""
        try:
            import pytesseract  # noqa: F401
            from PIL import Image  # noqa: F401
            import shutil

            # pytesseract calls the `tesseract` binary internally
            return shutil.which("tesseract") is not None
        except Exception:
            return False

    def extract(self, image_path: Path | str) -> dict[str, Any]:
        """Run OCR on an image. Returns dict with text/amount/date or error."""
        path = Path(image_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {path}"}

        try:
            import pytesseract
            from PIL import Image
        except ImportError as e:
            return {
                "success": False,
                "error": f"Required library not installed: {e}",
            }

        try:
            img = Image.open(path)
            text = pytesseract.image_to_string(img)
        except pytesseract.TesseractNotFoundError:
            return {
                "success": False,
                "error": (
                    "Tesseract OCR is not installed. "
                    "Install from https://github.com/UB-Mannheim/tesseract/wiki and ensure "
                    "tesseract.exe is on your PATH."
                ),
            }
        except Exception as e:
            return {"success": False, "error": f"OCR failed: {e}"}

        return {
            "success": True,
            "text": text.strip(),
            "amount": self._guess_amount(text),
            "date": self._guess_date(text),
        }

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------
    def _guess_amount(self, text: str) -> float | None:
        for pattern in _TOTAL_PATTERNS:
            match = pattern.search(text)
            if match:
                raw = match.group(1)
                cleaned = re.sub(r"[^\d.]", "", raw)
                try:
                    return float(cleaned) if cleaned else None
                except ValueError:
                    continue
        return None

    def _guess_date(self, text: str) -> str | None:
        match = _DATE_PATTERN.search(text)
        return match.group(1) if match else None
