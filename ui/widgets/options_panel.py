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

from core.interfaces.converter_interface import ConversionOptions, IConverter
from core.converters.pptx_to_pdf import ConversionEngine
from ui.styles.theme import PALETTE


def _section_header(text: str) -> QLabel:
    """Grup başlığı — GroupBox yerine sade label + ince çizgi."""
    lbl = QLabel(text)
    lbl.setMinimumHeight(16)  # Negatif yükseklik → QFont uyarısını önler
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
    line.setMinimumHeight(1)
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

    options_changed       = Signal()
    engine_changed        = Signal(object)   # ConversionEngine | None
    converter_type_changed = Signal(object)  # seçilen IConverter

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

        # ── Bölüm: Dönüşüm Türü ───────────────────────────────────
        root.addWidget(self._section("DÖNÜŞÜM TÜRÜ", self._build_converter_type_form()))

        # ── Bölüm: Motor ──────────────────────────────────────────
        root.addSpacing(6)
        self._engine_section = self._section("DÖNÜŞÜM MOTORU", self._build_engine_form())
        root.addWidget(self._engine_section)

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
        
        # Sıkışmayı önlemek için minimum yükseklik (4 bölüme göre azaltıldı)
        card.setMinimumHeight(72)
        return card

    # ── Dönüşüm türü formu ───────────────────────────────────────────── #

    def _build_converter_type_form(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        form = QFormLayout(w)
        form.setContentsMargins(0, 4, 0, 0)
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._conv_type_combo = QComboBox()
        self._conv_type_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        # Öğeler burada EKLENMEZ — DPI bağlamı henüz hazır değil.
        # populate_converter_types() çağrısı MainWindow tarafından yapılır.
        self._conv_type_combo.currentIndexChanged.connect(self._on_converter_type_changed)

        form.addRow(_form_label("Format:"), self._conv_type_combo)

        # Birleştirme onay kutusu — yalnızca IMergeConverter destekleyen
        # converter'lar seçiliyken görünür (bkz. set_merge_mode_available).
        self._merge_available = False
        self._merge_label = _form_label("")
        self._merge_check = QCheckBox("Tüm dosyaları TEK çıktıda birleştir")
        self._merge_check.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._merge_label.setVisible(False)
        self._merge_check.setVisible(False)
        form.addRow(self._merge_label, self._merge_check)

        return w

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
            "LibreOffice motorunda ve PDF → JPG dönüşümünde etkilidir.\n"
            "MS Office kendi kalite ayarlarını kullanır."
        )
        self._dpi_spin.valueChanged.connect(self.options_changed)

        self._quality_spin = QSpinBox()
        self._quality_spin.setRange(1, 100)
        self._quality_spin.setValue(90)
        self._quality_spin.setSuffix(" %")
        self._quality_spin.setMinimumWidth(80)
        self._quality_spin.setMaximumWidth(110)
        self._quality_spin.setToolTip(
            "Yalnızca PDF → JPG dönüşümünde etkilidir (JPEG kalitesi)."
        )
        self._quality_spin.valueChanged.connect(self.options_changed)

        self._overwrite_check = QCheckBox("Mevcut dosyaların üzerine yaz")
        self._overwrite_check.setChecked(True)
        self._overwrite_check.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._overwrite_check.stateChanged.connect(self.options_changed)

        form.addRow(_form_label("DPI:"),     self._dpi_spin)
        form.addRow(_form_label("Kalite:"),  self._quality_spin)
        form.addRow(_form_label(""),         self._overwrite_check)
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
            quality=self._quality_spin.value(),
            overwrite_existing=self._overwrite_check.isChecked(),
        )

    def selected_engine(self) -> Optional[ConversionEngine]:
        return self._engine_combo.currentData()

    def populate_converter_types(self, converters: List[IConverter]) -> None:
        """
        Dönüşüm türü seçeneklerini registry'den gelen converter listesinden
        JENERİK olarak doldurur — yeni bir converter eklemek bu metoda
        dokunmayı gerektirmez.
        MainWindow, pencere gösterildikten SONRA çağırır —
        bu sayede DPI bağlamı hazır olur ve QFont uyarısı oluşmaz.
        """
        self._conv_type_combo.blockSignals(True)
        self._conv_type_combo.clear()
        for converter in converters:
            self._conv_type_combo.addItem(converter.display_name, userData=converter)
        self._conv_type_combo.blockSignals(False)

    def select_converter(self, converter: IConverter) -> bool:
        """
        Verilen converter'ı dropdown'da seçili yapar (kayıtlı ayarları geri
        yüklerken kullanılır). Combo'da bulunamazsa `False` döner, seçim
        değişmez.
        """
        idx = self._conv_type_combo.findData(converter)
        if idx < 0:
            return False
        self._conv_type_combo.setCurrentIndex(idx)
        return True

    def set_merge_mode_available(self, available: bool) -> None:
        """
        Birleştirme onay kutusunu gösterir/gizler. `MainWindow`,
        `isinstance(converter, IMergeConverter)` sonucuna göre çağırır.
        Gizlenirken işaret kaldırılır — uyumsuz bir converter'a
        geçildiğinde eski seçimin sessizce kalmasını önler.

        `self._merge_available` ayrıca izlenir: `QWidget.isVisible()`
        yalnızca `setVisible(True)` bayrağını değil, TÜM üst pencere
        zincirinin gerçekten ekranda gösterilip gösterilmediğini de
        yansıtır — pencere henüz `show()` edilmemişse (örn. testlerde)
        `isVisible()` yanlışlıkla `False` döner. `is_merge_mode()` bu
        yüzden Qt'nin görünürlüğüne değil, kendi bayrağımıza bakar.
        """
        self._merge_available = available
        self._merge_label.setVisible(available)
        self._merge_check.setVisible(available)
        if not available:
            self._merge_check.setChecked(False)

    def is_merge_mode(self) -> bool:
        return self._merge_available and self._merge_check.isChecked()

    def set_output_dir(self, path: Optional[Path]) -> None:
        """Kayıtlı çıktı klasörünü sinyal fırlatmadan geri yükler."""
        self._output_dir = path
        self._out_edit.setText(str(path) if path else "")

    def set_quality_options(self, dpi: int, quality: int, overwrite: bool) -> None:
        """Kayıtlı DPI/kalite/üzerine-yaz ayarlarını sinyal fırlatmadan geri yükler."""
        self._dpi_spin.blockSignals(True)
        self._quality_spin.blockSignals(True)
        self._overwrite_check.blockSignals(True)
        self._dpi_spin.setValue(dpi)
        self._quality_spin.setValue(quality)
        self._overwrite_check.setChecked(overwrite)
        self._dpi_spin.blockSignals(False)
        self._quality_spin.blockSignals(False)
        self._overwrite_check.blockSignals(False)

    def set_engine_status(self, engine_name: str, is_available: bool) -> None:
        """
        PDF converter'lar için engine combo içeriğini değiştirir ve devre dışı bırakır.
        setVisible kullanmaz — layout değişmez, QFont uyarısı oluşmaz.
        """
        self._engine_combo.blockSignals(True)
        self._engine_combo.clear()
        self._engine_combo.addItem(engine_name)
        self._engine_combo.setEnabled(False)
        self._engine_combo.blockSignals(False)

        color = PALETTE["success"] if is_available else PALETTE["error"]
        self._engine_status.setText(f"●  {engine_name}")
        self._engine_status.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600; background: transparent;"
        )

    def restore_engine_combo(self) -> None:
        """PPTX converter seçildiğinde combo'yu tekrar etkinleştirir."""
        self._engine_combo.setEnabled(True)
        # populate_engines() main_window tarafından çağrılarak öğeler yenilenir.

    # ================================================================== #
    #  Private                                                             #
    # ================================================================== #

    def _on_converter_type_changed(self, _index: int) -> None:
        self.converter_type_changed.emit(self._conv_type_combo.currentData())

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