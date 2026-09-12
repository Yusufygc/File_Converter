"""
PDF → DOCX / ODT Converter
===========================
Öncelik sırası (DOCX):
  1. pdf2docx — saf Python, yüksek kaliteli dönüşüm
  2. LibreOffice headless — cross-platform fallback

ODT için yalnızca LibreOffice kullanılır.

SRP : Yalnızca PDF dönüşümünden sorumlu.
OCP : Yeni motor için yeni _Strategy subclass'ı yaz.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.converters.libreoffice_engine import LibreOfficeEngine
from core.interfaces.converter_interface import ConversionOptions


# ======================================================================== #
#  Engine Enum                                                               #
# ======================================================================== #

class PdfConversionEngine(Enum):
    PDF2DOCX    = auto()
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
    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> None:
        """Dönüşümü gerçekleştirir. Başarısızlıkta Exception fırlatır."""


# ======================================================================== #
#  Strategy 1 — pdf2docx                                                    #
# ======================================================================== #

class _Pdf2DocxStrategy(_PdfStrategy):
    """
    pdf2docx kütüphanesiyle PDF → DOCX.
    Kurulum: pip install pdf2docx
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

    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> None:
        if target_ext == ".odt":
            raise ValueError("pdf2docx yalnızca DOCX çıktısı üretir.")

        from pdf2docx import Converter as _Cv
        cv = _Cv(str(source_path))
        try:
            cv.convert(str(output_path), start=0, end=None)
        finally:
            cv.close()


# ======================================================================== #
#  Strategy 2 — LibreOffice headless                                        #
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

    def convert(self, source_path: Path, output_path: Path, target_ext: str) -> None:
        # --infilter=writer_pdf_import: PDF'i Writer belgesi olarak import eder.
        # Bu olmadan LibreOffice "no export filter" hatası verir.
        self._engine.convert_to(
            source_path, output_path, target_ext,
            extra_args=["--infilter=writer_pdf_import"],
        )


# ======================================================================== #
#  PDF → DOCX Converter                                                     #
# ======================================================================== #

class PdfToDocxConverter(BaseConverter):
    """
    PDF → DOCX dönüştürücü.
    Önce pdf2docx dener, bulamazsa LibreOffice'e geçer.
    """

    def __init__(self):
        self._strategies: List[_PdfStrategy] = [
            _Pdf2DocxStrategy(),
            _LibreOfficePdfStrategy(),
        ]
        self._active_strategy: Optional[_PdfStrategy] = self._resolve_strategy()

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
        self._active_strategy.convert(source_path, output_path, ".docx")
        return None

    @property
    def unavailable_hint(self) -> str:
        return (
            "Dönüşüm motoru bulunamadı.\n\n"
            "Seçenek 1 — pdf2docx (önerilen):\n"
            "  pip install pdf2docx\n\n"
            "Seçenek 2 — LibreOffice (ücretsiz):\n"
            "  https://www.libreoffice.org/download"
        )

    # ------------------------------------------------------------------ #
    #  Public helpers                                                      #
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        return self._active_strategy is not None

    @property
    def active_engine(self) -> PdfConversionEngine:
        return self._active_strategy.engine if self._active_strategy else PdfConversionEngine.NONE

    @property
    def active_engine_name(self) -> str:
        return {
            PdfConversionEngine.PDF2DOCX:    "pdf2docx",
            PdfConversionEngine.LIBREOFFICE: "LibreOffice",
            PdfConversionEngine.NONE:        "Yok",
        }[self.active_engine]

    def available_engines(self) -> List[PdfConversionEngine]:
        return [s.engine for s in self._strategies if s.is_available()]

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _resolve_strategy(self) -> Optional[_PdfStrategy]:
        for s in self._strategies:
            if s.is_available():
                return s
        return None


# ======================================================================== #
#  PDF → ODT Converter                                                      #
# ======================================================================== #

class PdfToOdtConverter(BaseConverter):
    """
    PDF → ODT dönüştürücü.
    Yalnızca LibreOffice headless kullanır.
    """

    def __init__(self):
        self._lo_strategy = _LibreOfficePdfStrategy()

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

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
        self._lo_strategy.convert(source_path, output_path, ".odt")
        return None

    @property
    def unavailable_hint(self) -> str:
        return (
            "LibreOffice kurulu değil.\n\n"
            "Ubuntu/Debian : sudo apt install libreoffice\n"
            "macOS         : brew install --cask libreoffice\n"
            "Windows       : https://www.libreoffice.org/download"
        )

    # ------------------------------------------------------------------ #
    #  Public helpers                                                      #
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        return self._lo_strategy.is_available()

    @property
    def active_engine_name(self) -> str:
        return "LibreOffice" if self._lo_strategy.is_available() else "Yok"
