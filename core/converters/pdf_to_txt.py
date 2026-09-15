"""
PDF → TXT Converter
=====================
PyMuPDF (fitz) ile PDF'in metnini çıkarır.
Taranmış PDF'lerde OCR motoru (Tesseract) mevcutsa otomatik OCR metin çıkarımı yapar.
Tüm sayfalar TEK bir `.txt` dosyasında `--- Sayfa N ---` ayracıyla birleştirilir.

SRP : Yalnızca PDF → TXT metin çıkarmadan sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.converters.ocr_engine import OcrEngine
from core.interfaces.converter_interface import ConversionOptions
from core.utils.pdf_inspector import is_scanned_pdf


class PdfToTxtConverter(BaseConverter):
    """
    PDF → TXT dönüştürücü.
    Dijital PDF'lerde PyMuPDF ile anında metin çıkarır.
    Taranmış PDF'lerde OCR desteğiyle metni okur.
    """

    def __init__(self):
        self._ocr = OcrEngine()

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".txt"

    @property
    def display_name(self) -> str:
        return "PDF → TXT"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        is_scanned = is_scanned_pdf(source_path)

        # Taranmış PDF ve OCR mevcutsa → OCR ile metin çıkar
        if is_scanned and self._ocr.is_available():
            text = self._ocr.ocr_pdf_to_text(source_path)
            output_path.write_text(text, encoding="utf-8")
            doc = fitz.open(str(source_path))
            try:
                page_count = doc.page_count
            finally:
                doc.close()
            return ConvertOutcome(page_count=page_count)

        # Standart dijital PDF metin çıkarımı
        doc = fitz.open(str(source_path))
        try:
            page_count = doc.page_count
            parts = []
            for i, page in enumerate(doc):
                if i > 0:
                    parts.append(f"\n--- Sayfa {i + 1} ---\n")
                parts.append(page.get_text())
            output_path.write_text("".join(parts), encoding="utf-8")
        finally:
            doc.close()

        return ConvertOutcome(page_count=page_count)

    @property
    def unavailable_hint(self) -> str:
        return (
            "Dönüşüm motoru bulunamadı.\n\n"
            "PyMuPDF (önerilen):\n"
            "  pip install pymupdf\n\n"
            "Taranmış PDF'ler için OCR (opsiyonel):\n"
            "  winget install UB-Mannheim.TesseractOCR"
        )

    # ------------------------------------------------------------------ #
    #  Public helpers                                                      #
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        try:
            import fitz  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def active_engine_name(self) -> str:
        if self._ocr.is_available():
            return "PyMuPDF + OCR"
        return "PyMuPDF" if self.is_available else "Yok"

    @property
    def is_parallel_safe(self) -> bool:
        return True
