"""
Converter Registry
==================
OCP: Yeni converter'lar register() ile eklenir, registry kodu değişmez.
DIP: IConverterRegistry soyutlamasına bağımlı.
"""

from typing import Dict, List, Optional, Tuple

from core.interfaces.converter_interface import IConverter, IConverterRegistry


class ConverterRegistry(IConverterRegistry):
    """Thread-safe converter kayıt defteri."""

    def __init__(self):
        self._registry: Dict[Tuple[str, str], IConverter] = {}

    def register(self, converter: IConverter) -> None:
        key = (
            converter.source_extension.lower(),
            converter.target_extension.lower(),
        )
        self._registry[key] = converter

    def get(self, source_ext: str, target_ext: str) -> Optional[IConverter]:
        key = (source_ext.lower(), target_ext.lower())
        return self._registry.get(key)

    def all_converters(self) -> List[IConverter]:
        return list(self._registry.values())

    def supported_source_extensions(self) -> List[str]:
        return list({k[0] for k in self._registry})
