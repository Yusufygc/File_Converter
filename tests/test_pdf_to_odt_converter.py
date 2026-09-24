"""
`PdfToOdtConverter` — PDF önce gerçek pdf2docx ile DOCX'e çevrilir, sonra
LibreOffice DOCX → ODT yapar. CI'da LibreOffice garanti olmadığı için LO
adımı sahte bir motorla taklit edilir; asıl doğrulanan, ara DOCX'in
hedefle aynı adla LO'ya verilmesi (LO çıktıyı kaynak adına göre yazar).
"""

import shutil

import fitz

from core.converters.pdf_to_docx import PdfToOdtConverter
from core.interfaces.converter_interface import ConversionOptions


def _make_pdf(path, page_count: int) -> None:
    doc = fitz.open()
    for i in range(page_count):
        doc.new_page().insert_text((72, 72), f"page {i + 1}")
    doc.save(str(path))
    doc.close()


class _FakeLibreOffice:
    def __init__(self):
        self.calls = []

    def is_available(self) -> bool:
        return True

    def convert_to(self, source_path, output_path, target_ext, extra_args=None):
        self.calls.append((source_path.name, source_path.suffix, target_ext, extra_args))
        shutil.copy(source_path, output_path.parent / f"{source_path.stem}.odt")


def test_pdf_goes_through_docx_then_libreoffice(tmp_path):
    pdf = tmp_path / "belge.pdf"
    _make_pdf(pdf, page_count=2)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    conv = PdfToOdtConverter()
    fake = _FakeLibreOffice()
    conv._lo = fake

    result = conv.convert(pdf, ConversionOptions(output_dir=out_dir))

    assert result.success is True, result.error_message
    assert result.output_path == out_dir / "belge.odt"
    assert result.output_path.exists()
    assert result.page_count == 2
    assert fake.calls == [("belge.docx", ".docx", "odt", None)]
    # Ara DOCX çıktı klasörüne sızmaz.
    assert sorted(p.name for p in out_dir.iterdir()) == ["belge.odt"]


def test_does_not_use_libreoffice_pdf_import(tmp_path):
    pdf = tmp_path / "x.pdf"
    _make_pdf(pdf, page_count=1)
    conv = PdfToOdtConverter()
    fake = _FakeLibreOffice()
    conv._lo = fake

    conv.convert(pdf, ConversionOptions(output_dir=tmp_path))

    assert all(extra is None for *_, extra in fake.calls)
