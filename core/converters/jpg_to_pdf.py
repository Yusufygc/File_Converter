"""
JPG → PDF Converter
====================
PyMuPDF (fitz) ile tek bir görseli tek sayfalı PDF'e sarar.
Tek motor var (Strategy deseni gerekmiyor).

Ayrıca `IMergeConverter` capability'sini de destekler (`MergeCapableConverter`
üzerinden): birden fazla görsel tek bir çok sayfalı PDF'e birleştirilebilir
— UI'da bu, "Tüm dosyaları TEK çıktıda birleştir" onay kutusuyla sunulur.

SRP : Yalnızca JPG → PDF dönüşümünden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import ConvertOutcome, MergeCapableConverter
from core.interfaces.converter_interface import ConversionOptions


class JpgToPdfConverter(MergeCapableConverter):
    """
    JPG → PDF dönüştürücü. Hem .jpg hem .jpeg kabul eder.
    Tekil modda her görsel kendi tek sayfalı PDF'ine dönüştürülür;
    birleştirme modunda tüm görseller tek çok sayfalı PDF'e sarılır.
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

    def _do_convert_many(
        self,
        source_paths: List[Path],
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        doc = fitz.open()
        try:
            for p in source_paths:
                img_doc = fitz.open(str(p))
                try:
                    pdf_bytes = img_doc.convert_to_pdf()
                finally:
                    img_doc.close()

                page_pdf = fitz.open("pdf", pdf_bytes)
                try:
                    doc.insert_pdf(page_pdf)
                finally:
                    page_pdf.close()

            doc.save(str(output_path))
        finally:
            doc.close()

        return ConvertOutcome(page_count=len(source_paths))

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

    @property
    def is_parallel_safe(self) -> bool:
        # Yalnızca PyMuPDF kullanır — dış süreç/paylaşımlı durum yok.
        return True
