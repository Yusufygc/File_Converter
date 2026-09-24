"""
File List Model for QML
=======================
QAbstractListModel implementasyonu. QML ListView ile reaktif ve yüksek
performanslı dosya listesi veri bağlaması sağlar.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    Qt,
    QUrl,
    Signal,
)

from core.interfaces.converter_interface import ConversionResult
from core.utils.resource_helper import get_resource_path


_EXTENSION_ICONS = {
    ".pptx": "file_pptx",
    ".pdf": "file_pdf",
    ".jpg": "file_jpg",
    ".jpeg": "file_jpg",
    ".docx": "file_generic",
    ".xlsx": "file_generic",
    ".csv": "file_generic",
    ".odt": "file_generic",
    ".ods": "file_generic",
    ".txt": "file_generic",
    ".png": "file_generic",
}
_DEFAULT_ICON = "file_generic"
_ICON_DIR = "assets/icons"


def _icon_url_for(suffix: str) -> str:
    """Uzantıya göre ikon dosyasının QML dostu file:// URL'sini döner."""
    basename = _EXTENSION_ICONS.get(suffix.lower(), _DEFAULT_ICON)
    svg_path = Path(get_resource_path(f"{_ICON_DIR}/{basename}.svg"))
    if svg_path.exists():
        return QUrl.fromLocalFile(str(svg_path)).toString()
    png_path = Path(get_resource_path(f"{_ICON_DIR}/{basename}.png"))
    if png_path.exists():
        return QUrl.fromLocalFile(str(png_path)).toString()
    generic_svg = Path(get_resource_path(f"{_ICON_DIR}/file_generic.svg"))
    return QUrl.fromLocalFile(str(generic_svg)).toString()


class FileItem:
    """Model içindeki tek bir dosya öğesi."""

    def __init__(self, path: Path):
        self.path: Path = path
        self.name: str = path.name
        self.suffix: str = path.suffix.lower()
        self.size_bytes: int = path.stat().st_size if path.exists() else 0
        self.status: str = "idle"  # idle | converting | success | error
        self.error_message: str = ""
        self.elapsed_seconds: float = 0.0
        self.output_path: Optional[Path] = None
        self.page_count: int = 0
        self.icon_url: str = _icon_url_for(self.suffix)

    @property
    def size_str(self) -> str:
        size_kb = self.size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.1f} KB"
        return f"{size_kb / 1024:.1f} MB"

    @property
    def status_text(self) -> str:
        if self.status == "idle":
            return "Bekliyor"
        elif self.status == "converting":
            return "Dönüştürülüyor..."
        elif self.status == "success":
            return f"Tamam ({self.elapsed_seconds:.1f}s)"
        elif self.status == "error":
            return "Hata"
        return ""


