"""
PDF → JPG Converter
====================
PyMuPDF (fitz) ile PDF sayfalarını JPG'e rasterize eder.
Tek motor var (Strategy deseni gerekmiyor).

SRP : Yalnızca PDF → JPG dönüşümünden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions


class PdfToJpgConverter(BaseConverter):
    """
    PDF → JPG dönüştürücü.
    Çok sayfalı PDF'lerde her sayfa ayrı JPG dosyası olarak üretilir
    (ad_p1.jpg, ad_p2.jpg, ...). Tek sayfalı PDF'te ad.jpg üretilir.
    """

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".jpg"

    @property
    def display_name(self) -> str:
        return "PDF → JPG"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        doc = fitz.open(str(source_path))
        try:
            page_count = doc.page_count
            zoom = options.dpi / 72
            matrix = fitz.Matrix(zoom, zoom)

            first_output: Path = output_path
            for i, page in enumerate(doc):
                if page_count == 1:
                    page_output = output_path
                else:
                    page_output = output_path.with_name(
                        f"{output_path.stem}_p{i + 1}{output_path.suffix}"
                    )
                    if i == 0:
                        first_output = page_output

                pix = page.get_pixmap(matrix=matrix)
                pix.save(str(page_output), jpg_quality=options.quality)
        finally:
            doc.close()

        return ConvertOutcome(output_path=first_output, page_count=page_count)

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
