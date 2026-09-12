"""
PDF Bölme
===========
PyMuPDF (fitz) ile bir PDF'in her sayfasını ayrı bir PDF dosyasına
böler. `PdfToJpgConverter`'ın çok-sayfa-ayrı-dosya deseniyle aynı
mantık — bu, mevcut "1 girdi → N çıktı" modeline (BaseConverter +
ConvertOutcome) zaten oturuyor, `IMergeConverter` gerekmez.

Sayfa ARALIĞI seçimi (örn. "1-5") kapsam dışı — her sayfa ayrı dosya.

SRP : Yalnızca PDF bölmeden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions


class PdfSplitConverter(BaseConverter):
    """
    PDF → PDF (bölünmüş) dönüştürücü.
    Kaynak ve hedef uzantı aynı olduğu için `get_output_path()` override
    edilir — tek sayfalı bir PDF'te bile kaynağın üzerine yazma riski
    olmasın diye her zaman `_sayfa1.pdf` soneki eklenir.
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
        return "PDF Böl"

    def get_output_path(self, source_path: Path, options: ConversionOptions) -> Path:
        out_dir = options.output_dir or source_path.parent
        return out_dir / f"{source_path.stem}_sayfa1.pdf"

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
            first_output = output_path
            for i in range(page_count):
                page_output = output_path.with_name(f"{source_path.stem}_sayfa{i + 1}.pdf")
                page_doc = fitz.open()
                try:
                    page_doc.insert_pdf(doc, from_page=i, to_page=i)
                    page_doc.save(str(page_output))
                finally:
                    page_doc.close()
                if i == 0:
                    first_output = page_output
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

    @property
    def is_parallel_safe(self) -> bool:
        # Yalnızca PyMuPDF kullanır — dış süreç/paylaşımlı durum yok.
        return True
