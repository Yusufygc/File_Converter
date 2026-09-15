"""
`PdfToPngConverter`'ı gerçek PyMuPDF ile uçtan uca test eder.
Diğer testlerin aksine `FakeConverter` kullanmaz — burada asıl amaç,
gerçek bir converter'ın `BaseConverter` şablonuyla birlikte doğru
çalıştığını kanıtlamak (bkz. docs/wiki/test-ve-bagimliliklar.md).
"""

import fitz
import pytest

from core.converters.pdf_to_png import PdfToPngConverter
from core.interfaces.converter_interface import ConversionOptions


def _make_pdf(path, page_count: int) -> None:
    doc = fitz.open()
    for i in range(page_count):
        doc.new_page().insert_text((72, 72), f"page {i + 1}")
    doc.save(str(path))
    doc.close()


def test_single_page_pdf_produces_single_png(tmp_path):
    pdf = tmp_path / "single.pdf"
    _make_pdf(pdf, page_count=1)
    conv = PdfToPngConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path, dpi=100))

    assert result.success is True
    assert result.page_count == 1
    assert result.output_path == tmp_path / "single.png"
    assert result.output_path.exists()


def test_multi_page_pdf_produces_one_png_per_page(tmp_path):
    pdf = tmp_path / "multi.pdf"
    _make_pdf(pdf, page_count=3)
    conv = PdfToPngConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path, dpi=100))

    assert result.success is True
    assert result.page_count == 3
    assert result.output_path == tmp_path / "multi_p1.png"
    for i in range(1, 4):
        assert (tmp_path / f"multi_p{i}.png").exists()


def test_validate_rejects_non_pdf(tmp_path):
    txt = tmp_path / "input.txt"
    txt.write_text("x")
    conv = PdfToPngConverter()

    assert conv.validate(txt) is False


def test_is_available_and_engine_name():
    conv = PdfToPngConverter()
    assert conv.is_available is True
    assert conv.active_engine_name == "PyMuPDF"
