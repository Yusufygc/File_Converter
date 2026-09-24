"""
PDF Bölme
===========
PyMuPDF (fitz) ile bir PDF'in sayfalarını ayrı PDF dosyalarına böler.
`PdfToJpgConverter`'ın çok-sayfa-ayrı-dosya deseniyle aynı mantık — bu,
mevcut "1 girdi → N çıktı" modeline (BaseConverter + ConvertOutcome)
zaten oturuyor, `IMergeConverter` gerekmez.

`options.page_range` boşsa tüm sayfalar tek tek ayrı dosyalara bölünür
(varsayılan, geriye dönük uyumlu — her sayfa kendi PDF'i). Doluysa
(örn. "1-3,5,7-9") — `IPageRangeSelectable.parse_page_range()` —
belirtilen sayfalar **TEK bir PDF'te** (verilen sırayla) birleştirilerek
çıkarılır; kullanıcı bir aralık verdiğinde "bu aralığı tek parça olarak
al" bekliyor, aralık içindeki her sayfayı ayrıca bölmek değil.

SRP : Yalnızca PDF bölmeden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.page_range_interface import IPageRangeSelectable


class PdfSplitConverter(BaseConverter, IPageRangeSelectable):
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

    def parse_page_range(self, page_range: str, page_count: int) -> List[int]:
        pages: List[int] = []
        seen = set()
        for part in page_range.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start_str, _, end_str = part.partition("-")
                try:
                    start, end = int(start_str.strip()), int(end_str.strip())
                except ValueError:
                    raise ValueError(f"Geçersiz sayfa aralığı: '{part}'") from None
            else:
                try:
                    start = end = int(part)
                except ValueError:
                    raise ValueError(f"Geçersiz sayfa numarası: '{part}'") from None

            if start < 1 or end < start or end > page_count:
                raise ValueError(
                    f"Geçersiz sayfa aralığı: '{part}' (belge {page_count} sayfa içeriyor)"
                )

            for page_num in range(start, end + 1):
                if page_num not in seen:
                    seen.add(page_num)
                    pages.append(page_num)

        if not pages:
            raise ValueError("Sayfa aralığı boş.")
        return pages

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

            if options.page_range:
                # Aralık verildiğinde seçili sayfalar TEK bir PDF'te birleştirilir.
                pages = self.parse_page_range(options.page_range, page_count)
                range_output = output_path.with_name(
                    f"{source_path.stem}_sayfa{'-'.join(str(p) for p in pages)}.pdf"
                )
                range_doc = fitz.open()
                try:
                    for page_num in pages:
                        range_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
                    range_doc.save(str(range_output))
                finally:
                    range_doc.close()
                return ConvertOutcome(output_path=range_output, page_count=len(pages))

            # Aralık verilmediyse her sayfa kendi ayrı dosyasına bölünür.
            pages = list(range(1, page_count + 1))
            first_output = output_path
            for idx, page_num in enumerate(pages):
                page_output = output_path.with_name(f"{source_path.stem}_sayfa{page_num}.pdf")
                page_doc = fitz.open()
                try:
                    page_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
                    page_doc.save(str(page_output))
                finally:
                    page_doc.close()
                if idx == 0:
                    first_output = page_output
        finally:
            doc.close()

        return ConvertOutcome(output_path=first_output, page_count=len(pages))

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
