"""
Drop Zone Widget
================
Dosya sürükle-bırak alanı. SRP: sadece dosya alımından sorumlu.
"""

from pathlib import Path
from typing import List

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


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
        icon_label = QLabel("📂")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 28px; background: transparent; border: none;")

        # Primary text
        self._primary_label = QLabel("Dosyaları buraya sürükleyin veya tıklayın")
        self._primary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._primary_label.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: #ECEEF5; background: transparent; border: none;"
        )

        # Secondary text
        ext_list = "  ·  ".join(e.upper() for e in self._accepted)
        secondary = QLabel(ext_list)
        secondary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        secondary.setStyleSheet(
            f"font-size: 11px; color: #525A78; background: transparent; border: none; letter-spacing: 0.5px;"
        )

        layout.addWidget(icon_label)
        layout.addWidget(self._primary_label)
        layout.addWidget(secondary)

    # ------------------------------------------------------------------ #
    #  Drag & Drop Events                                                  #
    # ------------------------------------------------------------------ #

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            paths = [Path(u.toLocalFile()) for u in event.mimeData().urls()]
            if any(p.suffix.lower() in self._accepted for p in paths):
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

        paths = [
            Path(u.toLocalFile())
            for u in event.mimeData().urls()
            if Path(u.toLocalFile()).suffix.lower() in self._accepted
        ]
        if paths:
            self.files_dropped.emit(paths)
        event.acceptProposedAction()

    def mousePressEvent(self, event) -> None:
        # Tıklama ile de dosya seçilebilsin (parent MainWindow handle eder)
        self.files_dropped.emit([])  # boş liste → dosya diyaloğu aç
        super().mousePressEvent(event)

    def _refresh_style(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)