class FileListModel(QAbstractListModel):
    """QML için dosya listesi modeli."""

    countChanged = Signal(int)

    NameRole = Qt.ItemDataRole.UserRole + 1
    PathRole = Qt.ItemDataRole.UserRole + 2
    SizeRole = Qt.ItemDataRole.UserRole + 3
    SuffixRole = Qt.ItemDataRole.UserRole + 4
    StatusRole = Qt.ItemDataRole.UserRole + 5
    StatusTextRole = Qt.ItemDataRole.UserRole + 6
    ErrorMessageRole = Qt.ItemDataRole.UserRole + 7
    ElapsedRole = Qt.ItemDataRole.UserRole + 8
    OutputPathRole = Qt.ItemDataRole.UserRole + 9
    PageCountRole = Qt.ItemDataRole.UserRole + 10
    IconUrlRole = Qt.ItemDataRole.UserRole + 11

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[FileItem] = []
        self._path_map: Dict[Path, int] = {}

    def roleNames(self) -> Dict[int, QByteArray]:
        return {
            self.NameRole: QByteArray(b"name"),
            self.PathRole: QByteArray(b"path"),
            self.SizeRole: QByteArray(b"sizeStr"),
            self.SuffixRole: QByteArray(b"suffix"),
            self.StatusRole: QByteArray(b"status"),
            self.StatusTextRole: QByteArray(b"statusText"),
            self.ErrorMessageRole: QByteArray(b"errorMessage"),
            self.ElapsedRole: QByteArray(b"elapsedSeconds"),
            self.OutputPathRole: QByteArray(b"outputPath"),
            self.PageCountRole: QByteArray(b"pageCount"),
            self.IconUrlRole: QByteArray(b"iconUrl"),
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._items)):
            return None

        item = self._items[index.row()]
        if role == self.NameRole:
            return item.name
        elif role == self.PathRole:
            return str(item.path)
        elif role == self.SizeRole:
            return item.size_str
        elif role == self.SuffixRole:
            return item.suffix
        elif role == self.StatusRole:
            return item.status
        elif role == self.StatusTextRole:
            return item.status_text
        elif role == self.ErrorMessageRole:
            return item.error_message
        elif role == self.ElapsedRole:
            return item.elapsed_seconds
        elif role == self.OutputPathRole:
            return str(item.output_path) if item.output_path else ""
        elif role == self.PageCountRole:
            return item.page_count
        elif role == self.IconUrlRole:
            return item.icon_url

        return None

    # ------------------------------------------------------------------ #
    #  Mutasyon Metodları                                                  #
    # ------------------------------------------------------------------ #

    def add_files(self, paths: List[Path]) -> int:
        """Yeni dosyaları ekler, yinelenenleri atlar."""
        new_paths = [p for p in paths if p not in self._path_map]
        if not new_paths:
            return 0

        start_row = len(self._items)
        end_row = start_row + len(new_paths) - 1

        self.beginInsertRows(QModelIndex(), start_row, end_row)
        for p in new_paths:
            item = FileItem(p)
            self._items.append(item)
            self._path_map[p] = len(self._items) - 1
        self.endInsertRows()

        self.countChanged.emit(len(self._items))
        return len(new_paths)

    def remove_at(self, row: int) -> bool:
        """Belirtilen indeksteki dosyayı kaldırır."""
        if not (0 <= row < len(self._items)):
            return False

        self.beginRemoveRows(QModelIndex(), row, row)
        removed_item = self._items.pop(row)
        del self._path_map[removed_item.path]
        # Kalan öğelerin map indekslerini güncelle
        for i in range(row, len(self._items)):
            self._path_map[self._items[i].path] = i
        self.endRemoveRows()

        self.countChanged.emit(len(self._items))
        return True

    def remove_paths(self, paths: List[Path]) -> int:
        """Verilen yollara ait dosyaları kaldırır."""
        removed_count = 0
        for p in paths:
            if p in self._path_map:
                row = self._path_map[p]
                self.remove_at(row)
                removed_count += 1
        return removed_count

    def clear(self) -> None:
        """Tüm dosyaları temizler."""
        if not self._items:
            return
        self.beginResetModel()
        self._items.clear()
        self._path_map.clear()
        self.endResetModel()
        self.countChanged.emit(0)

    def all_paths(self) -> List[Path]:
        """Listedeki tüm dosya yollarını döner."""
        return [item.path for item in self._items]

    def count(self) -> int:
        return len(self._items)

    # ------------------------------------------------------------------ #
    #  Durum Güncellemeleri                                               #
    # ------------------------------------------------------------------ #

    def mark_converting(self, path: Path) -> None:
        if path in self._path_map:
            row = self._path_map[path]
            item = self._items[row]
            item.status = "converting"
            idx = self.index(row, 0)
            self.dataChanged.emit(idx, idx, [self.StatusRole, self.StatusTextRole])

    def mark_result(self, result: ConversionResult) -> None:
        if result.source_path in self._path_map:
            row = self._path_map[result.source_path]
            item = self._items[row]
            if result.success:
                item.status = "success"
                item.elapsed_seconds = result.elapsed_seconds
                item.output_path = result.output_path
                item.page_count = result.page_count
            else:
                item.status = "error"
                item.error_message = result.error_message or "Bilinmeyen hata"

            idx = self.index(row, 0)
            self.dataChanged.emit(
                idx,
                idx,
                [
                    self.StatusRole,
                    self.StatusTextRole,
                    self.ErrorMessageRole,
                    self.ElapsedRole,
                    self.OutputPathRole,
                    self.PageCountRole,
                ],
            )

    def reset_statuses(self) -> None:
        """Tüm dosya durumlarını 'idle' (Bekliyor) yapar."""
        for item in self._items:
            item.status = "idle"
            item.error_message = ""
            item.elapsed_seconds = 0.0
            item.output_path = None
            item.page_count = 0

        if self._items:
            first_idx = self.index(0, 0)
            last_idx = self.index(len(self._items) - 1, 0)
            self.dataChanged.emit(
                first_idx,
                last_idx,
                [
                    self.StatusRole,
                    self.StatusTextRole,
                    self.ErrorMessageRole,
                    self.ElapsedRole,
                    self.OutputPathRole,
                ],
            )
