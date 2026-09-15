"""
PDF Birleştirme
=================
PyMuPDF (fitz) ile birden fazla PDF'i tek bir dosyada birleştirir.
`IMergeConverter` capability'sini (`MergeCapableConverter` üzerinden)
destekler — UI'da "Tüm dosyaları TEK çıktıda birleştir" onay kutusuyla
sunulur. Tekil dosya modunda (`convert()`) "1 dosyayı birleştirmek"
dejenere ama tutarlı bir durumdur: dosyanın kendisinin bir kopyası
üretilir — aynı `_merge()` yardımcı metodu her iki modda da kullanılır.

SRP : Yalnızca PDF birleştirmeden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import ConvertOutcome, MergeCapableConverter
from core.interfaces.converter_interface import ConversionOptions


class PdfMergeConverter(MergeCapableConverter):
    """PDF → PDF (birleştirilmiş) dönüştürücü."""

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
        return "PDF Birleştir"

    def get_output_path(self, source_path: Path, options: ConversionOptions) -> Path:
        out_dir = options.output_dir or source_path.parent
        return out_dir / f"{source_path.stem}_birlesik.pdf"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        page_count = self._merge([source_path], output_path)
        return ConvertOutcome(page_count=page_count)

    def _do_convert_many(
        self,
        source_paths: List[Path],
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        page_count = self._merge(source_paths, output_path)
        return ConvertOutcome(page_count=page_count)

    @staticmethod
    def _merge(source_paths: List[Path], output_path: Path) -> int:
        """Verilen PDF'leri sırayla tek bir belgede birleştirir, sayfa sayısını döner."""
        import fitz

        doc = fitz.open()
        try:
            for p in source_paths:
                src = fitz.open(str(p))
                try:
                    doc.insert_pdf(src)
                finally:
                    src.close()
            doc.save(str(output_path))
            return doc.page_count
        finally:
            doc.close()

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
