"""
Option Schema Capability
==========================
Bazı converter'lar (PDF Döndür, Filigran, Şifrele, ...) kullanıcıdan
araca özgü parametre ister. Her biri için `ConversionOptions`'a ayrı bir
alan + bridge property + QML kontrolü eklemek, her yeni araçta UI'a
dokunmayı zorunlu kılardı. Bunun yerine converter, ihtiyaç duyduğu
alanları `OptionSpec` listesiyle **bildirir**; UI bu şemadan kontrolleri
generik olarak çizer, değerler `ConversionOptions.extra` sözlüğüyle taşınır.

`IPageRangeSelectable`/`IEngineSelectable` ile aynı desen: UI hangi
converter'ın şema sunduğunu `isinstance(c, IOptionsProvider)` ile anlar.

OCP : Yeni parametreli araç eklemek UI kodu değiştirmeyi gerektirmez.
ISP : Parametre istemeyen converter'lar bu protokolü hiç implemente etmez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

# UI'ın çizebildiği kontrol türleri. Yeni tür eklenirse QML tarafındaki
# `DynamicOptionField.qml` da güncellenmelidir.
OPTION_KINDS = ("text", "password", "choice", "int")


@dataclass
class OptionSpec:
    """Tek bir kullanıcı parametresinin tanımı (Value Object)."""
    key: str
    label: str
    kind: str = "text"
    default: Any = None
    choices: List[Tuple[Any, str]] = field(default_factory=list)
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    placeholder: str = ""
    required: bool = False

    def __post_init__(self):
        if self.kind not in OPTION_KINDS:
            raise ValueError(f"Bilinmeyen seçenek türü: {self.kind}")
        if self.kind == "choice" and not self.choices:
            raise ValueError(f"'{self.key}' seçimi için en az bir seçenek gerekli.")

    def to_dict(self) -> Dict[str, Any]:
        """QML'e aktarılabilir düz sözlük (tuple yerine value/label nesneleri)."""
        return {
            "key": self.key,
            "label": self.label,
            "kind": self.kind,
            "default": self.default,
            "choices": [{"value": v, "label": lbl} for v, lbl in self.choices],
            "minimum": self.minimum,
            "maximum": self.maximum,
            "placeholder": self.placeholder,
            "required": self.required,
        }


@runtime_checkable
class IOptionsProvider(Protocol):
    """Araca özgü kullanıcı parametresi bildiren converter'lar için."""

    @property
    def option_specs(self) -> List[OptionSpec]:
        """UI'da gösterilecek parametre alanları (görüntülenme sırasıyla)."""
        ...


def default_option_values(specs: List[OptionSpec]) -> Dict[str, Any]:
    """Şemadaki varsayılan değerlerden başlangıç `extra` sözlüğü üretir."""
    return {s.key: s.default for s in specs}
