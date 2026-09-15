"""
Converter Auto-Discovery
=========================
`core/converters/` paketindeki tüm somut `IConverter` alt sınıflarını
otomatik bulur ve bir registry'ye kaydeder. Yeni bir dönüşüm eklemenin
tek adımı: bu paket içine `IConverter`'ı implemente eden bir dosya
eklemek — `main_window.py` / `options_panel.py`'ye dokunmaya gerek
kalmaz (tak-çıkar mimari).

Nasıl çalışır:
  1. `core.converters` paketindeki her modülü import eder (pkgutil).
  2. Her modülün KENDİ TANIMLADIĞI somut (abstract olmayan) `IConverter`
     alt sınıflarını bulur (başka modülden import edilmiş sınıfları,
     örn. `BaseConverter`, tekrar saymamak için `__module__` kontrolü
     yapılır).
  3. Her birini örnekleyip registry'ye kaydeder.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import List, Type

import core.converters as _converters_pkg
from core.interfaces.converter_interface import IConverter, IConverterRegistry


def discover_converter_classes() -> List[Type[IConverter]]:
    """`core.converters` paketindeki tüm somut `IConverter` alt sınıflarını bulur."""
    classes: List[Type[IConverter]] = []

    for module_info in pkgutil.iter_modules(
        _converters_pkg.__path__, prefix=f"{_converters_pkg.__name__}."
    ):
        module = importlib.import_module(module_info.name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                obj.__module__ == module.__name__
                and issubclass(obj, IConverter)
                and obj is not IConverter
                and not inspect.isabstract(obj)
                and obj not in classes
            ):
                classes.append(obj)

    if not classes:
        # PyInstaller/Frozen ortamlarında dinamik keşif boş dönerse statik fallback
        _known_modules = [
            "core.converters.pptx_to_pdf",
            "core.converters.docx_to_pdf",
            "core.converters.pdf_to_docx",
            "core.converters.docx_to_txt",
            "core.converters.docx_to_odt",
            "core.converters.odt_to_docx",
            "core.converters.pdf_to_odt",
            "core.converters.pdf_to_jpg",
            "core.converters.pdf_to_png",
            "core.converters.pdf_to_txt",
            "core.converters.pdf_compress",
            "core.converters.pdf_split",
            "core.converters.pdf_merge",
            "core.converters.xlsx_to_pdf",
            "core.converters.xlsx_to_csv",
            "core.converters.csv_to_xlsx",
            "core.converters.xlsx_to_ods",
            "core.converters.ods_to_xlsx",
            "core.converters.jpg_to_pdf",
        ]
        for mod_name in _known_modules:
            try:
                module = importlib.import_module(mod_name)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        obj.__module__ == module.__name__
                        and issubclass(obj, IConverter)
                        and obj is not IConverter
                        and not inspect.isabstract(obj)
                        and obj not in classes
                    ):
                        classes.append(obj)
            except Exception:
                pass

    return classes


def register_all(registry: IConverterRegistry) -> None:
    """Bulunan tüm converter'ları örnekleyip registry'ye kaydeder."""
    for cls in discover_converter_classes():
        registry.register(cls())
