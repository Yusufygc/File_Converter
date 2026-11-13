"""
iLovePDF genişletmesi Paket 3 — Aranabilir PDF (OCR), PDF→Markdown,
PDF→Excel. OCR testi Tesseract kurulu değilse atlanır (CI'da garanti yok,
bkz. docs/wiki/test-ve-bagimliliklar.md).
"""

from pathlib import Path

import fitz
import pytest

from core.converters.pdf_ocr import PdfOcrConverter
from core.converters.pdf_to_markdown import PdfToMarkdownConverter
from core.converters.pdf_to_xlsx import PdfToXlsxConverter
from core.interfaces.converter_interface import ConversionOptions


def _opts(tmp_path):
    return ConversionOptions(output_dir=tmp_path / "out")


# ── PDF → Markdown ─────────────────────────────────────────────────────

def test_markdown_contains_text_and_respects_page_range(tmp_path):
    src = tmp_path / "m.pdf"
    doc = fitz.open()
    for i in range(3):
        doc.new_page().insert_text((72, 72), f"Bolum {i + 1} icerigi", fontsize=14)
    doc.save(str(src))
    doc.close()

    conv = PdfToMarkdownConverter()
    if not conv.is_available:
        pytest.skip("pymupdf4llm kurulu değil")
    opts = _opts(tmp_path)
    opts.page_range = "2-3"

    result = conv.convert(src, opts)

    assert result.success, result.error_message
    assert result.output_path.suffix == ".md"
    text = result.output_path.read_text(encoding="utf-8")
    assert "Bolum 2" in text and "Bolum 3" in text
    assert "Bolum 1" not in text
    assert result.page_count == 2


def test_markdown_errors_on_textless_pdf(tmp_path):
    src = tmp_path / "bos.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(src))
    doc.close()
    conv = PdfToMarkdownConverter()
    if not conv.is_available:
        pytest.skip("pymupdf4llm kurulu değil")

    result = conv.convert(src, _opts(tmp_path))
    assert result.success is False


# ── PDF → Excel ────────────────────────────────────────────────────────

def _make_table_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    cells = [["Ad", "Adet"], ["Elma", "3"], ["Armut", "5"]]
    x0, y0, w, h = 72, 72, 120, 24
    for r, row in enumerate(cells):
        for c, value in enumerate(row):
            rect = fitz.Rect(x0 + c * w, y0 + r * h, x0 + (c + 1) * w, y0 + (r + 1) * h)
            page.draw_rect(rect, color=(0, 0, 0), width=1)
            page.insert_text((rect.x0 + 6, rect.y1 - 7), value, fontsize=11)
    doc.save(str(path))
    doc.close()


def test_xlsx_extracts_ruled_table(tmp_path):
    from openpyxl import load_workbook

    src = tmp_path / "t.pdf"
    _make_table_pdf(src)
    conv = PdfToXlsxConverter()
    if not conv.is_available:
        pytest.skip("openpyxl kurulu değil")

    result = conv.convert(src, _opts(tmp_path))

    assert result.success, result.error_message
    wb = load_workbook(result.output_path)
    assert wb.sheetnames == ["S1_T1"]
    rows = [[str(v).strip() for v in row] for row in wb["S1_T1"].iter_rows(values_only=True)]
    assert rows == [["Ad", "Adet"], ["Elma", "3"], ["Armut", "5"]]


def test_xlsx_errors_without_tables(tmp_path):
    src = tmp_path / "metin.pdf"
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "Tablo yok")
    doc.save(str(src))
    doc.close()
    conv = PdfToXlsxConverter()
    if not conv.is_available:
        pytest.skip("openpyxl kurulu değil")

    result = conv.convert(src, _opts(tmp_path))
    assert result.success is False
    assert "tablo" in result.error_message.lower()


# ── Aranabilir PDF (OCR) ──────────────────────────────────────────────

def test_ocr_metadata():
    conv = PdfOcrConverter()
    src = Path("x.pdf")
    out = conv.get_output_path(src, ConversionOptions())
    assert out.name == "x_aranabilir.pdf" and out != src
    assert conv.is_parallel_safe is False
    assert "Tesseract" in conv.unavailable_hint


def _make_scanned_pdf(path):
    """Metni görsele çevrilmiş (taranmış gibi) tek sayfalık PDF üretir."""
    text_doc = fitz.open()
    page = text_doc.new_page()
    page.insert_text((72, 120), "TARANMIS BELGE ORNEGI", fontsize=28)
    pix = page.get_pixmap(dpi=200)
    text_doc.close()

    doc = fitz.open()
    target = doc.new_page()
    target.insert_image(target.rect, pixmap=pix)
    doc.save(str(path))
    doc.close()


def test_ocr_adds_searchable_text_layer(tmp_path):
    conv = PdfOcrConverter()
    if not conv.is_available:
        pytest.skip("Tesseract kurulu değil")
    src = tmp_path / "tarama.pdf"
    _make_scanned_pdf(src)

    result = conv.convert(src, _opts(tmp_path))

    assert result.success, result.error_message
    doc = fitz.open(str(result.output_path))
    original = fitz.open(str(src))
    assert doc[0].rect == original[0].rect
    assert "TARANMIS" in doc[0].get_text().upper()
    doc.close()
    original.close()


def test_ocr_skips_already_digital_pdf(tmp_path):
    conv = PdfOcrConverter()
    if not conv.is_available:
        pytest.skip("Tesseract kurulu değil")
    src = tmp_path / "dijital.pdf"
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "Bu sayfa zaten secilebilir metin iceriyor.")
    doc.save(str(src))
    doc.close()

    result = conv.convert(src, _opts(tmp_path))
    assert result.success is False
    assert "işlem gerekmedi" in result.error_message
