"""
Converter Registry
==================
OCP: Yeni converter'lar register() ile eklenir, registry kodu değişmez.
DIP: IConverterRegistry soyutlamasına bağımlı.
"""

from typing import Dict, List, Optional, Tuple

from core.interfaces.converter_interface import IConverter, IConverterRegistry


class ConverterRegistry(IConverterRegistry):
    """
    Thread-safe converter kayıt defteri.

    İç anahtar `(source_ext, target_ext, class_name)` — yalnızca
    `(source_ext, target_ext)` kullanılsaydı aynı uzantı çiftini
    paylaşan birden fazla converter (örn. `PdfCompressConverter`,
    `PdfSplitConverter`, `PdfMergeConverter` — hepsi `.pdf`→`.pdf`)
    birbirinin üzerine yazardı ve sessizce kaybolurdu. Sınıf adı
    eklenerek her converter kendi slotunu korur.
    """

    def __init__(self):
        self._registry: Dict[Tuple[str, str, str], IConverter] = {}

    def register(self, converter: IConverter) -> None:
        key = (
            converter.source_extension.lower(),
            converter.target_extension.lower(),
            converter.__class__.__name__,
        )
        self._registry[key] = converter

    def get(self, source_ext: str, target_ext: str) -> Optional[IConverter]:
        source_ext, target_ext = source_ext.lower(), target_ext.lower()
        for (s, t, _), converter in self._registry.items():
            if s == source_ext and t == target_ext:
                return converter
        return None

    def all_converters(self) -> List[IConverter]:
        return list(self._registry.values())

    def supported_source_extensions(self) -> List[str]:
        return list({k[0] for k in self._registry})
