"""
PDF → TXT Converter
=====================
PyMuPDF (fitz) ile PDF'in metnini çıkarır. LibreOffice bile gerekmez —
`fitz.Page.get_text()` yeterli. Tüm sayfalar TEK bir `.txt` dosyasında
birleştirilir (görsel dönüşümlerin sayfa-başına-dosya deseninden farklı
olarak — metin çıktısında tek dosya çok daha kullanışlı).

SRP : Yalnızca PDF → TXT metin çıkarmadan sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions


class PdfToTxtConverter(BaseConverter):
    """
    PDF → TXT dönüştürücü. Tablo/başlık gibi yapısal öğeler korunmaz,
    yalnızca düz metin çıkarılır. Sayfalar `--- Sayfa N ---` ayracıyla birleşir.
    """

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
