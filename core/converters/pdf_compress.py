"""
PDF Sıkıştırma
================
PyMuPDF'in yerleşik akış/nesne temizleme bayraklarıyla PDF dosya
boyutunu küçültür. Sayfaları görsele çevirmez — metin ve vektör
grafikler kayıpsız kalır, yalnızca gereksiz nesneler ve sıkıştırılmamış
akışlar yeniden düzenlenir.

SRP : Yalnızca PDF boyut küçültmeden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions


class PdfCompressConverter(BaseConverter):
    """
    PDF → PDF (sıkıştırılmış) dönüştürücü.
    Kaynak ve hedef uzantı aynı olduğu için `get_output_path()` override
    edilir — aksi halde kullanıcı ayrı bir çıktı klasörü seçmediğinde
    (varsayılan davranış) orijinal dosyanın üzerine yazılırdı.
    """

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PDF Sıkıştır"

    def get_output_path(self, source_path: Path, options: ConversionOptions) -> Path:
        out_dir = options.output_dir or source_path.parent
        return out_dir / f"{source_path.stem}_sikistirilmis.pdf"

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
            doc.save(
                str(output_path),
                garbage=4,
                deflate=True,
                deflate_images=True,
                deflate_fonts=True,
                clean=True,
            )
        finally:
            doc.close()

        return ConvertOutcome(page_count=page_count)

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
