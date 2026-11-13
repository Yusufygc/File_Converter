"""
PDF'ten Gömülü Görselleri Çıkarma
===================================
`PdfToJpgConverter` sayfayı render eder; bu converter ise PDF'e gömülü
orijinal görsel akışlarını yeniden kodlamadan, kendi formatında
(jpg/png/jpx...) diske yazar — kalite kaybı yok.

Aynı görsel (aynı xref) birden fazla sayfada kullanılsa da bir kez
yazılır. Hedef uzantı `.png` yalnızca nominaldir (registry anahtarı ve
UI rozeti için); gerçek dosya uzantısı görselin kendi formatıdır.

SRP : Yalnızca gömülü görsel çıkarmadan sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import ConvertOutcome
from core.converters.pymupdf_tool_base import PyMuPdfToolConverter
from core.errors import NothingToConvertError
from core.interfaces.converter_interface import ConversionOptions


class PdfExtractImagesConverter(PyMuPdfToolConverter):

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".png"

    @property
    def display_name(self) -> str:
        return "PDF Görsel Çıkar"

    def get_output_path(self, source_path: Path, options: ConversionOptions) -> Path:
        out_dir = options.output_dir or source_path.parent
        return out_dir / f"{source_path.stem}_gorsel1.png"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        doc = fitz.open(str(source_path))
        written = []
        try:
            seen = set()
            for page in doc:
                for img in page.get_images(full=True):
                    xref = img[0]
                    if xref in seen:
                        continue
                    seen.add(xref)
                    data = doc.extract_image(xref)
                    if not data or not data.get("image"):
                        continue
                    ext = data.get("ext", "png")
                    target = output_path.with_name(
                        f"{source_path.stem}_gorsel{len(written) + 1}.{ext}"
                    )
                    target.write_bytes(data["image"])
                    written.append(target)
        finally:
            doc.close()

        if not written:
            raise NothingToConvertError("PDF'te gömülü görsel bulunamadı.")
        return ConvertOutcome(output_path=written[0], page_count=len(written))
