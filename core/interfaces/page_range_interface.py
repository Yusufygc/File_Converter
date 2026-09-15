"""
Page Range Selectable Capability
==================================
Bazı converter'lar (örn. PDF Böl) kaynağın yalnızca belirli sayfalarını/
aralıklarını işlemek üzere kullanıcıdan bir aralık ifadesi (örn. "1-3,5")
kabul eder. Bu opsiyonel "capability" protokolü, UI'ın hangi converter'ın
aralık girişi sunduğunu `isinstance(converter, IPageRangeSelectable)` ile
generik biçimde anlamasını sağlar — `IEngineSelectable`/`IMergeConverter`
ile aynı desen, belirli dönüşüm türlerini hardcode etmeden.

`typing.Protocol` kullanır (yapısal sözleşme): converter sınıfları bunu
explicit inherit etmese de gerekli metoda sahipse `isinstance` testi
geçer; yine de netlik için implemente eden sınıflar explicit inherit eder.
"""

from __future__ import annotations

from typing import List, Protocol, runtime_checkable


@runtime_checkable
class IPageRangeSelectable(Protocol):
    """Kaynağın yalnızca belirli sayfalarını işleyen converter'lar için."""

    def parse_page_range(self, page_range: str, page_count: int) -> List[int]:
        """
        '1-3,5' gibi 1-tabanlı bir aralık ifadesini sayfa numarası
        listesine çevirir (görülme sırasına göre tekilleştirilmiş).
        Geçersiz format veya `page_count` dışında bir sayfa içeren
        girişte `ValueError` fırlatır.
        """
        ...
