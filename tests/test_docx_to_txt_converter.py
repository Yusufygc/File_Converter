"""`DocxToTxtConverter`'ı gerçek `python-docx` ile uçtan uca test eder."""

from docx import Document

from core.converters.docx_to_txt import DocxToTxtConverter
from core.interfaces.converter_interface import ConversionOptions


def _make_docx(path, paragraphs):
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    doc.save(str(path))


def test_extracts_paragraph_text(tmp_path):
    docx = tmp_path / "belge.docx"
    _make_docx(docx, ["merhaba dunya", "ikinci paragraf"])
    conv = DocxToTxtConverter()

    result = conv.convert(docx, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.output_path == tmp_path / "belge.txt"
    content = result.output_path.read_text(encoding="utf-8")
    assert "merhaba dunya" in content
    assert "ikinci paragraf" in content


def test_validate_rejects_non_docx(tmp_path):
    txt = tmp_path / "input.txt"
    txt.write_text("x")
    conv = DocxToTxtConverter()

    assert conv.validate(txt) is False


def test_is_available_and_engine_name():
    conv = DocxToTxtConverter()
    assert conv.is_available is True
    assert conv.active_engine_name == "python-docx"


def test_is_parallel_safe():
    assert DocxToTxtConverter().is_parallel_safe is True
