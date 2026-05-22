"""PDF contract parser — extracts text from uploaded contract PDFs.

WOW Feature: Upload PDF → extract text → feed to clause classifier → risk report.
"""
from __future__ import annotations

from pathlib import Path


class ContractParser:
    """Extracts and cleans text from PDF contract files."""

    def extract_text(self, pdf_path: str | Path) -> str:
        """Extract all text from a PDF file."""
        import pdfplumber

        text_parts = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def extract_pages(self, pdf_path: str | Path) -> list[str]:
        """Extract text page by page."""
        import pdfplumber

        pages = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)
        return pages
