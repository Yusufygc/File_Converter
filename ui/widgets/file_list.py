"""
File List Widget
================
Eklenen dosyaları ve dönüşüm durumlarını listeler.
SRP: Yalnızca liste gösterimi ve dosya yönetiminden sorumlu.
"""

from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QWidget,
)

from core.interfaces.converter_interface import ConversionResult
from ui.styles.theme import PALETTE
from core.utils.resource_helper import get_resource_path
from ui.icon_map import icon_path_for


class FileItemWidget(QWidget):
    """Her dosya için özel liste satırı widget'ı."""

    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFixedHeight(44) # Kesin yükseklik, list item ile tam örtüşmeli
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(10)

        # Durum ikonu — dosya uzantısına göre (bkz. ui/icon_map.py)
        self._icon = QLabel()
        icon_path = icon_path_for(self.file_path.suffix)
        self._icon.setPixmap(QIcon(icon_path).pixmap(20, 20))
        self._icon.setFixedWidth(24)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet("background: transparent;")

        # Dosya adı
        self._name_label = QLabel(self.file_path.name)
        self._name_label.setObjectName("fileNameLabel")
        self._name_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._name_label.setMinimumWidth(50)  # En azından bir kısmı görünsün

        # Boyut
        size_kb = self.file_path.stat().st_size / 1024 if self.file_path.exists() else 0
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        self._size_label = QLabel(size_str)
        self._size_label.setObjectName("fileSizeLabel")
        self._size_label.setFixedWidth(64)
        self._size_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Durum — dinamik (bekliyor/dönüştürülüyor/başarılı/hatalı), tema
        # değişiminde retheme() ile PALETTE'ten yeniden okunur.
        self._status_kind = "idle"
        self._status_label = QLabel("Bekliyor")
        self._status_label.setFixedWidth(110)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._apply_status_style()

        layout.addWidget(self._icon)
        layout.addWidget(self._name_label)
        layout.addWidget(self._size_label)
        layout.addWidget(self._status_label)

    def _apply_status_style(self) -> None:
        """`self._status_kind`'e göre durum label'ını güncel PALETTE ile boyar."""
        styles = {
            "idle":       (PALETTE['text_muted'], 400),
            "converting": (PALETTE['warning'],    600),
            "success":    (PALETTE['success'],    600),
            "error":      (PALETTE['error'],      600),
        }
        color, weight = styles[self._status_kind]
        self._status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; background: transparent; font-weight: {weight};"
        )

    def retheme(self) -> None:
        """Tema değiştiğinde son durumu güncel PALETTE ile yeniden boyar."""
        self._apply_status_style()

    def set_converting(self) -> None:
        self._status_kind = "converting"
        self._status_label.setText("Dönüştürülüyor...")
        self._apply_status_style()

    def set_result(self, result: ConversionResult) -> None:
        if result.success:
            icon_path = get_resource_path("assets/icons/success.svg")
            self._icon.setPixmap(QIcon(icon_path).pixmap(20, 20))
            elapsed = f"{result.elapsed_seconds:.1f}s"
            self._status_kind = "success"
            self._status_label.setText(f"✓ Tamam  {elapsed}")
            self._apply_status_style()
        else:
            icon_path = get_resource_path("assets/icons/error.svg")
            self._icon.setPixmap(QIcon(icon_path).pixmap(20, 20))
            self._status_kind = "error"
            self._status_label.setText("Hata")
            self._apply_status_style()
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
        layout = QVBoxLayout(self) # QVBoxLayout daha iyi container yönetimi sağlar
        layout.setContentsMargins(0, 0, 0, 0)

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._list.itemSelectionChanged.connect(
            lambda: self.selection_changed.emit(len(self._list.selectedItems()))
        )
        self.setMinimumHeight(200) # Liste için makul bir alan ayır
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
                item.setSizeHint(QSize(0, 44)) # Kesin yükseklik, kaymaları önler
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
            icon_path = icon_path_for(widget.file_path.suffix)
            widget._icon.setPixmap(QIcon(icon_path).pixmap(20, 20))
            widget._status_kind = "idle"
            widget._status_label.setText("Bekliyor")
            widget._apply_status_style()

    def retheme(self) -> None:
        """Tema değiştiğinde her dosya satırının rengini günceller."""
        for widget in self._path_to_widget.values():
            widget.retheme()