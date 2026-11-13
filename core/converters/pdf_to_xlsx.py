"""
PDF → Excel (Tablo Çıkarma)
=============================
PyMuPDF `page.find_tables()` ile PDF'teki tabloları bulur, her tabloyu
ayrı bir çalışma sayfasına (`S{sayfa}_T{n}`) `openpyxl` ile yazar.

LibreOffice yolu bilinçli olarak kullanılmaz: PDF'i LibreOffice'e
açtırmak tablo değil serbest metin kutuları üretir ve çizim yoğun
PDF'lerde çok yavaştır (bkz. docs/wiki/libreoffice-motoru.md).
Tablo tespiti çizgi/hizalama tabanlıdır; çizgisiz, serbest düzenli
"tablolar" bulunamayabilir — bu durumda anlaşılır hata verilir.

SRP : Yalnızca PDF tablolarını Excel'e aktarmaktan sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import BaseConverter, ConvertOutcome
from core.errors import NothingToConvertError, PasswordProtectedError
from core.interfaces.converter_interface import ConversionOptions
from core.user_texts import ENGINE_BUILTIN, ENGINE_UNAVAILABLE, HINT_BUILTIN_MISSING


class PdfToXlsxConverter(BaseConverter):

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".xlsx"

    @property
    def display_name(self) -> str:
        return "PDF → Excel"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz
        from openpyxl import Workbook

        workbook = Workbook()
        workbook.remove(workbook.active)
        table_count = 0

        doc = fitz.open(str(source_path))
        try:
            if doc.needs_pass:
                raise PasswordProtectedError()
            for page in doc:
                for t_idx, table in enumerate(page.find_tables().tables, start=1):
                    rows = table.extract()
                    if not any(any(cell for cell in row) for row in rows):
                        continue
                    sheet = workbook.create_sheet(f"S{page.number + 1}_T{t_idx}")
                    for row in rows:
                        sheet.append(["" if cell is None else cell for cell in row])
                    table_count += 1
        finally:
            doc.close()

        if table_count == 0:
            raise NothingToConvertError(
                "PDF'te tablo bulunamadı. Yalnızca çizgili tablolar tanınabilir."
            )
        workbook.save(str(output_path))
        return ConvertOutcome(output_path=output_path, page_count=table_count)

    @property
    def unavailable_hint(self) -> str:
        return HINT_BUILTIN_MISSING

    @property
    def is_available(self) -> bool:
        try:
            import fitz  # noqa: F401
            import openpyxl  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def active_engine_name(self) -> str:
        return ENGINE_BUILTIN if self.is_available else ENGINE_UNAVAILABLE

    @property
    def is_parallel_safe(self) -> bool:
        return True
