"""
PDF → Markdown
================
`pymupdf4llm` ile PDF'i başlık, liste, tablo ve bağlantıları koruyarak
Markdown'a çevirir (not alma, dokümantasyon, LLM girdisi için).

`pymupdf4llm` PyMuPDF ekibinin paketidir; sürümü `PyMuPDF` ile birebir
eşleşecek şekilde sabitlenir (bkz. requirements.txt).

SRP : Yalnızca PDF→Markdown dönüşümünden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.converters.page_range import parse_page_range
from core.errors import NothingToConvertError, PasswordProtectedError
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.page_range_interface import IPageRangeSelectable
from core.user_texts import ENGINE_BUILTIN, ENGINE_UNAVAILABLE, HINT_BUILTIN_MISSING


class PdfToMarkdownConverter(BaseConverter, IPageRangeSelectable):

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".md"

    @property
    def display_name(self) -> str:
        return "PDF → Markdown"

    def parse_page_range(self, page_range: str, page_count: int) -> List[int]:
        return parse_page_range(page_range, page_count)

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz
        import pymupdf4llm

        doc = fitz.open(str(source_path))
        try:
            if doc.needs_pass:
                raise PasswordProtectedError()
            if options.page_range:
                pages = [p - 1 for p in self.parse_page_range(options.page_range, doc.page_count)]
            else:
                pages = list(range(doc.page_count))
            md_text = pymupdf4llm.to_markdown(doc, pages=pages, show_progress=False)
        finally:
            doc.close()

        if not md_text.strip():
            raise NothingToConvertError(
                "PDF'te metin bulunamadı. Taranmış bir belgeyse önce 'Aranabilir PDF' aracını kullanın."
            )
        output_path.write_text(md_text, encoding="utf-8")
        return ConvertOutcome(output_path=output_path, page_count=len(pages))

    @property
    def unavailable_hint(self) -> str:
        return HINT_BUILTIN_MISSING

    @property
    def is_available(self) -> bool:
        try:
            import fitz  # noqa: F401
            import pymupdf4llm  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def active_engine_name(self) -> str:
        return ENGINE_BUILTIN if self.is_available else ENGINE_UNAVAILABLE

    @property
    def is_parallel_safe(self) -> bool:
        return True
