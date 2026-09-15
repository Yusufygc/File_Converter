"""`PdfSplitConverter`'ı gerçek PyMuPDF ile uçtan uca test eder."""

import fitz

from core.converters.pdf_split import PdfSplitConverter
from core.interfaces.converter_interface import ConversionOptions


def _make_pdf(path, page_count: int) -> None:
    doc = fitz.open()
    for i in range(page_count):
        doc.new_page().insert_text((72, 72), f"page {i + 1}")
    doc.save(str(path))
    doc.close()


def test_splits_each_page_into_separate_file(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=3)
    conv = PdfSplitConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.page_count == 3
    assert result.output_path == tmp_path / "belge_sayfa1.pdf"
    for i in range(1, 4):
        page_file = tmp_path / f"belge_sayfa{i}.pdf"
        assert page_file.exists()
        d = fitz.open(str(page_file))
        assert d.page_count == 1
        d.close()


def test_single_page_pdf_output_never_collides_with_source(tmp_path):
    pdf = tmp_path / "tek.pdf"
    _make_pdf(pdf, page_count=1)
    conv = PdfSplitConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.output_path != pdf
    assert result.output_path == tmp_path / "tek_sayfa1.pdf"
    assert pdf.exists()  # kaynak dosya el değmeden duruyor


def test_validate_rejects_non_pdf(tmp_path):
    txt = tmp_path / "input.txt"
    txt.write_text("x")
    conv = PdfSplitConverter()

    assert conv.validate(txt) is False


def test_page_range_splits_only_selected_pages(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=5)
    conv = PdfSplitConverter()

    result = conv.convert(
        pdf, ConversionOptions(output_dir=tmp_path, page_range="1-2,4")
    )

    assert result.success is True
    assert result.page_count == 3
    for i in (1, 2, 4):
        assert (tmp_path / f"belge_sayfa{i}.pdf").exists()
    for i in (3, 5):
        assert not (tmp_path / f"belge_sayfa{i}.pdf").exists()


def test_page_range_single_page_number(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=3)
    conv = PdfSplitConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path, page_range="2"))

    assert result.success is True
    assert result.page_count == 1
    assert result.output_path == tmp_path / "belge_sayfa2.pdf"


def test_page_range_out_of_bounds_fails(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=3)
    conv = PdfSplitConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path, page_range="5"))

    assert result.success is False
    assert "5" in result.error_message


def test_page_range_invalid_format_fails(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=3)
    conv = PdfSplitConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path, page_range="abc"))

    assert result.success is False


def test_page_range_reversed_bounds_fails(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=3)
    conv = PdfSplitConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path, page_range="3-1"))

    assert result.success is False


def test_parse_page_range_dedupes_preserving_order():
    conv = PdfSplitConverter()

    assert conv.parse_page_range("3,1-2,2", page_count=5) == [3, 1, 2]
