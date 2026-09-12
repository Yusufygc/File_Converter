"""`PdfToTxtConverter`'ı gerçek PyMuPDF ile uçtan uca test eder."""

import fitz

from core.converters.pdf_to_txt import PdfToTxtConverter
from core.interfaces.converter_interface import ConversionOptions


def _make_pdf(path, texts):
    doc = fitz.open()
    for t in texts:
        doc.new_page().insert_text((72, 72), t)
    doc.save(str(path))
    doc.close()


def test_extracts_text_from_single_page(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, ["merhaba dunya"])
    conv = PdfToTxtConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.output_path == tmp_path / "belge.txt"
    content = result.output_path.read_text(encoding="utf-8")
    assert "merhaba dunya" in content


def test_multi_page_text_joined_with_page_markers(tmp_path):
    pdf = tmp_path / "cok.pdf"
    _make_pdf(pdf, ["birinci sayfa", "ikinci sayfa"])
    conv = PdfToTxtConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.page_count == 2
    content = result.output_path.read_text(encoding="utf-8")
    assert "birinci sayfa" in content
    assert "ikinci sayfa" in content
    assert "Sayfa 2" in content


def test_validate_rejects_non_pdf(tmp_path):
    txt = tmp_path / "input.txt"
    txt.write_text("x")
    conv = PdfToTxtConverter()

    assert conv.validate(txt) is False


def test_is_parallel_safe():
    assert PdfToTxtConverter().is_parallel_safe is True
