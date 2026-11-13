"""
PDF Sayfa Numarası Ekleme
===========================
PyMuPDF ile her sayfaya seçilen köşede numara metni yazar.

Konum, sayfanın **görünen** (döndürülmüş) yüzeyine göre hesaplanır ve
`derotation_matrix` ile PDF'in döndürülmemiş koordinatlarına çevrilir;
aksi halde `/Rotate` değeri olan sayfalarda numara yanlış kenara ve yan
yatmış olarak düşerdi.

SRP : Yalnızca sayfa numarası eklemeden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import ConvertOutcome
from core.converters.pymupdf_tool_base import PyMuPdfToolConverter
from core.errors import InvalidOptionError
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.option_schema_interface import IOptionsProvider, OptionSpec

_MARGIN = 24
_BOX_WIDTH = 160
_FONT_SIZE = 10

# konum -> (dikey: top/bottom, yatay hizalama: 0 sol, 1 orta, 2 sağ)
_POSITIONS = {
    "bottom-center": ("bottom", 1),
    "bottom-right": ("bottom", 2),
    "bottom-left": ("bottom", 0),
    "top-center": ("top", 1),
    "top-right": ("top", 2),
    "top-left": ("top", 0),
}


class PdfPageNumbersConverter(PyMuPdfToolConverter, IOptionsProvider):
    output_suffix = "_numarali"

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PDF Sayfa Numarası"

    @property
    def option_specs(self) -> List[OptionSpec]:
        return [
            OptionSpec(
                key="position",
                label="Konum",
                kind="choice",
                default="bottom-center",
                choices=[
                    ("bottom-center", "Alt orta"),
                    ("bottom-right", "Alt sağ"),
                    ("bottom-left", "Alt sol"),
                    ("top-center", "Üst orta"),
                    ("top-right", "Üst sağ"),
                    ("top-left", "Üst sol"),
                ],
            ),
            OptionSpec(
                key="format",
                label="Biçim",
                kind="choice",
                default="n",
                choices=[("n", "1"), ("n_of_total", "1 / N"), ("page_n", "Sayfa 1")],
            ),
            OptionSpec(key="start", label="Başlangıç", kind="int", default=1, minimum=1, maximum=9999),
        ]

    @staticmethod
    def _label(fmt: str, number: int, total: int) -> str:
        if fmt == "n_of_total":
            return f"{number} / {total}"
        if fmt == "page_n":
            return f"Sayfa {number}"
        return str(number)

    @staticmethod
    def _visual_box(width: float, height: float, position: str):
        import fitz

        vertical, align = _POSITIONS[position]
        if align == 0:
            x0 = _MARGIN
        elif align == 2:
            x0 = width - _MARGIN - _BOX_WIDTH
        else:
            x0 = (width - _BOX_WIDTH) / 2
        box_h = _FONT_SIZE * 2
        y0 = _MARGIN if vertical == "top" else height - _MARGIN - box_h
        return fitz.Rect(x0, y0, x0 + _BOX_WIDTH, y0 + box_h), align

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        position = options.get_extra("position", "bottom-center")
        if position not in _POSITIONS:
            raise InvalidOptionError(f"Bilinmeyen konum: {position}")
        fmt = options.get_extra("format", "n")
        start = int(options.get_extra("start", 1))

        doc = fitz.open(str(source_path))
        try:
            total_last = start + doc.page_count - 1
            for idx, page in enumerate(doc):
                visual = page.rect  # döndürülmüş görünen boyut
                box, align = self._visual_box(visual.width, visual.height, position)
                box = box * page.derotation_matrix
                box.normalize()
                rc = page.insert_textbox(
                    box,
                    self._label(fmt, start + idx, total_last),
                    fontsize=_FONT_SIZE,
                    fontname="helv",
                    color=(0.2, 0.2, 0.2),
                    align=align,
                    rotate=page.rotation,
                )
                if rc < 0:
                    raise InvalidOptionError(
                        f"Sayfa {idx + 1}: numara sayfaya sığmadı. Daha kısa bir biçim seçin."
                    )
            doc.save(str(output_path), garbage=3, deflate=True)
            return ConvertOutcome(output_path=output_path, page_count=doc.page_count)
        finally:
            doc.close()
