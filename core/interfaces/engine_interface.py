"""
Engine Selectable Capability
=============================
Bazı converter'lar (örn. PPTX→PDF) birden fazla dönüşüm motoru arasında
kullanıcının elle seçim yapmasına izin verir (MS Office/LibreOffice gibi).
Bu opsiyonel "capability" protokolü, UI'ın hangi converter'ın motor
seçimi sunduğunu `isinstance(converter, IEngineSelectable)` ile generik
biçimde anlamasını sağlar — belirli dönüşüm türlerini hardcode etmeden.

`typing.Protocol` kullanır (yapısal sözleşme): converter sınıfları bunu
explicit inherit etmese de gerekli metodlara sahipse `isinstance` testi
geçer; yine de netlik için implemente eden sınıflar explicit inherit eder.
"""

from __future__ import annotations

from typing import Any, List, Protocol, runtime_checkable


@runtime_checkable
class IEngineSelectable(Protocol):
    """Birden fazla dönüşüm motoru arasında kullanıcı seçimi sunan converter'lar için."""

    @property
    def active_engine(self) -> Any:
        """Şu anda aktif olan motor (converter'a özel enum değeri)."""
        ...

    def available_engines(self) -> List[Any]:
        """Sistemde kullanılabilir motorların listesini döndürür."""
        ...

    def set_preferred_engine(self, engine: Any) -> bool:
        """Motoru elle seç. Mevcut değilse False döner, aktif motor değişmez."""
        ...
