"""Testlerde paylaşılan sahte converter. Gerçek harici motor (LibreOffice,
PyMuPDF vb.) gerektirmez — `core/` katmanının Qt'siz, hızlı test edilebilir
olduğunu göstermek bu dosyanın amacı."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions


class FakeConverter(BaseConverter):
    def __init__(self, available: bool = True, raise_error: bool = False):
        self._available = available
        self._raise_error = raise_error

    @property
    def source_extension(self) -> str:
        return ".foo"

    @property
    def target_extension(self) -> str:
        return ".bar"

    @property
    def display_name(self) -> str:
        return "FOO → BAR"

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def active_engine_name(self) -> str:
        return "fake-engine"

    @property
    def unavailable_hint(self) -> str:
        return "pip install fake-engine"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        if self._raise_error:
            raise RuntimeError("boom")
        output_path.write_text(source_path.read_text())
        return None
