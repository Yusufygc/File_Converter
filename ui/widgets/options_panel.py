"""
Options Panel Widget
====================
Dönüşüm seçeneklerini sunar. SRP: yalnızca seçenek toplama.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.interfaces.converter_interface import ConversionOptions
from core.converters.pptx_to_pdf import ConversionEngine
from ui.styles.theme import PALETTE


class OptionsPanelWidget(QWidget):
    """Kullanıcı seçeneklerini toplayan panel."""

    options_changed = Signal()
    engine_changed = Signal(object)  # ConversionEngine

    def __init__(self, parent=None):
        super().__init__(parent)
        self._output_dir: Optional[Path] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ── Motor Seçimi ───────────────────────────────────────────
        engine_group = QGroupBox("Dönüşüm Motoru")
        engine_group.setStyleSheet(
            f"QGroupBox {{ background-color: {PALETTE['bg_card']}; }}"
            f"QGroupBox::title {{ background-color: {PALETTE['bg_card']}; }}"
        )
        engine_layout = QHBoxLayout(engine_group)
        engine_layout.setSpacing(12)

        engine_label = QLabel("Motor:")
        engine_label.setStyleSheet(
            f"color: {PALETTE['text_secondary']}; background: transparent;"
        )

        self._engine_combo = QComboBox()
        self._engine_combo.setFixedWidth(200)
        self._engine_combo.setToolTip(
            "Hangi program kullanılarak dönüşüm yapılacağını seçin.\n"
            "Otomatik: Önce MS Office, bulunamazsa LibreOffice denenir."
        )
        self._engine_combo.currentIndexChanged.connect(self._on_engine_changed)

        self._engine_status = QLabel("")
        self._engine_status.setStyleSheet(
            f"color: {PALETTE['text_muted']}; font-size: 11px; background: transparent;"
        )

        engine_layout.addWidget(engine_label)
        engine_layout.addWidget(self._engine_combo)
        engine_layout.addWidget(self._engine_status)
        engine_layout.addStretch()

        # ── Çıktı Klasörü ─────────────────────────────────────────
        out_group = QGroupBox("Çıktı Konumu")
        out_group.setStyleSheet(
            f"QGroupBox {{ background-color: {PALETTE['bg_card']}; }}"
            f"QGroupBox::title {{ background-color: {PALETTE['bg_card']}; }}"
        )
        out_layout = QHBoxLayout(out_group)
        out_layout.setSpacing(8)

        self._out_edit = QLineEdit()
        self._out_edit.setPlaceholderText("Kaynak dosyayla aynı klasör (varsayılan)")
        self._out_edit.setReadOnly(True)
        self._out_edit.setStyleSheet(
            f"background: {PALETTE['bg_elevated']}; border: 1px solid {PALETTE['border']};"
            f"border-radius: 8px; padding: 6px 10px; color: {PALETTE['text_secondary']};"
        )

        browse_btn = QPushButton("Gözat...")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse_output_dir)

        clear_btn = QPushButton("✕")
        clear_btn.setFixedWidth(32)
        clear_btn.setToolTip("Varsayılana dön")
        clear_btn.clicked.connect(self._clear_output_dir)

        out_layout.addWidget(self._out_edit)
        out_layout.addWidget(browse_btn)
        out_layout.addWidget(clear_btn)

        # ── DPI Seçimi ─────────────────────────────────────────────
        dpi_group = QGroupBox("Kalite Ayarları")
        dpi_group.setStyleSheet(
            f"QGroupBox {{ background-color: {PALETTE['bg_card']}; }}"
            f"QGroupBox::title {{ background-color: {PALETTE['bg_card']}; }}"
        )
        dpi_layout = QHBoxLayout(dpi_group)
        dpi_layout.setSpacing(16)

        dpi_label = QLabel("DPI:")
        dpi_label.setStyleSheet(
            f"color: {PALETTE['text_secondary']}; background: transparent;"
        )

        self._dpi_spin = QSpinBox()
        self._dpi_spin.setRange(72, 600)
        self._dpi_spin.setValue(150)
        self._dpi_spin.setSuffix(" dpi")
        self._dpi_spin.setFixedWidth(100)
        self._dpi_spin.setToolTip(
            "Yalnızca LibreOffice motorunda etkilidir.\n"
            "MS Office kendi kalite ayarlarını kullanır."
        )
        self._dpi_spin.valueChanged.connect(self.options_changed)

        self._overwrite_check = QCheckBox("Mevcut dosyaların üzerine yaz")
        self._overwrite_check.setChecked(True)
        self._overwrite_check.stateChanged.connect(self.options_changed)

        dpi_layout.addWidget(dpi_label)
        dpi_layout.addWidget(self._dpi_spin)
        dpi_layout.addSpacing(16)
        dpi_layout.addWidget(self._overwrite_check)
        dpi_layout.addStretch()

        layout.addWidget(engine_group)
        layout.addWidget(out_group)
        layout.addWidget(dpi_group)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def populate_engines(
        self,
        available: List[ConversionEngine],
        active: ConversionEngine,
    ) -> None:
        """
        Motor ComboBox'ını mevcut motorlarla doldurur.
        MainWindow tarafından PptxToPdfConverter sorgulandıktan sonra çağrılır.
        """
        _LABELS = {
            ConversionEngine.MS_OFFICE:   "Microsoft Office",
            ConversionEngine.LIBREOFFICE: "LibreOffice",
        }

        self._engine_combo.blockSignals(True)
        self._engine_combo.clear()

        # "Otomatik" seçeneği her zaman başta
        self._engine_combo.addItem("🔄  Otomatik (önerilen)", userData=None)

        for engine in [ConversionEngine.MS_OFFICE, ConversionEngine.LIBREOFFICE]:
            label = _LABELS[engine]
            if engine in available:
                self._engine_combo.addItem(f"✅  {label}", userData=engine)
            else:
                self._engine_combo.addItem(f"❌  {label} (kurulu değil)", userData=engine)
                # Mevcut olmayan motoru disable et
                idx = self._engine_combo.count() - 1
                item = self._engine_combo.model().item(idx)
                if item:
                    item.setEnabled(False)

        self._engine_combo.blockSignals(False)
        self._update_engine_status(active)

    def get_options(self) -> ConversionOptions:
        return ConversionOptions(
            output_dir=self._output_dir,
            dpi=self._dpi_spin.value(),
            overwrite_existing=self._overwrite_check.isChecked(),
        )

    def selected_engine(self) -> Optional[ConversionEngine]:
        """None → Otomatik, değer varsa o motor."""
        return self._engine_combo.currentData()

    # ------------------------------------------------------------------ #
    #  Private Slots                                                       #
    # ------------------------------------------------------------------ #

    def _on_engine_changed(self, _index: int) -> None:
        engine = self._engine_combo.currentData()
        self.engine_changed.emit(engine)
        # DPI seçeneği sadece LibreOffice'te anlamlı
        is_lo = engine == ConversionEngine.LIBREOFFICE or engine is None
        self._dpi_spin.setEnabled(True)  # her zaman göster, tooltip açıklar

    def _update_engine_status(self, active: ConversionEngine) -> None:
        names = {
            ConversionEngine.MS_OFFICE:   "Microsoft Office",
            ConversionEngine.LIBREOFFICE: "LibreOffice",
            ConversionEngine.NONE:        "Motor yok",
        }
        colors = {
            ConversionEngine.MS_OFFICE:   PALETTE["success"],
            ConversionEngine.LIBREOFFICE: PALETTE["success"],
            ConversionEngine.NONE:        PALETTE["error"],
        }
        name = names.get(active, "?")
        color = colors.get(active, PALETTE["text_muted"])
        self._engine_status.setText(f"Aktif: {name}")
        self._engine_status.setStyleSheet(
            f"color: {color}; font-size: 11px; background: transparent;"
        )

    def _browse_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Çıktı Klasörü Seç",
            str(Path.home()),
        )
        if directory:
            self._output_dir = Path(directory)
            self._out_edit.setText(directory)
            self.options_changed.emit()

    def _clear_output_dir(self) -> None:
        self._output_dir = None
        self._out_edit.clear()
        self.options_changed.emit()