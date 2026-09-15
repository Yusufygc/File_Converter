"""`PdfCompressConverter`'ı gerçek PyMuPDF ile uçtan uca test eder."""

import fitz

from core.converters.pdf_compress import PdfCompressConverter
from core.interfaces.converter_interface import ConversionOptions


def _make_pdf(path, page_count: int = 2) -> None:
    doc = fitz.open()
    for i in range(page_count):
        doc.new_page().insert_text((72, 72), f"page {i + 1}")
    doc.save(str(path))
    doc.close()


def test_output_filename_differs_from_source(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf)
    conv = PdfCompressConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.output_path != pdf
    assert result.output_path == tmp_path / "belge_sikistirilmis.pdf"
    assert result.output_path.exists()


def test_output_filename_differs_even_without_explicit_output_dir(tmp_path):
    """`output_dir=None` iken varsayılan kaynak klasörü kullanılır — bu
    durumda bile üzerine yazma riski olmamalı (asıl güvenlik amacı bu)."""
    pdf = tmp_path / "belge2.pdf"
    _make_pdf(pdf)
    conv = PdfCompressConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=None))

    assert result.success is True
    assert result.output_path != pdf
    assert pdf.exists()  # kaynak dosya el değmeden duruyor


def test_page_count_preserved(tmp_path):
    pdf = tmp_path / "cok_sayfali.pdf"
    _make_pdf(pdf, page_count=4)
    conv = PdfCompressConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.page_count == 4
    out_doc = fitz.open(str(result.output_path))
    assert out_doc.page_count == 4
    out_doc.close()


def test_validate_rejects_non_pdf(tmp_path):
    txt = tmp_path / "input.txt"
    txt.write_text("x")
    conv = PdfCompressConverter()

    assert conv.validate(txt) is False
