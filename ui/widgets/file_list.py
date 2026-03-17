"""
File List Widget
================
Eklenen dosyaları ve dönüşüm durumlarını listeler.
SRP: Yalnızca liste gösterimi ve dosya yönetiminden sorumlu.
"""

from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QWidget,
)

from core.interfaces.converter_interface import ConversionResult
from ui.styles.theme import PALETTE


class FileItemWidget(QWidget):
    """Her dosya için özel liste satırı widget'ı."""

    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(10)

        # Durum ikonu
        self._icon = QLabel("📄")
        self._icon.setFixedWidth(22)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet("font-size: 14px; background: transparent;")

        # Dosya adı
        self._name_label = QLabel(self.file_path.name)
        self._name_label.setStyleSheet(
            "color: #ECEEF5; font-size: 13px; font-weight: 500; background: transparent;"
        )
        self._name_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        # Boyut
        size_kb = self.file_path.stat().st_size / 1024 if self.file_path.exists() else 0
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        self._size_label = QLabel(size_str)
        self._size_label.setFixedWidth(64)
        self._size_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._size_label.setStyleSheet(
            "color: #525A78; font-size: 11px; background: transparent;"
        )

        # Durum
        self._status_label = QLabel("Bekliyor")
        self._status_label.setFixedWidth(110)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._status_label.setStyleSheet(
            "color: #525A78; font-size: 11px; background: transparent;"
        )

        layout.addWidget(self._icon)
        layout.addWidget(self._name_label)
        layout.addWidget(self._size_label)
        layout.addWidget(self._status_label)

    def set_converting(self) -> None:
        self._icon.setText("⏳")
        self._status_label.setText("Dönüştürülüyor...")
        self._status_label.setStyleSheet(
            "color: #F5A623; font-size: 11px; background: transparent; font-weight: 600;"
        )

    def set_result(self, result: ConversionResult) -> None:
        if result.success:
            self._icon.setText("✅")
            elapsed = f"{result.elapsed_seconds:.1f}s"
            self._status_label.setText(f"✓ Tamam  {elapsed}")
            self._status_label.setStyleSheet(
                "color: #34D27A; font-size: 11px; background: transparent; font-weight: 600;"
            )
        else:
            self._icon.setText("❌")
            self._status_label.setText("Hata")
            self._status_label.setStyleSheet(
                "color: #F05252; font-size: 11px; background: transparent; font-weight: 600;"
            )
            self._name_label.setToolTip(result.error_message)


class FileListWidget(QWidget):
    """
    Dosya listesi container'ı.
    Sinyal aracılığıyla seçim değişikliklerini bildirir.
    """

    selection_changed = Signal(int)  # seçili sayı
    list_changed = Signal(int)       # toplam dosya sayısı

    def __init__(self, parent=None):
        super().__init__(parent)
        self._path_to_item: Dict[Path, QListWidgetItem] = {}
        self._path_to_widget: Dict[Path, FileItemWidget] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._list.itemSelectionChanged.connect(
            lambda: self.selection_changed.emit(len(self._list.selectedItems()))
        )
        layout.addWidget(self._list)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def add_files(self, paths: List[Path]) -> None:
        added = 0
        for path in paths:
            if path not in self._path_to_item:
                item = QListWidgetItem(self._list)
                widget = FileItemWidget(path)
                item.setSizeHint(widget.sizeHint())
                self._list.addItem(item)
                self._list.setItemWidget(item, widget)
                self._path_to_item[path] = item
                self._path_to_widget[path] = widget
                added += 1

        if added:
            self.list_changed.emit(len(self._path_to_item))

    def remove_selected(self) -> None:
        for item in self._list.selectedItems():
            row = self._list.row(item)
            # Ters mapping için path bul
            path = next(
                (p for p, i in self._path_to_item.items() if i is item), None
            )
            if path:
                del self._path_to_item[path]
                del self._path_to_widget[path]
            self._list.takeItem(row)
        self.list_changed.emit(len(self._path_to_item))

    def clear_all(self) -> None:
        self._list.clear()
        self._path_to_item.clear()
        self._path_to_widget.clear()
        self.list_changed.emit(0)

    def all_paths(self) -> List[Path]:
        return list(self._path_to_item.keys())

    def count(self) -> int:
        return len(self._path_to_item)

    def mark_converting(self, path: Path) -> None:
        widget = self._path_to_widget.get(path)
        if widget:
            widget.set_converting()

    def mark_result(self, result: ConversionResult) -> None:
        widget = self._path_to_widget.get(result.source_path)
        if widget:
            widget.set_result(result)

    def reset_statuses(self) -> None:
        for widget in self._path_to_widget.values():
            widget._icon.setText("📄")
            widget._status_label.setText("Bekliyor")