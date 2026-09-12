"""`PdfMergeConverter`'ı gerçek PyMuPDF ile hem tekli hem `convert_many` modunda test eder."""

import fitz

from core.converters.pdf_merge import PdfMergeConverter
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.merge_interface import IMergeConverter


def _make_pdf(path, page_count: int) -> None:
    doc = fitz.open()
    for i in range(page_count):
        doc.new_page().insert_text((72, 72), f"page {i + 1}")
    doc.save(str(path))
    doc.close()


def test_is_merge_converter():
    assert isinstance(PdfMergeConverter(), IMergeConverter)


def test_single_file_output_differs_from_source(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=2)
    conv = PdfMergeConverter()

    result = conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.output_path != pdf
    assert result.output_path == tmp_path / "belge_birlesik.pdf"
    assert result.page_count == 2


def test_convert_many_merges_multiple_pdfs(tmp_path):
    pdf1 = tmp_path / "a.pdf"
    pdf2 = tmp_path / "b.pdf"
    _make_pdf(pdf1, page_count=2)
    _make_pdf(pdf2, page_count=3)
    conv = PdfMergeConverter()

    result = conv.convert_many([pdf1, pdf2], ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.page_count == 5
    assert result.output_path == tmp_path / "a_birlesik.pdf"
    doc = fitz.open(str(result.output_path))
    assert doc.page_count == 5
    doc.close()


def test_validate_rejects_non_pdf(tmp_path):
    txt = tmp_path / "input.txt"
    txt.write_text("x")
    conv = PdfMergeConverter()

    assert conv.validate(txt) is False
