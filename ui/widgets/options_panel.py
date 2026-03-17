"""
Options Panel Widget
====================
Dönüşüm seçeneklerini sunar. SRP: yalnızca seçenek toplama.

Responsive: QFormLayout kullanır — Qt'nin native form düzeni.
Pencere ne kadar daraltılırsa daraltılsın etiket+kontrol hizası bozulmaz.
"""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from core.interfaces.converter_interface import ConversionOptions
from core.converters.pptx_to_pdf import ConversionEngine
from ui.styles.theme import PALETTE


def _section_header(text: str) -> QLabel:
    """Grup başlığı — GroupBox yerine sade label + ince çizgi."""
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {PALETTE['text_muted']};"
        f"font-size: 10px; font-weight: 700; letter-spacing: 1.2px;"
        f"background: transparent; padding: 0; margin: 0;"
    )
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {PALETTE['border']}; background: transparent;")
    line.setFixedHeight(1)
    return line


def _form_label(text: str) -> QLabel:
    """Form satırı sol etiketi."""
    lbl = QLabel(text)
    lbl.setMinimumWidth(50 if text else 0)
    lbl.setMinimumHeight(24) # Font uyarısını önlemek için minimum yükseklik
    lbl.setStyleSheet(
        f"color: {PALETTE['text_secondary']}; font-size: 12px; background: transparent;"
    )
    # NOT: setSizePolicy(Fixed, Fixed) burada KULLANILMAMALI.
    # QFormLayout etiket sütununa negatif boyut atadığında
    # "QFont::setPointSize: Point size <= 0" uyarısı üretir.
    # QFormLayout kendi etiket genişliğini otomatik yönetir.
    return lbl


