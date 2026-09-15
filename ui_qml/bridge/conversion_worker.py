"""
QML Conversion Workers
======================
QThread türevi arka plan işçileri. `core/conversion_facade.py`'ın senkron
metodlarını UI thread'ini dondurmadan çalıştırır.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QObject, QThread, Signal

from core.conversion_facade import convert_batch, convert_batch_parallel, merge_files
from core.interfaces.converter_interface import (
    BatchConversionResult,
    ConversionOptions,
    ConversionResult,
    IConverter,
)
from core.interfaces.merge_interface import IMergeConverter


class QmlConversionWorker(QThread):
    """Toplu dosya dönüştürme işçisi."""

    progress = Signal(int, int)               # (tamamlanan, toplam)
    file_completed = Signal(object)           # ConversionResult
    batch_completed = Signal(object)          # BatchConversionResult

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


class QmlMergeWorker(QThread):
    """Birleştirme (N:1) işçisi."""

    merge_completed = Signal(object)  # BatchConversionResult

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
        """Birleştirme bölünemez; no-op."""
        pass
