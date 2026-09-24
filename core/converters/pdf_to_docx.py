"""
PDF → DOCX / ODT Converter
===========================
Akıllı Çok Kademeli Dönüşüm Mimarisi:
  1. Dijital PDF (Metin Katmanlı)  → `pdf2docx` (saf Python, 1-2s, tam layout koruma)
  2. Taranmış PDF (OCR Mevcut)      → `OcrEngine` (Tesseract OCR -> düzenlenebilir DOCX)
  3. Taranmış PDF (OCR Yok)         → `pdf2docx` / `ImageEmbed` (temiz, bozulmayan sayfa görüntüleri)
  4. Fallback                       → LibreOffice headless

ODT için LibreOffice kullanılır.

SRP : Yalnızca PDF dönüşümünden sorumlu.
OCP : Yeni motor için yeni _Strategy subclass'ı yaz.
"""

from __future__ import annotations

import io
import tempfile
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.converters.libreoffice_engine import LibreOfficeEngine
from core.converters.ocr_engine import OcrEngine
from core.interfaces.converter_interface import ConversionOptions
from core.utils.pdf_inspector import is_scanned_pdf


# ======================================================================== #
#  Engine Enum                                                               #
# ======================================================================== #

class PdfConversionEngine(Enum):
    PDF2DOCX    = auto()
    OCR         = auto()
    IMAGE_EMBED = auto()
    LIBREOFFICE = auto()
    NONE        = auto()


# ======================================================================== #
#  Abstract Strategy                                                         #
# ======================================================================== #

class _PdfStrategy(ABC):

    @property
    @abstractmethod
    def engine(self) -> PdfConversionEngine: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> Optional[int]:
        """Dönüşümü gerçekleştirir. Sayfa sayısı (varsa) döner."""


# ======================================================================== #
#  Strategy 1 — pdf2docx (Dijital PDF & Standart Düzen)                    #
# ======================================================================== #

class _Pdf2DocxStrategy(_PdfStrategy):
    """
    pdf2docx kütüphanesiyle PDF → DOCX.
    Dijital PDF'lerde tabloları, paragrafları ve fontları 1:1 aktarır.
    """

    @property
    def engine(self) -> PdfConversionEngine:
        return PdfConversionEngine.PDF2DOCX

    def is_available(self) -> bool:
        try:
            import pdf2docx  # noqa: F401
            return True
        except ImportError:
            return False

    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> Optional[int]:
        if target_ext == ".odt":
            raise ValueError("pdf2docx yalnızca DOCX çıktısı üretir.")

        from pdf2docx import Converter as _Cv
        cv = _Cv(str(source_path))
        try:
            cv.convert(str(output_path), start=0, end=None)
            return len(cv.fitz_doc)
        finally:
            cv.close()


# ======================================================================== #
#  Strategy 2 — OCR Tabanlı DOCX (Taranmış PDF'ler İçin)                   #
# ======================================================================== #

class _OcrPdf2DocxStrategy(_PdfStrategy):
    """
    Tesseract OCR ile taranmış PDF'lerdeki yazıları tanıyıp düzenlenebilir
    Word belgesi oluşturur.
    """

    def __init__(self):
        self._ocr = OcrEngine()

    @property
    def engine(self) -> PdfConversionEngine:
        return PdfConversionEngine.OCR

    def is_available(self) -> bool:
        return self._ocr.is_available()

    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> Optional[int]:
        if target_ext == ".odt":
            raise ValueError("OCR motoru doğrudan DOCX çıktısı üretir.")
        return self._ocr.ocr_pdf_to_docx(source_path, output_path)


# ======================================================================== #
#  Strategy 3 — Görsel Gömme DOCX (OCR Olmayan Taranmış PDF'ler)           #
# ======================================================================== #

