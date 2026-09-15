"""
PDF Inspector
=============
PDF dosyalarının yapısını (dijital metin katmanı mı yoksa taranmış görüntü mü)
analiz eder. Saf Python / PyMuPDF mantığıdır, Qt bağımlılığı içermez.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any


def is_scanned_pdf(
    pdf_path: Path,
    max_pages_to_check: int = 5,
    char_threshold_per_page: int = 40,
) -> bool:
    """
    PDF'in taranmış (görüntü tabanlı) olup olmadığını tespit eder.
    
    Örneklem olarak ilk `max_pages_to_check` sayfayı inceler:
    - Sayfa başına düşen ortalama karakter sayısı `char_threshold_per_page`'in altındaysa
    - ve sayfalar görsel (raster image) barındırıyorsa veya hiç metin yoksa `True` döner.
    """
    if not pdf_path.exists():
        return False

    import fitz  # PyMuPDF

    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return False

    try:
        page_count = len(doc)
        if page_count == 0:
            return False

        pages_to_sample = min(page_count, max_pages_to_check)
        total_chars = 0
        has_any_images = False

        for i in range(pages_to_sample):
            page = doc[i]
            text = page.get_text().strip()
            total_chars += len(text)
            if len(page.get_images()) > 0:
                has_any_images = True

        avg_chars = total_chars / pages_to_sample
        # Eğer sayfa başına ortalama karakter eşiğin altındaysa ve resim varsa (veya hiç metin yoksa) taranmıştır
        return avg_chars < char_threshold_per_page and (has_any_images or avg_chars == 0)
    finally:
        doc.close()


def get_pdf_stats(pdf_path: Path) -> Dict[str, Any]:
    """PDF hakkında sayfa sayısı, taranmışlık durumu ve metin yoğunluğu döner."""
    import fitz

    doc = fitz.open(str(pdf_path))
    try:
        page_count = len(doc)
        sample = min(page_count, 5)
        total_chars = sum(len(doc[i].get_text().strip()) for i in range(sample))
        avg_chars = total_chars / sample if sample > 0 else 0
        is_scanned = is_scanned_pdf(pdf_path)

        return {
            "page_count": page_count,
            "is_scanned": is_scanned,
            "avg_chars_per_page": avg_chars,
            "has_text_layer": avg_chars > 30,
        }
    finally:
        doc.close()
