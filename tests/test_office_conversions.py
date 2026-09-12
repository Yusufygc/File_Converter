"""
`office_conversions.py`'deki 7 `SimpleLibreOfficeConverter` alt sınıfı
için ortak, LibreOffice binary'sine ihtiyaç duymayan kontroller.

Gerçek dönüşüm testi yok — `PdfToDocxConverter`/`PdfToOdtConverter`/
`DocxToPdfConverter` için de yok, CI'da LibreOffice kurulu olacağı
garanti değil (bkz. docs/wiki/test-ve-bagimliliklar.md).
"""

import pytest

from core.converters.office_conversions import (
    CsvToXlsxConverter,
    DocxToOdtConverter,
    OdsToXlsxConverter,
    OdtToDocxConverter,
    XlsxToCsvConverter,
    XlsxToOdsConverter,
    XlsxToPdfConverter,
)

_CASES = [
    (XlsxToPdfConverter, ".xlsx", ".pdf"),
    (XlsxToCsvConverter, ".xlsx", ".csv"),
    (CsvToXlsxConverter, ".csv", ".xlsx"),
    (XlsxToOdsConverter, ".xlsx", ".ods"),
    (OdsToXlsxConverter, ".ods", ".xlsx"),
    (DocxToOdtConverter, ".docx", ".odt"),
    (OdtToDocxConverter, ".odt", ".docx"),
]


@pytest.mark.parametrize("cls,source_ext,target_ext", _CASES)
def test_extensions_match_expected(cls, source_ext, target_ext):
    conv = cls()
    assert conv.source_extension == source_ext
    assert conv.target_extension == target_ext
    assert conv.accepted_extensions == [source_ext]


@pytest.mark.parametrize("cls,source_ext,target_ext", _CASES)
def test_display_name_is_nonempty_string(cls, source_ext, target_ext):
    assert isinstance(cls().display_name, str) and cls().display_name


@pytest.mark.parametrize("cls,source_ext,target_ext", _CASES)
def test_validate_accepts_correct_extension_rejects_other(cls, source_ext, target_ext, tmp_path):
    conv = cls()
    good = tmp_path / f"input{source_ext}"
    good.write_text("x")
    bad = tmp_path / "input.zzz"
    bad.write_text("x")

    assert conv.validate(good) is True
    assert conv.validate(bad) is False


@pytest.mark.parametrize("cls,source_ext,target_ext", _CASES)
def test_is_available_is_bool_and_engine_name_consistent(cls, source_ext, target_ext):
    conv = cls()
    assert isinstance(conv.is_available, bool)
    if conv.is_available:
        assert conv.active_engine_name == "LibreOffice"
    else:
        assert conv.active_engine_name == "Yok"


@pytest.mark.parametrize("cls,source_ext,target_ext", _CASES)
def test_unavailable_hint_mentions_libreoffice(cls, source_ext, target_ext):
    assert "LibreOffice" in cls().unavailable_hint


@pytest.mark.parametrize("cls,source_ext,target_ext", _CASES)
def test_not_parallel_safe_by_default(cls, source_ext, target_ext):
    # LibreOffice subprocess'leri paralel çalıştırıldığında profil/soket
    # çakışması riski taşıyor - bkz. docs/wiki/libreoffice-motoru.md.
    assert cls().is_parallel_safe is False
