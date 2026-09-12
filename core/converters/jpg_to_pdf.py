"""
JPG → PDF Converter
====================
PyMuPDF (fitz) ile tek bir görseli tek sayfalı PDF'e sarar.
Tek motor var (Strategy deseni gerekmiyor).

SRP : Yalnızca JPG → PDF dönüşümünden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions


class JpgToPdfConverter(BaseConverter):
    """
    JPG → PDF dönüştürücü. Hem .jpg hem .jpeg kabul eder.
    Her görsel tek sayfalı bir PDF'e dönüştürülür.
    """

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

    @property
    def source_extension(self) -> str:
        return ".jpg"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "JPG → PDF"

    @property
    def accepted_extensions(self) -> List[str]:
        return [".jpg", ".jpeg"]

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        img_doc = fitz.open(str(source_path))
        try:
            pdf_bytes = img_doc.convert_to_pdf()
        finally:
            img_doc.close()

        pdf_doc = fitz.open("pdf", pdf_bytes)
        try:
            pdf_doc.save(str(output_path))
        finally:
            pdf_doc.close()

        return ConvertOutcome(page_count=1)

    @property
    def unavailable_hint(self) -> str:
        return (
            "Dönüşüm motoru bulunamadı.\n\n"
            "PyMuPDF (önerilen):\n"
            "  pip install pymupdf"
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
        return "PyMuPDF" if self.is_available else "Yok"
