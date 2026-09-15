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

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, List, Optional

from core.interfaces.converter_interface import (
    BatchConversionResult,
    ConversionOptions,
    ConversionResult,
    IConverter,
)
from core.interfaces.merge_interface import IMergeConverter


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


def convert_batch_parallel(
    files: List[Path],
    converter: IConverter,
    options: ConversionOptions,
    on_progress: Optional[Callable[[int, int], None]] = None,
    on_file_done: Optional[Callable[[ConversionResult], None]] = None,
    should_cancel: Optional[Callable[[], bool]] = None,
    max_workers: int = 4,
) -> BatchConversionResult:
    """
    `convert_batch()`'in paralel sürümü — yalnızca `converter.is_parallel_safe`
    `True` olan (dış süreç/paylaşımlı durum kullanmayan, örn. PyMuPDF
    tabanlı) converter'lar için kullanılmalıdır (bkz. `IConverter.is_parallel_safe`).

    İptal en iyi çaba (best-effort) düzeyindedir: `should_cancel()` `True`
    olduğunda henüz BAŞLAMAMIŞ `Future`'lar iptal edilir, hâlihazırda
    çalışmakta olanlar kesilmeden tamamlanır — bu, sıralı `convert_batch()`'in
    dosyalar-arası iptal granularity'siyle tutarlıdır.
    """
    batch = BatchConversionResult()
    total = len(files)
    completed = 0
    lock = threading.Lock()
    workers = max(1, min(max_workers, os.cpu_count() or max_workers))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(converter.convert, f, options): f for f in files}

        for future in as_completed(futures):
            if should_cancel is not None and should_cancel():
                for pending in futures:
                    if not pending.done():
                        pending.cancel()

            try:
                result = future.result()
            except Exception:
                continue  # .cancel() edilmiş (henüz başlamamış) future'lar için

            with lock:
                batch.results.append(result)
                completed += 1
                current = completed

            if on_file_done is not None:
                on_file_done(result)
            if on_progress is not None:
                on_progress(current, total)

    return batch


def merge_files(
    converter: IMergeConverter,
    source_paths: List[Path],
    options: ConversionOptions,
) -> ConversionResult:
    """
    Birden fazla dosyayı TEK bir çıktıda birleştirir. İnce bir sarmalayıcı
    — asıl mantık `converter.convert_many()`'de (bkz. `MergeCapableConverter`,
    `core/converters/base.py`); bu fonksiyon `core/`'un tek-giriş-noktası
    ilkesini korumak için var (UI, converter'ı doğrudan çağırmak yerine
    buradan geçer — `convert_batch()` ile simetrik).
    """
    return converter.convert_many(source_paths, options)