class _ImageEmbedDocxStrategy(_PdfStrategy):
    """
    OCR bulunmadığında taranmış sayfaları yüksek çözünürlükle Word içine
    hizalar (LibreOffice'in çizim çerçevelerini parçalama hatasını önler).
    """

    @property
    def engine(self) -> PdfConversionEngine:
        return PdfConversionEngine.IMAGE_EMBED

    def is_available(self) -> bool:
        try:
            import fitz  # noqa: F401
            import docx  # noqa: F401
            return True
        except ImportError:
            return False

    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> Optional[int]:
        import fitz
        from docx import Document
        from docx.shared import Inches

        doc = fitz.open(str(source_path))
        word_doc = Document()

        for section in word_doc.sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        total_pages = len(doc)
        try:
            for i, page in enumerate(doc):
                if i > 0:
                    word_doc.add_page_break()

                pix = page.get_pixmap(dpi=200)
                img_stream = io.BytesIO(pix.tobytes("png"))
                word_doc.add_picture(img_stream, width=Inches(7.2))

            output_path.parent.mkdir(parents=True, exist_ok=True)
            word_doc.save(str(output_path))
            return total_pages
        finally:
            doc.close()


# ======================================================================== #
#  Strategy 4 — LibreOffice headless (Fallback / ODT)                       #
# ======================================================================== #

class _LibreOfficePdfStrategy(_PdfStrategy):
    """LibreOffice headless ile PDF → DOCX veya ODT."""

    def __init__(self):
        self._engine = LibreOfficeEngine()

    @property
    def engine(self) -> PdfConversionEngine:
        return PdfConversionEngine.LIBREOFFICE

    def is_available(self) -> bool:
        return self._engine.is_available()

    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> Optional[int]:
        self._engine.convert_to(
            source_path,
            output_path,
            target_ext,
            extra_args=["--infilter=writer_pdf_import"],
        )
        return None


# ======================================================================== #
#  PDF → DOCX Converter                                                     #
# ======================================================================== #

class PdfToDocxConverter(BaseConverter):
    """
    PDF → DOCX dönüştürücü.
    Belge türünü (dijital vs taranmış) akıllıca tespit eder ve en uygun
    stratejiyi uygular.
    """

    def __init__(self):
        self._pdf2docx_strat = _Pdf2DocxStrategy()
        self._ocr_strat = _OcrPdf2DocxStrategy()
        self._img_embed_strat = _ImageEmbedDocxStrategy()
        self._lo_strat = _LibreOfficePdfStrategy()

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".docx"

    @property
    def display_name(self) -> str:
        return "PDF → DOCX"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        is_scanned = is_scanned_pdf(source_path)

        # 1. Taranmış PDF ve OCR mevcutsa → OCR Pipeline
        if is_scanned and self._ocr_strat.is_available():
            pages = self._ocr_strat.convert(source_path, output_path, ".docx")
            return ConvertOutcome(page_count=pages or 1)

        # 2. Standart PDF veya pdf2docx kuruluysa → pdf2docx (en hızlı, 1-2s)
        if self._pdf2docx_strat.is_available():
            pages = self._pdf2docx_strat.convert(source_path, output_path, ".docx")
            return ConvertOutcome(page_count=pages or 1)

        # 3. Taranmış PDF ve OCR yoksa → Temiz Görsel Gömme
        if is_scanned and self._img_embed_strat.is_available():
            pages = self._img_embed_strat.convert(source_path, output_path, ".docx")
            return ConvertOutcome(page_count=pages or 1)

        # 4. Fallback → LibreOffice
        if self._lo_strat.is_available():
            self._lo_strat.convert(source_path, output_path, ".docx")
            return None

        raise RuntimeError("Uygun bir PDF → DOCX dönüştürücü motor bulunamadı.")

    @property
    def unavailable_hint(self) -> str:
        return (
            "Dönüşüm motoru bulunamadı.\n\n"
            "Seçenek 1 — pdf2docx (hızlı ve yüksek kaliteli):\n"
            "  pip install pdf2docx\n\n"
            "Seçenek 2 — Tesseract OCR (taranmış belgeler için):\n"
            "  winget install UB-Mannheim.TesseractOCR\n\n"
            "Seçenek 3 — LibreOffice:\n"
            "  https://www.libreoffice.org/download"
        )

    # ------------------------------------------------------------------ #
    #  Public helpers                                                      #
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        return (
            self._pdf2docx_strat.is_available()
            or self._ocr_strat.is_available()
            or self._img_embed_strat.is_available()
            or self._lo_strat.is_available()
        )

    @property
    def active_engine(self) -> PdfConversionEngine:
        if self._ocr_strat.is_available():
            return PdfConversionEngine.OCR
        if self._pdf2docx_strat.is_available():
            return PdfConversionEngine.PDF2DOCX
        if self._lo_strat.is_available():
            return PdfConversionEngine.LIBREOFFICE
        if self._img_embed_strat.is_available():
            return PdfConversionEngine.IMAGE_EMBED
        return PdfConversionEngine.NONE

    @property
    def active_engine_name(self) -> str:
        # Dijital PDF'ler her zaman pdf2docx ile dönüşür; OCR yalnızca taranmışlarda devreye girer.
        if self._pdf2docx_strat.is_available():
            return "pdf2docx + OCR" if self._ocr_strat.is_available() else "pdf2docx"
        names = {
            PdfConversionEngine.PDF2DOCX:    "pdf2docx",
            PdfConversionEngine.OCR:         "OCR (Tesseract)",
            PdfConversionEngine.IMAGE_EMBED: "Görsel Gömme",
            PdfConversionEngine.LIBREOFFICE: "LibreOffice",
            PdfConversionEngine.NONE:        "Yok",
        }
        return names.get(self.active_engine, "Yok")

    def available_engines(self) -> List[PdfConversionEngine]:
        res = []
        for s in [self._pdf2docx_strat, self._ocr_strat, self._lo_strat]:
            if s.is_available():
                res.append(s.engine)
        return res


