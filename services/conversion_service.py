"""
Conversion Service
==================
SRP: Dönüşüm iş akışını orkestre eder.
DIP: Concrete converter'lara değil IConverter soyutlamasına bağımlı.
"""

from pathlib import Path
from typing import List, Callable, Optional

from PySide6.QtCore import QThread, Signal, QObject

from core.interfaces.converter_interface import (
    IConverter,
    IConverterRegistry,
    ConversionOptions,
    ConversionResult,
    BatchConversionResult,
)


class ConversionWorker(QThread):
    """
    Dönüşümleri arka plan thread'inde çalıştırır.
    UI thread'i asla bloklamaz.
    """

    progress = Signal(int, int)               # (tamamlanan, toplam)
    file_completed = Signal(ConversionResult) # her dosya bitince
    batch_completed = Signal(BatchConversionResult)
    error_occurred = Signal(str)

    def __init__(
        self,
        files: List[Path],
        converter: IConverter,
        options: ConversionOptions,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._files = files
        self._converter = converter
        self._options = options
        self._cancelled = False

    def run(self) -> None:
        batch = BatchConversionResult()
        total = len(self._files)

        for i, file_path in enumerate(self._files):
            if self._cancelled:
                break

            result = self._converter.convert(file_path, self._options)
            batch.results.append(result)
            self.file_completed.emit(result)
            self.progress.emit(i + 1, total)

        self.batch_completed.emit(batch)

    def cancel(self) -> None:
        self._cancelled = True


class ConversionService:
    """
    Yüksek seviyeli dönüşüm servis katmanı.
    UI kodundan converter detaylarını izole eder.
    """

    def __init__(self, registry: IConverterRegistry):
        self._registry = registry
        self._active_worker: Optional[ConversionWorker] = None

    def find_converter(
        self,
        source_ext: str,
        target_ext: str,
    ) -> Optional[IConverter]:
        return self._registry.get(source_ext, target_ext)

    def start_batch_conversion(
        self,
        files: List[Path],
        converter: IConverter,
        options: ConversionOptions,
        on_progress: Callable[[int, int], None],
        on_file_done: Callable[[ConversionResult], None],
        on_batch_done: Callable[[BatchConversionResult], None],
    ) -> ConversionWorker:
        worker = ConversionWorker(files, converter, options)
        worker.progress.connect(on_progress)
        worker.file_completed.connect(on_file_done)
        worker.batch_completed.connect(on_batch_done)
        self._active_worker = worker
        worker.start()
        return worker

    def cancel(self) -> None:
        if self._active_worker and self._active_worker.isRunning():
            self._active_worker.cancel()
