"""
`DocxToPdfConverter` için gerçek dönüşüm testi yazılmaz — LibreOffice
binary'sine ihtiyaç duyar ve CI'da kurulu olacağı garanti değildir
(`PdfToDocxConverter`/`PdfToOdtConverter` için de yok, aynı sebep).
Burada yalnızca LibreOffice olmadan da çalışan, saf Python kısımlar
test edilir.
"""

from pathlib import Path

from core.converters.docx_to_pdf import DocxToPdfConverter


def test_validate_accepts_docx_rejects_other(tmp_path):
    conv = DocxToPdfConverter()

    docx = tmp_path / "input.docx"
    docx.write_text("x")
    assert conv.validate(docx) is True

    txt = tmp_path / "input.txt"
    txt.write_text("x")
    assert conv.validate(txt) is False


def test_is_available_is_bool_and_engine_name_consistent():
    conv = DocxToPdfConverter()
    assert isinstance(conv.is_available, bool)
    if conv.is_available:
        assert conv.active_engine_name == "LibreOffice"
    else:
        assert conv.active_engine_name == "Yok"


def test_unavailable_hint_mentions_libreoffice():
    conv = DocxToPdfConverter()
    assert "LibreOffice" in conv.unavailable_hint


def test_display_name_and_extensions():
    conv = DocxToPdfConverter()
    assert conv.source_extension == ".docx"
    assert conv.target_extension == ".pdf"
    assert conv.display_name == "Word → PDF"
