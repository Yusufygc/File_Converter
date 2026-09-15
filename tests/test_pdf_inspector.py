"""
Unit tests for PdfInspector and OcrEngine
"""

from pathlib import Path
import fitz

from core.utils.pdf_inspector import is_scanned_pdf, get_pdf_stats
from core.converters.ocr_engine import OcrEngine


def test_pdf_inspector_digital_pdf(tmp_path: Path):
    # Metin içeren dijital PDF oluştur
    pdf_path = tmp_path / "digital.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Bu bir dijital test PDF belgesidir. İçinde bolca metin bulunur.")
    doc.save(str(pdf_path))
    doc.close()

    assert is_scanned_pdf(pdf_path) is False
    stats = get_pdf_stats(pdf_path)
    assert stats["is_scanned"] is False
    assert stats["has_text_layer"] is True
    assert stats["page_count"] == 1


def test_pdf_inspector_scanned_image_pdf(tmp_path: Path):
    # Salt görsel içeren taranmış PDF oluştur (metin yok)
    pdf_path = tmp_path / "scanned.pdf"
    doc = fitz.open()
    page = doc.new_page(width=300, height=300)
    # 50x50 kırmızı pixmap
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 50, 50), 1)
    pix.clear_with(255)
    page.insert_image(page.rect, pixmap=pix)
    doc.save(str(pdf_path))
    doc.close()

    assert is_scanned_pdf(pdf_path) is True
    stats = get_pdf_stats(pdf_path)
    assert stats["is_scanned"] is True
    assert stats["has_text_layer"] is False


def test_ocr_engine_graceful_fallback():
    engine = OcrEngine()
    # is_available bool dönmeli
    assert isinstance(engine.is_available(), bool)
