"""
Aranabilir PDF (OCR)
======================
Taranmış PDF sayfalarını Tesseract ile okuyup görünmez bir metin
katmanı ekler: çıktı aynı görünür ama metin seçilebilir/aranabilir.

Zaten metin içeren (dijital) sayfalar OCR'dan geçirilmeden olduğu gibi
kopyalanır — hem hız hem de vektör içeriğin rasterleşmemesi için.
OCR'lanan sayfa, Tesseract'ın ürettiği tek sayfalık PDF'in orijinal
sayfa boyutuna `show_pdf_page` ile yerleştirilmesiyle oluşur; böylece
Tesseract'ın DPI'dan türettiği sayfa boyutu orijinalden sapmaz.

SRP : Yalnızca PDF'e OCR metin katmanı eklemekten sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import ConvertOutcome
from core.converters.ocr_engine import OcrEngine
from core.converters.pymupdf_tool_base import PyMuPdfToolConverter
from core.errors import NothingToConvertError, PasswordProtectedError
from core.interfaces.converter_interface import ConversionOptions
from core.user_texts import ENGINE_OCR, ENGINE_UNAVAILABLE, HINT_TESSERACT

_OCR_DPI = 300
# Bu kadar karakterden az metni olan sayfa "taranmış" sayılır (sayfa
# numarası/başlık gibi küçük dijital artıklar OCR'ı engellemesin diye).
_MIN_TEXT_CHARS = 20


class PdfOcrConverter(PyMuPdfToolConverter):
    output_suffix = "_aranabilir"

    def __init__(self):
        self._ocr = OcrEngine()

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "Aranabilir PDF"

    @property
    def is_available(self) -> bool:
        return super().is_available and self._ocr.is_available()

    @property
    def active_engine_name(self) -> str:
        return ENGINE_OCR if self.is_available else ENGINE_UNAVAILABLE

    @property
    def is_parallel_safe(self) -> bool:
        # Her sayfada dış Tesseract süreci başlatır; paralel toplu dönüşümde
        # CPU'yu boğar ve diğer OCR converter'larıyla tutarlı kalsın diye sıralı.
        return False

    @property
    def unavailable_hint(self) -> str:
        return HINT_TESSERACT

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        src = fitz.open(str(source_path))
        out = fitz.open()
        ocr_count = 0
        try:
            if src.needs_pass:
                raise PasswordProtectedError()
            for page in src:
                if len(page.get_text().strip()) >= _MIN_TEXT_CHARS:
                    out.insert_pdf(src, from_page=page.number, to_page=page.number)
                    continue
                ocr_doc = fitz.open("pdf", self._ocr.ocr_page_to_pdf(page, dpi=_OCR_DPI))
                try:
                    target = out.new_page(width=page.rect.width, height=page.rect.height)
                    target.show_pdf_page(target.rect, ocr_doc, 0)
                finally:
                    ocr_doc.close()
                ocr_count += 1

            if ocr_count == 0:
                raise NothingToConvertError("PDF zaten aranabilir metin içeriyor; işlem gerekmedi.")
            out.save(str(output_path), garbage=3, deflate=True)
            return ConvertOutcome(output_path=output_path, page_count=src.page_count)
        finally:
            out.close()
            src.close()
