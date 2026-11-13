"""
Sayfa Aralığı Ayrıştırma
==========================
"1-3,5,7-9" gibi 1-tabanlı aralık ifadelerini sayfa listesine çevirir.
Önceden yalnızca `PdfSplitConverter` içindeydi; PDF Döndür, PDF→Markdown
gibi `IPageRangeSelectable` sunan diğer converter'lar da aynı kuralları
(sıra korunur, tekrar atılır, sınır dışı = hata) paylaşsın diye ayrıldı.

SRP : Yalnızca aralık ifadesi ayrıştırmadan sorumlu.
"""

from __future__ import annotations

from typing import List

from core.errors import InvalidOptionError


def parse_page_range(page_range: str, page_count: int) -> List[int]:
    pages: List[int] = []
    seen = set()
    for part in page_range.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_str, _, end_str = part.partition("-")
            try:
                start, end = int(start_str.strip()), int(end_str.strip())
            except ValueError:
                raise InvalidOptionError(f"Geçersiz sayfa aralığı: '{part}'") from None
        else:
            try:
                start = end = int(part)
            except ValueError:
                raise InvalidOptionError(f"Geçersiz sayfa numarası: '{part}'") from None

        if start < 1 or end < start or end > page_count:
            raise InvalidOptionError(
                f"Geçersiz sayfa aralığı: '{part}' (belge {page_count} sayfa içeriyor)"
            )

        for page_num in range(start, end + 1):
            if page_num not in seen:
                seen.add(page_num)
                pages.append(page_num)

    if not pages:
        raise InvalidOptionError("Sayfa aralığı boş.")
    return pages
