"""
PDF Şifreleme ve Şifre Kaldırma
=================================
PyMuPDF ile AES-256 parola koruması ekler (`PdfProtectConverter`) veya
bilinen parolayla korumayı kaldırır (`PdfUnlockConverter`). İkisi aynı
şifreleme API'sinin iki yönü olduğu için tek dosyada tutulur
(`office_conversions.py`'nin çoklu converter deseniyle tutarlı).

Parola değerleri hiçbir yerde loglanmaz veya saklanmaz; UI da bunları
QSettings'e yazmaz (bkz. docs/wiki/ui-katmani.md).

SRP : Yalnızca PDF şifreleme durumunu değiştirmekten sorumlu.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.converters.base import ConvertOutcome
from core.converters.pymupdf_tool_base import PyMuPdfToolConverter
from core.errors import (
    InvalidOptionError,
    NothingToConvertError,
    PasswordProtectedError,
    WrongPasswordError,
)
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.option_schema_interface import IOptionsProvider, OptionSpec


class PdfProtectConverter(PyMuPdfToolConverter, IOptionsProvider):
    output_suffix = "_sifreli"

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PDF Şifrele"

    @property
    def option_specs(self) -> List[OptionSpec]:
        return [OptionSpec(key="password", label="Parola", kind="password", required=True)]

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        password = str(options.get_extra("password", ""))
        if not password:
            raise InvalidOptionError("Parola boş olamaz.")

        doc = fitz.open(str(source_path))
        try:
            if doc.needs_pass:
                raise PasswordProtectedError(
                    "PDF zaten parola korumalı. Önce 'PDF Şifre Kaldır' aracını kullanın."
                )
            doc.save(
                str(output_path),
                garbage=3,
                deflate=True,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=password,
                owner_pw=password,
            )
            return ConvertOutcome(output_path=output_path, page_count=doc.page_count)
        finally:
            doc.close()


class PdfUnlockConverter(PyMuPdfToolConverter, IOptionsProvider):
    output_suffix = "_sifresiz"

    @property
    def source_extension(self) -> str:
        return ".pdf"

    @property
    def target_extension(self) -> str:
        return ".pdf"

    @property
    def display_name(self) -> str:
        return "PDF Şifre Kaldır"

    @property
    def option_specs(self) -> List[OptionSpec]:
        # Zorunlu değil: yalnızca "izin" kilitli (açılış parolasız) PDF'lerde
        # parola gerekmeden kısıtlamalar kaldırılabilir.
        return [
            OptionSpec(
                key="password",
                label="Parola",
                kind="password",
                placeholder="Açılış parolası yoksa boş bırakın",
            )
        ]

    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        import fitz

        password = str(options.get_extra("password", ""))
        doc = fitz.open(str(source_path))
        try:
            if doc.needs_pass:
                if not password:
                    raise InvalidOptionError("Bu PDF parola korumalı, parolayı girin.")
                if not doc.authenticate(password):
                    raise WrongPasswordError()
            elif not doc.metadata.get("encryption"):
                raise NothingToConvertError("PDF şifreli değil.")

            doc.save(str(output_path), garbage=3, deflate=True, encryption=fitz.PDF_ENCRYPT_NONE)
            return ConvertOutcome(output_path=output_path, page_count=doc.page_count)
        finally:
            doc.close()
