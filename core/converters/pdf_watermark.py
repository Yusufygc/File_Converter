"""
PDF Filigran (Metin)
======================
PyMuPDF `TextWriter` ile her sayfanın ortasına yarı saydam, 45° eğik
metin filigranı basar.

`insert_text` yerine `TextWriter` kullanılır: `fill_opacity` + merkez
etrafında döndürme (`morph`) tek çağrıda yapılabiliyor. Gömülü "helv"
(Nimbus Sans) fontu Türkçe karakterleri (ş, ğ, İ, ı) içerir — base-14
WinAnsi kodlamalı `fontname="helv"` ise içermez, bu yüzden `fitz.Font`
nesnesi kullanılır.

SRP : Yalnızca metin filigranı eklemeden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import ConvertOutcome
from core.converters.pymupdf_tool_base import PyMuPdfToolConverter
from core.errors import InvalidOptionError
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.option_schema_interface import IOptionsProvider, OptionSpec


class PdfWatermarkConverter(PyMuPdfToolConverter, IOptionsProvider):
    output_suffix = "_filigranli"

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PDF Filigran"

    @property
    def option_specs(self) -> List[OptionSpec]:
        return [
            OptionSpec(key="text", label="Metin", kind="text", placeholder="örn: GİZLİ", required=True),
            OptionSpec(key="opacity", label="Opaklık %", kind="int", default=30, minimum=5, maximum=100),
            OptionSpec(key="font_size", label="Punto", kind="int", default=60, minimum=8, maximum=300),
        ]

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        text = str(options.get_extra("text", "")).strip()
        if not text:
            raise InvalidOptionError("Filigran metni boş olamaz.")
        opacity = max(5, min(100, int(options.get_extra("opacity", 30)))) / 100
        font_size = max(8, min(300, int(options.get_extra("font_size", 60))))
        font = fitz.Font("helv")

        doc = fitz.open(str(source_path))
        try:
            text_width = font.text_length(text, fontsize=font_size)
            for page in doc:
                # Döndürülmemiş koordinatlarda merkez; 45° eğim döndürülmüş
                # sayfalarda da köşegen kalır, ayrıca derotation gerekmez.
                center = (page.cropbox.tl + page.cropbox.br) / 2
                writer = fitz.TextWriter(page.rect)
                writer.append(
                    fitz.Point(center.x - text_width / 2, center.y + font_size / 3),
                    text,
                    font=font,
                    fontsize=font_size,
                )
                writer.write_text(
                    page,
                    color=(0.55, 0.55, 0.55),
                    opacity=opacity,
                    morph=(center, fitz.Matrix(-45)),
                    overlay=True,
                )
            doc.save(str(output_path), garbage=3, deflate=True)
            return ConvertOutcome(output_path=output_path, page_count=doc.page_count)
        finally:
            doc.close()
