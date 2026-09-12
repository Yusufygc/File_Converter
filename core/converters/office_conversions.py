"""
Basit LibreOffice Dönüşümleri
===============================
XLSX↔PDF/CSV/ODS, DOCX↔ODT gibi yalnızca LibreOffice'in tek satırlık
`--convert-to` çağrısıyla yapılabilen, aralarında dönüşüm mantığı
farkı olmayan converter'lar için ortak taban + concrete alt sınıflar.

Bunları 7 ayrı ~80 satırlık dosya olarak yazmak, `BaseConverter`/
`LibreOfficeEngine`'in zaten çözdüğü "tekrar eden boilerplate" sorununu
üçüncü kez kopyalamak olurdu — `pdf_to_docx.py`'nin birden fazla
converter'ı tek dosyada barındırma deseniyle tutarlı, tek dosyada toplandı.

SRP : Yalnızca "düz LibreOffice --convert-to" dönüşümlerinden sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.converters.libreoffice_engine import LibreOfficeEngine
from core.interfaces.converter_interface import ConversionOptions


class SimpleLibreOfficeConverter(BaseConverter):
    """
    `is_available`/`active_engine_name`/`unavailable_hint`/`_do_convert`'i
    tek yerde çözer. **Kasıtlı olarak** `source_extension`/`target_extension`/
    `display_name`'i implemente ETMEZ — bu üçü `IConverter`'dan abstract
    olarak miras kalır, bu yüzden bu sınıf hâlâ `inspect.isabstract()`
    için `True` döner ve `core/converters/discovery.py` (parametre almadan
    `cls()` ile örneklemeye çalışıp patlamadan) bunu otomatik atlar.
    Yalnızca aşağıdaki gerçek alt sınıflar somutlaşır.
    """

    def __init__(self):
        self._engine = LibreOfficeEngine()

    @property
    def convert_extra_args(self) -> Optional[List[str]]:
        """Gerekirse alt sınıf override eder (örn. CSV import filtresi)."""
        return None

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        self._engine.convert_to(
            source_path, output_path, self.target_extension,
            extra_args=self.convert_extra_args,
        )
        return None

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
        return self._engine.is_available()

    @property
    def active_engine_name(self) -> str:
        return "LibreOffice" if self._engine.is_available() else "Yok"


# ======================================================================== #
#  Excel Ailesi                                                             #
# ======================================================================== #

class XlsxToPdfConverter(SimpleLibreOfficeConverter):
    @property
    def source_extension(self) -> str:
        return ".xlsx"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "Excel → PDF"


class XlsxToCsvConverter(SimpleLibreOfficeConverter):
    @property
    def source_extension(self) -> str:
        return ".xlsx"

    @property
    def target_extension(self) -> str:
        return ".csv"

    @property
    def display_name(self) -> str:
        return "Excel → CSV"


class CsvToXlsxConverter(SimpleLibreOfficeConverter):
    """
    NOT: LibreOffice'in CSV import filtresi bazı delimiter/encoding
    kombinasyonlarında yanlış algılama yapabilir (bilinen bir LibreOffice
    CLI kıvrımı). İlk sürüm varsayılan auto-detect ile gidiyor; sorun
    çıkarsa `convert_extra_args`'a `--infilter` eklenebilir.
    """

    @property
    def source_extension(self) -> str:
        return ".csv"

    @property
    def target_extension(self) -> str:
        return ".xlsx"

    @property
    def display_name(self) -> str:
        return "CSV → Excel"


class XlsxToOdsConverter(SimpleLibreOfficeConverter):
    @property
    def source_extension(self) -> str:
        return ".xlsx"

    @property
    def target_extension(self) -> str:
        return ".ods"

    @property
    def display_name(self) -> str:
        return "Excel → ODS"


class OdsToXlsxConverter(SimpleLibreOfficeConverter):
    @property
    def source_extension(self) -> str:
        return ".ods"

    @property
    def target_extension(self) -> str:
        return ".xlsx"

    @property
    def display_name(self) -> str:
        return "ODS → Excel"


# ======================================================================== #
#  Word ↔ ODT                                                               #
# ======================================================================== #

class DocxToOdtConverter(SimpleLibreOfficeConverter):
    @property
    def source_extension(self) -> str:
        return ".docx"

    @property
    def target_extension(self) -> str:
        return ".odt"

    @property
    def display_name(self) -> str:
        return "Word → ODT"


class OdtToDocxConverter(SimpleLibreOfficeConverter):
    @property
    def source_extension(self) -> str:
        return ".odt"

    @property
    def target_extension(self) -> str:
        return ".docx"

    @property
    def display_name(self) -> str:
        return "ODT → Word"
