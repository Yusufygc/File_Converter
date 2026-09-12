"""`JpgToPdfConverter`'ı gerçek PyMuPDF ile hem tekli hem `convert_many`
(birleştirme) modunda test eder."""

import fitz

from core.converters.jpg_to_pdf import JpgToPdfConverter
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.merge_interface import IMergeConverter


def _make_jpg(path) -> None:
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 10, 10))
    pix.set_rect(pix.irect, (255, 0, 0))
    pix.save(str(path))


def test_is_merge_converter():
    assert isinstance(JpgToPdfConverter(), IMergeConverter)


def test_single_jpg_produces_single_page_pdf(tmp_path):
    jpg = tmp_path / "a.jpg"
    _make_jpg(jpg)
    conv = JpgToPdfConverter()

    result = conv.convert(jpg, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.page_count == 1
    assert result.output_path == tmp_path / "a.pdf"


def test_convert_many_merges_into_single_multi_page_pdf(tmp_path):
    jpgs = []
    for i in range(3):
        p = tmp_path / f"img{i}.jpg"
        _make_jpg(p)
        jpgs.append(p)
    conv = JpgToPdfConverter()

    result = conv.convert_many(jpgs, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.page_count == 3
    assert result.output_path == tmp_path / "img0_birlesik.pdf"
    doc = fitz.open(str(result.output_path))
    assert doc.page_count == 3
    doc.close()


def test_convert_many_rejects_when_no_valid_files(tmp_path):
    txt = tmp_path / "not_an_image.txt"
    txt.write_text("x")
    conv = JpgToPdfConverter()

    result = conv.convert_many([txt], ConversionOptions(output_dir=tmp_path))

    assert result.success is False
    assert "Geçerli dosya" in result.error_message
