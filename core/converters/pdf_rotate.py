"""
PDF Döndürme
==============
PyMuPDF ile sayfaların görüntülenme açısını değiştirir. İçerik yeniden
render edilmez; yalnızca sayfanın `/Rotate` değeri güncellenir, bu yüzden
kayıpsız ve hızlıdır. Sayfa aralığı boşsa tüm sayfalar döndürülür.

SRP : Yalnızca PDF sayfa döndürmeden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import ConvertOutcome
from core.converters.page_range import parse_page_range
from core.converters.pymupdf_tool_base import PyMuPdfToolConverter
from core.errors import InvalidOptionError
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.option_schema_interface import IOptionsProvider, OptionSpec
from core.interfaces.page_range_interface import IPageRangeSelectable


class PdfRotateConverter(PyMuPdfToolConverter, IPageRangeSelectable, IOptionsProvider):
    output_suffix = "_dondurulmus"

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PDF Döndür"

    @property
    def option_specs(self) -> List[OptionSpec]:
        return [
            OptionSpec(
                key="angle",
                label="Açı",
                kind="choice",
                default=90,
                choices=[(90, "90° saat yönü"), (180, "180°"), (270, "90° saat tersi")],
            )
        ]

    def parse_page_range(self, page_range: str, page_count: int) -> List[int]:
        return parse_page_range(page_range, page_count)

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        angle = int(options.get_extra("angle", 90))
        if angle % 90 != 0:
            raise InvalidOptionError(f"Açı 90'ın katı olmalıdır: {angle}")

        doc = fitz.open(str(source_path))
        try:
            if options.page_range:
                pages = self.parse_page_range(options.page_range, doc.page_count)
            else:
                pages = list(range(1, doc.page_count + 1))
            for page_num in pages:
                page = doc[page_num - 1]
                page.set_rotation((page.rotation + angle) % 360)
            doc.save(str(output_path), garbage=3, deflate=True)
            return ConvertOutcome(output_path=output_path, page_count=len(pages))
        finally:
            doc.close()
