"""
Conversion Summary Dialog
=========================
Toplu dönüşüm sonucunu özetler. SRP: yalnızca rapor gösterimi.
"""

import subprocess
import platform
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from core.interfaces.converter_interface import BatchConversionResult
from ui.styles.theme import PALETTE


class SummaryDialog(QDialog):
    """Dönüşüm tamamlandığında detaylı özet sunar."""

    def __init__(self, result: BatchConversionResult, parent=None):
        super().__init__(parent)
        self._result = result
        self.setWindowTitle("Dönüşüm Tamamlandı")
        self.setMinimumSize(520, 400)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 20)

        # ── Başlık ─────────────────────────────────────────────────
        title = QLabel("Dönüşüm Özeti")
        title.setObjectName("heading")

        # ── İstatistikler ──────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        for label, value, color in [
            ("Toplam", str(self._result.total), PALETTE["text_primary"]),
            ("Başarılı", str(self._result.success_count), PALETTE["success"]),
            ("Hatalı", str(self._result.failure_count), PALETTE["error"]),
        ]:
            card = self._stat_card(label, value, color)
            stats_row.addWidget(card)

        # ── Detay Listesi ──────────────────────────────────────────
        detail_label = QLabel("Detaylar:")
        detail_label.setStyleSheet(
            f"color: {PALETTE['text_secondary']}; font-size: 12px;"
        )

        self._list = QListWidget()
        self._list.setStyleSheet(
            f"QListWidget {{ background: {PALETTE['bg_elevated']}; "
            f"border: 1px solid {PALETTE['border']}; border-radius: 8px; }}"
        )

        for res in self._result.results:
            icon = "✅" if res.success else "❌"
            text = f"{icon}  {res.file_name}"
            if res.success and res.output_path:
                text += f"  →  {res.output_path.name}  ({res.elapsed_seconds:.1f}s)"
                if res.page_count > 1:
                    text += f"  —  {res.page_count} sayfa"
            else:
                text += f"  —  {res.error_message[:80]}"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, res)
            if res.success:
                item.setForeground(QColor(PALETTE["text_primary"]))
            else:
                item.setForeground(QColor(PALETTE["error"]))
            self._list.addItem(item)

        # ── Butonlar ───────────────────────────────────────────────
        btn_row = QHBoxLayout()

        open_btn = QPushButton("📁  Klasörü Aç")
        open_btn.clicked.connect(self._open_output_folder)

        close_btn = QPushButton("Kapat")
        close_btn.setObjectName("primaryBtn")
        close_btn.clicked.connect(self.accept)

        btn_row.addWidget(open_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)

        layout.addWidget(title)
        layout.addLayout(stats_row)
        layout.addWidget(detail_label)
        layout.addWidget(self._list)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _stat_card(self, label: str, value: str, color: str) -> QLabel:
        card = QLabel(f"<b style='font-size:22px;color:{color}'>{value}</b><br>"
                      f"<small style='color:{PALETTE['text_muted']}'>{label}</small>")
        card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setStyleSheet(
            f"background: {PALETTE['bg_elevated']}; border: 1px solid {PALETTE['border']};"
            f"border-radius: 10px; padding: 12px 24px;"
        )
        return card

    def _open_output_folder(self) -> None:
        # Başarılı ilk çıktıyı bul
        for res in self._result.results:
            if res.success and res.output_path:
                folder = str(res.output_path.parent)
                system = platform.system()
                if system == "Windows":
                    subprocess.Popen(["explorer", folder])
                elif system == "Darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
                break