# ======================================================================== #
#  PDF → ODT Converter                                                      #
# ======================================================================== #

class PdfToOdtConverter(BaseConverter):
    """
    PDF → ODT dönüştürücü.
    Önce `PdfToDocxConverter`'ın akıllı hattıyla (pdf2docx / OCR / görsel
    gömme) geçici bir DOCX üretilir, ardından LibreOffice DOCX → ODT yapar.

    LibreOffice'in PDF içe aktarıcısı (`writer_pdf_import`) doğrudan
    kullanılmıyor: çizim yoğun PDF'lerde tek çekirdeği dakikalarca
    kilitliyor (45 sayfalık bir ders notunda 15 dk+, bu hatla ~40 sn) ve
    her satırı konumlandırılmış çerçeve yapıp düzenlenemez çıktı üretiyor.
    """

    def __init__(self):
        self._to_docx = PdfToDocxConverter()
        self._lo = LibreOfficeEngine()

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".odt"

    @property
    def display_name(self) -> str:
        return "PDF → ODT"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        with tempfile.TemporaryDirectory(prefix="fileconvert_") as tmp:
            docx_result = self._to_docx.convert(source_path, ConversionOptions(output_dir=Path(tmp)))
            if not docx_result.success:
                raise RuntimeError(docx_result.error_message)
            # LibreOffice çıktıyı kaynak adına göre adlandırır; ara DOCX'in adı hedefle aynı olmalı.
            tmp_docx = docx_result.output_path.rename(Path(tmp) / f"{output_path.stem}.docx")
            self._lo.convert_to(tmp_docx, output_path, "odt")
        return ConvertOutcome(page_count=docx_result.page_count)

    @property
    def unavailable_hint(self) -> str:
        return (
            "LibreOffice kurulu değil.\n\n"
            "Ubuntu/Debian : sudo apt install libreoffice\n"
            "macOS         : brew install --cask libreoffice\n"
            "Windows       : https://www.libreoffice.org/download"
        )

    @property
    def is_available(self) -> bool:
        return self._lo.is_available() and self._to_docx.is_available

    @property
    def active_engine_name(self) -> str:
        if not self.is_available:
            return "Yok"
        return f"{self._to_docx.active_engine_name} + LibreOffice"
