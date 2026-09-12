"""
Drop Zone Widget
================
Dosya sürükle-bırak alanı. SRP: sadece dosya alımından sorumlu.
"""

from pathlib import Path
from typing import List

from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.styles.theme import PALETTE
from core.utils.resource_helper import get_resource_path
from ui.file_discovery import collect_files


class DropZoneWidget(QWidget):
    """
    Kullanıcının dosyaları sürükleyip bırakabileceği alan.
    Geçerli uzantı filtresi dışındaki dosyaları reddeder.
    """

    files_dropped = Signal(list)  # List[Path]

    def __init__(self, accepted_extensions: List[str], parent=None):
        super().__init__(parent)
        self._accepted = {ext.lower() for ext in accepted_extensions}
        self._setup_ui()
        self.setAcceptDrops(True)

    # ------------------------------------------------------------------ #
    #  UI Setup                                                            #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        self.setObjectName("dropZone")
        self.setMinimumHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        # Icon
        icon_label = QLabel()
        icon_pixmap = QIcon(get_resource_path("assets/icons/app_icon.svg")).pixmap(48, 48)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")

        # Primary text
        self._primary_label = QLabel("Dosyaları veya bir klasörü buraya sürükleyin ya da tıklayın")
        self._primary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._primary_label.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {PALETTE['text_primary']}; background: transparent; border: none;"
        )

        # Secondary text
        ext_list = "  ·  ".join(e.upper() for e in sorted(self._accepted))
        self._ext_label = QLabel(ext_list)
        self._ext_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ext_label.setStyleSheet(
            f"font-size: 11px; color: {PALETTE['text_muted']}; background: transparent; border: none; letter-spacing: 0.5px;"
        )

        layout.addWidget(icon_label)
        layout.addWidget(self._primary_label)
        layout.addWidget(self._ext_label)

    # ------------------------------------------------------------------ #
    #  Drag & Drop Events                                                  #
    # ------------------------------------------------------------------ #

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            paths = [Path(u.toLocalFile()) for u in event.mimeData().urls()]
            if any(p.is_dir() or p.suffix.lower() in self._accepted for p in paths):
                event.acceptProposedAction()
                self.setObjectName("dropZoneActive")
                self._refresh_style()
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self.setObjectName("dropZone")
        self._refresh_style()

    def dropEvent(self, event: QDropEvent) -> None:
        self.setObjectName("dropZone")
        self._refresh_style()

        paths: List[Path] = []
        for u in event.mimeData().urls():
            p = Path(u.toLocalFile())
            if p.is_dir():
                paths.extend(collect_files(p, self._accepted))
            elif p.suffix.lower() in self._accepted:
                paths.append(p)

        if paths:
            self.files_dropped.emit(paths)
        event.acceptProposedAction()

    def mousePressEvent(self, event) -> None:
        # Tıklama ile de dosya seçilebilsin (parent MainWindow handle eder)
        self.files_dropped.emit([])  # boş liste → dosya diyaloğu aç
        super().mousePressEvent(event)

    def set_accepted_extensions(self, extensions: List[str]) -> None:
        """Kabul edilen dosya uzantılarını günceller ve etiketi yeniler."""
        self._accepted = {ext.lower() for ext in extensions}
        ext_list = "  ·  ".join(e.upper() for e in sorted(self._accepted))
        self._ext_label.setText(ext_list)

    def _refresh_style(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)