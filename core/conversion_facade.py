"""
Conversion Facade
===================
Backend'in gerçek, framework-agnostic giriş noktası. `core/` paketinin
geri kalanı gibi bu modül de hiç Qt import etmez — CLI, test veya
otomasyon senaryosunda PySide6 kurulu olmadan da kullanılabilir.

UI tarafı (`ui/adapters/qt_conversion_runner.py`), arayüzü bloklamadan
çalıştırmak için bu fonksiyonu bir `QThread` içinde çağırır.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional

from core.interfaces.converter_interface import (
    BatchConversionResult,
    ConversionOptions,
    ConversionResult,
    IConverter,
)


def convert_batch(
    files: List[Path],
    converter: IConverter,
    options: ConversionOptions,
    on_progress: Optional[Callable[[int, int], None]] = None,
    on_file_done: Optional[Callable[[ConversionResult], None]] = None,
    should_cancel: Optional[Callable[[], bool]] = None,
) -> BatchConversionResult:
    """
    Dosyaları sırayla dönüştürür. Tamamen senkron çalışır, Qt bağımlılığı yoktur.
    `should_cancel`, her adımda sorulur; `True` dönerse batch erken durur.
    """
    batch = BatchConversionResult()
    total = len(files)

    for i, file_path in enumerate(files):
        if should_cancel is not None and should_cancel():
            break

        result = converter.convert(file_path, options)
        batch.results.append(result)

        if on_file_done is not None:
            on_file_done(result)
        if on_progress is not None:
            on_progress(i + 1, total)

    return batch
