"""
Qt Conversion Runner
=====================
`core/conversion_facade.py`'daki senkron, Qt'siz `convert_batch()`'i bir
`QThread` içinde çalıştırır — UI thread'i asla bloklamaz.

Önceden `services/conversion_service.py` içindeydi. Backend/frontend
ayrımını fiziksel dizin yapısıyla da netleştirmek için buraya taşındı:
`core/` artık hiçbir Qt importu barındırmaz, Qt'ye bağımlı her şey
`ui/` altında yaşar.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional, Union

from PySide6.QtCore import QObject, QThread, Signal

from core.conversion_facade import convert_batch, convert_batch_parallel, merge_files
from core.interfaces.converter_interface import (
    BatchConversionResult,
    ConversionOptions,
    ConversionResult,
    IConverter,
    IConverterRegistry,
)
from core.interfaces.merge_interface import IMergeConverter


class ConversionWorker(QThread):
    """Dönüşümleri arka plan thread'inde çalıştırır."""

    progress = Signal(int, int)               # (tamamlanan, toplam)
    file_completed = Signal(ConversionResult)  # her dosya bitince
    batch_completed = Signal(BatchConversionResult)

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
        # Yalnızca dış süreç/paylaşımlı durum kullanmayan (örn. PyMuPDF
        # tabanlı) converter'lar paralel çalıştırılır — bkz.
        # IConverter.is_parallel_safe ve docs/wiki/libreoffice-motoru.md.
        convert_fn = (
            convert_batch_parallel if self._converter.is_parallel_safe else convert_batch
        )
        batch = convert_fn(
            self._files,
            self._converter,
            self._options,
            on_progress=self.progress.emit,
            on_file_done=self.file_completed.emit,
            should_cancel=lambda: self._cancelled,
        )
        self.batch_completed.emit(batch)

    def cancel(self) -> None:
        self._cancelled = True


class MergeWorker(QThread):
    """
    Birleştirme (`convert_many`) işlemini arka plan thread'inde çalıştırır.
    Tek bir `ConversionResult` üretir ama bunu `BatchConversionResult(results=[result])`'a
    sararak yayınlar — bu sayede `MainWindow._on_batch_done()` ve
    `SummaryDialog` hiç değişmeden (zaten `List[ConversionResult]`
    bekledikleri için) çalışmaya devam eder.
    """

    merge_completed = Signal(BatchConversionResult)

    def __init__(
        self,
        files: List[Path],
        converter: IMergeConverter,
        options: ConversionOptions,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._files = files
        self._converter = converter
        self._options = options

    def run(self) -> None:
        result = merge_files(self._converter, self._files, self._options)
        self.merge_completed.emit(BatchConversionResult(results=[result]))

    def cancel(self) -> None:
        """
        Birleştirme tek parça bir işlemdir, yarıda kesilebilir değil —
        bu no-op yalnızca `QtConversionRunner.cancel()`'ın (aktif worker
        türünden bağımsız çağırdığı) `.cancel()` çağrısının hata
        fırlatmamasını sağlar. İptal isteği sessizce görmezden gelinir.
        """
        pass


class QtConversionRunner:
    """
    UI'ın kullandığı yüksek seviyeli servis. Converter detaylarını
    UI kodundan izole eder; asıl dönüşüm mantığı `core.conversion_facade`'da.
    """

    def __init__(self, registry: IConverterRegistry):
        self._registry = registry
        self._active_worker: Optional[Union[ConversionWorker, MergeWorker]] = None

    def find_converter(self, source_ext: str, target_ext: str) -> Optional[IConverter]:
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

    def start_merge_conversion(
        self,
        files: List[Path],
        converter: IMergeConverter,
        options: ConversionOptions,
        on_done: Callable[[BatchConversionResult], None],
    ) -> MergeWorker:
        worker = MergeWorker(files, converter, options)
        worker.merge_completed.connect(on_done)
        self._active_worker = worker
        worker.start()
        return worker

    def cancel(self) -> None:
        if self._active_worker and self._active_worker.isRunning():
            self._active_worker.cancel()
