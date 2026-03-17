"""
PPTX → PDF Converter
====================
Strategy Pattern ile çoklu dönüşüm motoru desteği.

Öncelik sırası:
  1. Microsoft Office (win32com) — Windows + Office kurulu ise
  2. LibreOffice headless      — cross-platform fallback
  3. İkisi de yoksa anlamlı hata

SRP : Sadece PPTX→PDF dönüşümünden sorumlu.
OCP : Yeni motor eklemek için sadece yeni bir _Engine subclass'ı yaz.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

from core.interfaces.converter_interface import (
    ConversionOptions,
    ConversionResult,
    IConverter,
)


# ======================================================================== #
#  Engine Enum — hangi motorun kullanıldığını raporlamak için              #
# ======================================================================== #

class ConversionEngine(Enum):
    MS_OFFICE   = auto()
    LIBREOFFICE = auto()
    NONE        = auto()


# ======================================================================== #
#  Abstract Engine Strategy                                                 #
# ======================================================================== #

class _ConversionStrategy(ABC):
    """Her dönüşüm motoru bu sözleşmeyi uygular."""

    @property
    @abstractmethod
    def engine(self) -> ConversionEngine: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def convert(self, source_path: Path, output_path: Path) -> None:
        """
        Dönüşümü gerçekleştirir.
        Başarısızlıkta Exception fırlatır.
        """


# ======================================================================== #
#  Strategy 1 — Microsoft Office (win32com)                                #
# ======================================================================== #

class _MsOfficeStrategy(_ConversionStrategy):
    """
    PowerPoint COM otomasyonu ile dönüştürür.
    Gereksinim: Windows + Microsoft Office kurulu + pywin32

    pip install pywin32
    """

    # PowerPoint.SaveAs formatı: 32 = ppSaveAsPDF
    _PP_SAVE_AS_PDF = 32

    @property
    def engine(self) -> ConversionEngine:
        return ConversionEngine.MS_OFFICE

    def is_available(self) -> bool:
        if sys.platform != "win32":
            return False
        try:
            import win32com.client  # noqa: F401
            return True
        except ImportError:
            return False

    def convert(self, source_path: Path, output_path: Path) -> None:
        import win32com.client

        powerpoint = None
        presentation = None
        try:
            powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            presentation = powerpoint.Presentations.Open(
                str(source_path.resolve()),
                ReadOnly=True,
                Untitled=False,
                WithWindow=False,
            )
            presentation.SaveAs(
                str(output_path.resolve()),
                self._PP_SAVE_AS_PDF,
            )
        finally:
            if presentation is not None:
                try:
                    presentation.Close()
                except Exception:
                    pass
            if powerpoint is not None:
                try:
                    powerpoint.Quit()
                except Exception:
                    pass


# ======================================================================== #
#  Strategy 2 — LibreOffice headless                                       #
# ======================================================================== #

class _LibreOfficeStrategy(_ConversionStrategy):
    """LibreOffice headless ile dönüştürür. Cross-platform."""

    _CANDIDATES: List[str] = [
        "libreoffice",
        "soffice",
        "/usr/lib/libreoffice/program/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]

    def __init__(self):
        self._path: Optional[str] = self._detect()

    @property
    def engine(self) -> ConversionEngine:
        return ConversionEngine.LIBREOFFICE

    def is_available(self) -> bool:
        return self._path is not None

    def convert(self, source_path: Path, output_path: Path) -> None:
        out_dir = output_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [
                self._path,
                "--headless",
                "--invisible",
                "--nologo",
                "--norestore",
                "--convert-to", "pdf",
                "--outdir", str(out_dir),
                str(source_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice hatası:\n{result.stderr or result.stdout}"
            )

        lo_out = out_dir / (source_path.stem + ".pdf")
        if not lo_out.exists():
            fallback = source_path.parent / (source_path.stem + ".pdf")
            if fallback.exists() and fallback != lo_out:
                shutil.move(str(fallback), str(lo_out))
            else:
                raise FileNotFoundError(
                    f"Dönüşüm sonrası PDF bulunamadı: {lo_out}"
                )

        if lo_out != output_path:
            shutil.move(str(lo_out), str(output_path))

    @staticmethod
    def _detect() -> Optional[str]:
        for candidate in _LibreOfficeStrategy._CANDIDATES:
            found = shutil.which(candidate) or (
                Path(candidate).exists() and candidate
            )
            if found:
                return str(found)
        return None


# ======================================================================== #
#  Ana Converter — Strategy'leri orkestre eder                             #
# ======================================================================== #

class PptxToPdfConverter(IConverter):
    """
    PPTX → PDF dönüştürücü.

    Mevcut motorları öncelik sırasına göre dener:
      MS Office → LibreOffice → Hata

    Kullanıcı isterse `preferred_engine` ile motor kilitlenebilir.
    """

    def __init__(self, preferred_engine: Optional[ConversionEngine] = None):
        self._strategies: List[_ConversionStrategy] = [
            _MsOfficeStrategy(),
            _LibreOfficeStrategy(),
        ]
        self._preferred = preferred_engine
        self._active_strategy: Optional[_ConversionStrategy] = (
            self._resolve_strategy()
        )

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

    @property
    def source_extension(self) -> str:
        return ".pptx"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PowerPoint → PDF"

    def validate(self, source_path: Path) -> bool:
        return (
            source_path.exists()
            and source_path.is_file()
            and source_path.suffix.lower() == self.source_extension
        )

    def convert(
        self,
        source_path: Path,
        options: ConversionOptions,
    ) -> ConversionResult:
        start = time.monotonic()

        if not self.validate(source_path):
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message=f"Geçersiz dosya: {source_path.name}",
                elapsed_seconds=time.monotonic() - start,
            )

        if self._active_strategy is None:
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message=self._no_engine_message(),
                elapsed_seconds=time.monotonic() - start,
            )

        output_path = self.get_output_path(source_path, options)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._active_strategy.convert(source_path, output_path)
            return ConversionResult(
                source_path=source_path,
                output_path=output_path,
                success=True,
                elapsed_seconds=time.monotonic() - start,
            )
        except Exception as exc:
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message=str(exc),
                elapsed_seconds=time.monotonic() - start,
            )

    # ------------------------------------------------------------------ #
    #  Public helpers (UI tarafından kullanılır)                          #
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        return self._active_strategy is not None

    @property
    def active_engine(self) -> ConversionEngine:
        if self._active_strategy is None:
            return ConversionEngine.NONE
        return self._active_strategy.engine

    @property
    def active_engine_name(self) -> str:
        return {
            ConversionEngine.MS_OFFICE:   "Microsoft Office",
            ConversionEngine.LIBREOFFICE: "LibreOffice",
            ConversionEngine.NONE:        "Yok",
        }[self.active_engine]

    def available_engines(self) -> List[ConversionEngine]:
        return [s.engine for s in self._strategies if s.is_available()]

    def set_preferred_engine(self, engine: ConversionEngine) -> bool:
        """
        Motoru elle seç. Mevcut değilse False döner, strateji değişmez.
        UI'daki ComboBox buraya bağlanır.
        """
        self._preferred = engine
        new_strategy = self._resolve_strategy()
        if new_strategy is None:
            return False
        self._active_strategy = new_strategy
        return True

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _resolve_strategy(self) -> Optional[_ConversionStrategy]:
        """Tercih edilen veya ilk müsait stratejiyi döndürür."""
        if self._preferred is not None:
            for s in self._strategies:
                if s.engine == self._preferred and s.is_available():
                    return s
            return None

        for s in self._strategies:
            if s.is_available():
                return s
        return None

    @staticmethod
    def _no_engine_message() -> str:
        if sys.platform == "win32":
            return (
                "Dönüşüm motoru bulunamadı.\n\n"
                "Seçenek 1 — Microsoft Office (önerilen):\n"
                "  Office kuruluysa: pip install pywin32\n\n"
                "Seçenek 2 — LibreOffice (ücretsiz):\n"
                "  https://www.libreoffice.org/download"
            )
        return (
            "LibreOffice bulunamadı.\n\n"
            "Ubuntu/Debian : sudo apt install libreoffice\n"
            "macOS         : brew install --cask libreoffice\n"
            "  veya        : https://www.libreoffice.org/download"
        )