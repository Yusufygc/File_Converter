"""
PDF Onarma
============
PyMuPDF (MuPDF) bozuk xref tablosu, eksik `startxref` veya kırık nesne
akışları olan PDF'leri açarken otomatik olarak yeniden kurar. Belgeyi
`garbage=4` + `clean=True` ile baştan yazmak bu onarımı kalıcı hale
getirir ve kullanılmayan/bozuk nesneleri atar.

Kurtarılamayacak kadar bozuk dosyada `fitz.open` hata fırlatır;
`BaseConverter` bunu kullanıcıya hata sonucu olarak gösterir.

SRP : Yalnızca PDF yapısal onarımından sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.converters.base import ConvertOutcome
from core.converters.pymupdf_tool_base import PyMuPdfToolConverter
from core.errors import CorruptFileError, PasswordProtectedError
from core.interfaces.converter_interface import ConversionOptions


class PdfRepairConverter(PyMuPdfToolConverter):
    output_suffix = "_onarilmis"

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PDF Onar"

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        doc = fitz.open(str(source_path))
        try:
            if doc.needs_pass:
                raise PasswordProtectedError()
            if doc.page_count == 0:
                raise CorruptFileError("PDF'te kurtarılabilir sayfa bulunamadı.")
            doc.save(str(output_path), garbage=4, deflate=True, clean=True)
            return ConvertOutcome(output_path=output_path, page_count=doc.page_count)
        finally:
            doc.close()
