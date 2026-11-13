"""
DOCX → PDF Converter
======================
LibreOffice headless ile Word belgelerini PDF'e dönüştürür.
Tek motor var (Strategy deseni gerekmiyor) — bkz. libreoffice_engine.py.

SRP : Yalnızca DOCX → PDF dönüşümünden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.converters.libreoffice_engine import LibreOfficeEngine
from core.interfaces.converter_interface import ConversionOptions
from core.user_texts import ENGINE_LIBREOFFICE, ENGINE_UNAVAILABLE, HINT_LIBREOFFICE


class DocxToPdfConverter(BaseConverter):
    """
    DOCX → PDF dönüştürücü.
    Yalnızca LibreOffice headless kullanır (PDF→DOCX yönünün tersi;
    `PdfToOdtConverter` ile aynı tek-motor deseni).
    """

    def __init__(self):
        self._engine = LibreOfficeEngine()

    # ------------------------------------------------------------------ #
    #  IConverter interface                                                #
    # ------------------------------------------------------------------ #

    @property
    def source_extension(self) -> str:
        return ".docx"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "Word → PDF"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        self._engine.convert_to(source_path, output_path, "pdf")
        return None

    @property
    def unavailable_hint(self) -> str:
        return HINT_LIBREOFFICE

    # ------------------------------------------------------------------ #
    #  Public helpers                                                      #
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        return self._engine.is_available()

    @property
    def active_engine_name(self) -> str:
        return ENGINE_LIBREOFFICE if self._engine.is_available() else ENGINE_UNAVAILABLE