class OptionsPanelWidget(QWidget):
    """Kullanıcı seçeneklerini toplayan panel."""

    options_changed = Signal()
    engine_changed  = Signal(object)   # ConversionEngine | None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._output_dir: Optional[Path] = None
        self._setup_ui()

    # ================================================================== #
    #  UI Setup                                                            #
    # ================================================================== #

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 4, 0, 0)
        root.setSpacing(0)

        # ── Bölüm: Motor ──────────────────────────────────────────
        root.addWidget(self._section("DÖNÜŞÜM MOTORU", self._build_engine_form()))

        # ── Bölüm: Çıktı ──────────────────────────────────────────
        root.addSpacing(6)
        root.addWidget(self._section("ÇIKTI KONUMU", self._build_output_form()))

        # ── Bölüm: Kalite ─────────────────────────────────────────
        root.addSpacing(6)
        root.addWidget(self._section("KALİTE AYARLARI", self._build_quality_form()))

    def _section(self, title: str, form_widget: QWidget) -> QWidget:
        """Başlık + içerik kartı."""
        card = QWidget()
        card.setStyleSheet(
            f"QWidget#sectionCard {{"
            f"  background: {PALETTE['bg_card']};"
            f"  border: 1px solid {PALETTE['border']};"
            f"  border-radius: 8px;"
            f"}}"
        )
        card.setObjectName("sectionCard")

        v = QVBoxLayout(card)
        v.setContentsMargins(12, 8, 12, 10)
        v.setSpacing(4)

        hdr = _section_header(title)
        v.addWidget(hdr)
        v.addWidget(_divider())
        v.addWidget(form_widget)
        
        # Yatay yerleşimde sıkışmayı önlemek için minimum yükseklik
        card.setMinimumHeight(96)
        return card

    # ── Motor formu ───────────────────────────────────────────────────── #

    def _build_engine_form(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        form = QFormLayout(w)
        form.setContentsMargins(0, 4, 0, 0)
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._engine_combo = QComboBox()
        self._engine_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._engine_combo.setMinimumWidth(100)
        self._engine_combo.setToolTip(
            "Otomatik: Önce MS Office, bulunamazsa LibreOffice denenir."
        )
        self._engine_combo.currentIndexChanged.connect(self._on_engine_changed)

        self._engine_status = QLabel("—")
        self._engine_status.setStyleSheet(
            f"color: {PALETTE['text_muted']}; font-size: 12px; background: transparent;"
        )
        self._engine_status.setMinimumHeight(24) # Font uyarısını önlemek için
        self._engine_status.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        form.addRow(_form_label("Motor:"),  self._engine_combo)
        form.addRow(_form_label("Durum:"),  self._engine_status)
        return w

    # ── Çıktı formu ───────────────────────────────────────────────────── #

    def _build_output_form(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        form = QFormLayout(w)
        form.setContentsMargins(0, 4, 0, 0)
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._out_edit = QLineEdit()
        self._out_edit.setPlaceholderText("Kaynak dosyayla aynı klasör (varsayılan)")
        self._out_edit.setReadOnly(True)
        self._out_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        browse_btn = QPushButton("Gözat")
        browse_btn.setFixedWidth(64)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_output_dir)

        clear_btn = QPushButton("✕")
        clear_btn.setFixedWidth(28)
        clear_btn.setToolTip("Varsayılana dön")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_output_dir)

        row = QHBoxLayout()
        row.setSpacing(4)
        row.addWidget(self._out_edit)
        row.addWidget(browse_btn)
        row.addWidget(clear_btn)

        form.addRow(_form_label("Klasör:"), row)
        return w

    # ── Kalite formu ──────────────────────────────────────────────────── #

    def _build_quality_form(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        form = QFormLayout(w)
        form.setContentsMargins(0, 4, 0, 0)
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._dpi_spin = QSpinBox()
        self._dpi_spin.setRange(72, 600)
        self._dpi_spin.setValue(150)
        self._dpi_spin.setSuffix(" dpi")
        self._dpi_spin.setMinimumWidth(80)
        self._dpi_spin.setMaximumWidth(110)
        self._dpi_spin.setToolTip(
            "Yalnızca LibreOffice motorunda etkilidir.\n"
            "MS Office kendi kalite ayarlarını kullanır."
        )
        self._dpi_spin.valueChanged.connect(self.options_changed)

        self._overwrite_check = QCheckBox("Mevcut dosyaların üzerine yaz")
        self._overwrite_check.setChecked(True)
        self._overwrite_check.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._overwrite_check.stateChanged.connect(self.options_changed)

        form.addRow(_form_label("DPI:"),    self._dpi_spin)
        form.addRow(_form_label(""),        self._overwrite_check)
        return w

    # ================================================================== #
    #  Public API                                                          #
    # ================================================================== #

    def populate_engines(
        self,
        available: List[ConversionEngine],
        active: ConversionEngine,
    ) -> None:
        _LABELS = {
            ConversionEngine.MS_OFFICE:   "Microsoft Office",
            ConversionEngine.LIBREOFFICE: "LibreOffice",
        }

        self._engine_combo.blockSignals(True)
        self._engine_combo.clear()
        self._engine_combo.addItem("🔄  Otomatik (önerilen)", userData=None)

        for engine in [ConversionEngine.MS_OFFICE, ConversionEngine.LIBREOFFICE]:
            label = _LABELS[engine]
            if engine in available:
                self._engine_combo.addItem(f"✅  {label}", userData=engine)
            else:
                self._engine_combo.addItem(f"❌  {label} (kurulu değil)", userData=engine)
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
        return self._engine_combo.currentData()

    # ================================================================== #
    #  Private                                                             #
    # ================================================================== #

    def _on_engine_changed(self, _index: int) -> None:
        self.engine_changed.emit(self._engine_combo.currentData())

    def _update_engine_status(self, active: ConversionEngine) -> None:
        texts = {
            ConversionEngine.MS_OFFICE:   ("● Microsoft Office", PALETTE["success"]),
            ConversionEngine.LIBREOFFICE: ("● LibreOffice",      PALETTE["success"]),
            ConversionEngine.NONE:        ("● Motor bulunamadı", PALETTE["error"]),
        }
        text, color = texts.get(active, ("—", PALETTE["text_muted"]))
        self._engine_status.setText(text)
        self._engine_status.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600; background: transparent;"
        )

    def _browse_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Çıktı Klasörü Seç", str(Path.home()),
        )
        if directory:
            self._output_dir = Path(directory)
            self._out_edit.setText(directory)
            self.options_changed.emit()

    def _clear_output_dir(self) -> None:
        self._output_dir = None
        self._out_edit.clear()
        self.options_changed.emit()