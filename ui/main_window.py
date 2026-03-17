"""
Main Window
===========
Tüm widget'ları ve servisleri bir araya getirir.
Controller rolü üstlenir: UI event → Service → UI güncellemesi.
"""

from pathlib import Path
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from core.interfaces.converter_interface import (
    BatchConversionResult,
    ConversionResult,
)
from services.conversion_service import ConversionService
from ui.dialogs.summary_dialog import SummaryDialog
from ui.styles.theme import PALETTE
from ui.widgets.drop_zone import DropZoneWidget
from ui.widgets.file_list import FileListWidget
from ui.widgets.options_panel import OptionsPanelWidget
from core.converters.registry import ConverterRegistry
from core.converters.pptx_to_pdf import PptxToPdfConverter


class MainWindow(QMainWindow):
    """
    Uygulamanın ana penceresi.
    Composition Root görevi görür: tüm bağımlılıklar burada oluşturulur.
    """

    def __init__(self):
        super().__init__()
        # ── Dependency Composition ─────────────────────────────────
        self._registry = ConverterRegistry()
        self._pptx_converter = PptxToPdfConverter()
        self._registry.register(self._pptx_converter)

        self._service = ConversionService(self._registry)

        # ── Window Setup ───────────────────────────────────────────
        self.setWindowTitle("FileConvert Pro")
        self.setMinimumSize(960, 600) # Yatay yerleşim için genişletilmiş minimum
        self.resize(1100, 700)

        self._build_ui()
        self._connect_signals()
        self._populate_engines()
        self._update_ui_state()

    # ================================================================== #
    #  UI Construction                                                     #
    # ================================================================== #

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_body(), 1)
        root.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("titleBar")
        header.setMinimumHeight(52)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)

        logo = QLabel("⚡")
        logo.setStyleSheet("font-size: 18px; background: transparent; margin-right: 8px;")

        title = QLabel("FileConvert Pro")
        title.setObjectName("appTitle")
        title.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {PALETTE['text_primary']};"
            f"background: transparent; margin-right: 12px;"
        )

        badge = QLabel("PPTX → PDF")
        badge.setObjectName("formatBadge")
        badge.setStyleSheet(
            f"font-size: 10px; font-weight: 700; letter-spacing: 1px;"
            f"background: {PALETTE['accent_dim']}; color: {PALETTE['accent']};"
            f"border-radius: 4px; padding: 3px 8px;"
        )

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(badge)
        layout.addStretch()
        return header

    def _build_body(self) -> QWidget:
        body = QWidget()
        layout = QHBoxLayout(body) # Yatay yerleşim
        layout.setContentsMargins(20, 16, 20, 0)
        layout.setSpacing(24)

        # ── SOL PANEL: Ayarlar ve Dönüştür ────────────────────────────
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Seçenek paneli
        self._options_panel = OptionsPanelWidget()
        left_layout.addWidget(self._options_panel, 1)

        # Dönüştür butonu — CTA
        self._convert_btn = QPushButton("⚡   Dönüştür")
        self._convert_btn.setObjectName("primaryBtn")
        self._convert_btn.setFixedHeight(46)
        self._convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(self._convert_btn)
        left_layout.addSpacing(12)

        # ── SAĞ PANEL: Dosyalar ──────────────────────────────────────
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Drop Zone
        self._drop_zone = DropZoneWidget(accepted_extensions=[".pptx"])
        self._drop_zone.setFixedHeight(100)
        right_layout.addWidget(self._drop_zone)

        # Dosya listesi - Toolbar'dan önce oluşturulmalı çünkü toolbar buna referans veriyor
        self._file_list = FileListWidget()

        # Araç çubuğu
        right_layout.addLayout(self._build_toolbar())

        # Dosya listesi ekle
        right_layout.addWidget(self._file_list, 1)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMinimumHeight(6)
        self._progress_bar.setTextVisible(False)
        right_layout.addWidget(self._progress_bar)
        right_layout.addSpacing(12)

        layout.addWidget(left_panel, 1) # Eşit oran
        layout.addWidget(right_panel, 1) # Eşit oran
        
        return body

    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        self._file_count_label = QLabel("Dosya eklenmedi")
        self._file_count_label.setObjectName("fileCount")
        self._file_count_label.setMinimumWidth(80)
        self._file_count_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )

        add_btn = QPushButton("＋  Dosya Ekle")
        add_btn.setObjectName("addBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setMinimumWidth(100)
        add_btn.clicked.connect(self._open_file_dialog)

        self._remove_btn = QPushButton("Kaldır")
        self._remove_btn.setObjectName("dangerBtn")
        self._remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._remove_btn.setEnabled(False)
        self._remove_btn.setMinimumWidth(70)
        self._remove_btn.setToolTip("Seçili dosyaları listeden kaldır")
        self._remove_btn.clicked.connect(self._file_list.remove_selected)

        self._clear_btn = QPushButton("Temizle")
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setMinimumWidth(70)
        self._clear_btn.setToolTip("Tüm dosyaları listeden kaldır")
        self._clear_btn.clicked.connect(self._file_list.clear_all)

        toolbar.addWidget(self._file_count_label)
        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        toolbar.addWidget(self._remove_btn)
        toolbar.addWidget(self._clear_btn)

        return toolbar

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setMinimumHeight(32)
        footer.setStyleSheet(
            f"background: {PALETTE['bg_surface']}; border-top: 1px solid {PALETTE['border']};"
        )

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(16, 0, 16, 0)

        self._status_label = QLabel("Hazır")
        self._status_label.setObjectName("statusLabel")

        engine_name = self._pptx_converter.active_engine_name
        is_ok = self._pptx_converter.is_available
        dot = "●"
        self._engine_footer_label = QLabel(f"{dot}  {engine_name}")
        color = PALETTE['success'] if is_ok else PALETTE['error']
        self._engine_footer_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 600; background: transparent;"
        )

        layout.addWidget(self._status_label)
        layout.addStretch()
        layout.addWidget(self._engine_footer_label)

        return footer

    # ================================================================== #
    #  Engine Management                                                   #
    # ================================================================== #

    def _populate_engines(self) -> None:
        """Uygulama açılışında mevcut motorları options panel'e bildir."""
        self._options_panel.populate_engines(
            available=self._pptx_converter.available_engines(),
            active=self._pptx_converter.active_engine,
        )

    def _on_engine_changed(self, engine) -> None:
        """
        Kullanıcı motor seçimini değiştirdiğinde çağrılır.
        engine=None → Otomatik
        """
        from core.converters.pptx_to_pdf import ConversionEngine
        from PySide6.QtWidgets import QMessageBox

        if engine is None:
            # Otomatik moda geç: preferred'ı sıfırlayıp tekrar resolve et
            self._pptx_converter._preferred = None
            self._pptx_converter._active_strategy = (
                self._pptx_converter._resolve_strategy()
            )
        else:
            success = self._pptx_converter.set_preferred_engine(engine)
            if not success:
                hint = (
                    "pip install pywin32"
                    if engine == ConversionEngine.MS_OFFICE
                    else "https://www.libreoffice.org/download"
                )
                QMessageBox.warning(
                    self,
                    "Motor Kullanılamıyor",
                    f"Seçilen motor bu sistemde mevcut değil.\n\n{hint}",
                )
                return

        # Footer güncelle
        name = self._pptx_converter.active_engine_name
        is_ok = self._pptx_converter.is_available
        color = PALETTE['success'] if is_ok else PALETTE['error']
        self._engine_footer_label.setText(f"●  {name}")
        self._engine_footer_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 600; background: transparent;"
        )
        self._update_ui_state()

    # ================================================================== #
    #  Signal Connections                                                  #
    # ================================================================== #

    def _connect_signals(self) -> None:
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        self._file_list.list_changed.connect(self._on_list_changed)
        self._file_list.selection_changed.connect(self._on_selection_changed)
        self._convert_btn.clicked.connect(self._start_conversion)
        self._options_panel.engine_changed.connect(self._on_engine_changed)

    # ================================================================== #
    #  Slots                                                               #
    # ================================================================== #

    def _on_files_dropped(self, paths: List[Path]) -> None:
        if not paths:
            # Drop zone'a tıklama → dosya diyaloğu
            self._open_file_dialog()
            return
        self._file_list.add_files(paths)

    def _open_file_dialog(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "PPTX Dosyaları Seç",
            str(Path.home()),
            "PowerPoint Dosyaları (*.pptx);;Tüm Dosyalar (*.*)",
        )
        if paths:
            self._file_list.add_files([Path(p) for p in paths])

    def _on_list_changed(self, count: int) -> None:
        if count == 0:
            self._file_count_label.setText("Dosya eklenmedi")
        elif count == 1:
            self._file_count_label.setText("1 dosya eklendi")
        else:
            self._file_count_label.setText(f"{count} dosya eklendi")
        self._update_ui_state()

    def _on_selection_changed(self, count: int) -> None:
        self._remove_btn.setEnabled(count > 0)

    def _start_conversion(self) -> None:
        files = self._file_list.all_paths()
        if not files:
            return

        if not self._pptx_converter.is_available:
            QMessageBox.critical(
                self,
                "LibreOffice Gerekli",
                "PPTX → PDF dönüşümü için LibreOffice kurulu olmalıdır.\n\n"
                "Ubuntu/Debian: sudo apt install libreoffice\n"
                "Windows: https://www.libreoffice.org/download",
            )
            return

        options = self._options_panel.get_options()
        self._set_converting_state(True)
        self._file_list.reset_statuses()
        self._progress_bar.setMaximum(len(files))
        self._progress_bar.setValue(0)

        self._service.start_batch_conversion(
            files=files,
            converter=self._pptx_converter,
            options=options,
            on_progress=self._on_progress,
            on_file_done=self._on_file_done,
            on_batch_done=self._on_batch_done,
        )

    def _on_progress(self, completed: int, total: int) -> None:
        self._progress_bar.setValue(completed)
        self._status_label.setText(
            f"Dönüştürülüyor... {completed}/{total}"
        )

    def _on_file_done(self, result: ConversionResult) -> None:
        self._file_list.mark_result(result)

    def _on_batch_done(self, batch: BatchConversionResult) -> None:
        self._set_converting_state(False)
        self._progress_bar.setValue(batch.total)

        status = (
            f"✅ {batch.success_count}/{batch.total} dosya başarıyla dönüştürüldü"
            if batch.all_succeeded
            else f"⚠ {batch.success_count} başarılı, {batch.failure_count} hatalı"
        )
        self._status_label.setText(status)

        dialog = SummaryDialog(batch, self)
        dialog.exec()

    # ================================================================== #
    #  State Management                                                    #
    # ================================================================== #

    def _set_converting_state(self, converting: bool) -> None:
        self._convert_btn.setEnabled(not converting)
        self._progress_bar.setVisible(converting)
        self._drop_zone.setEnabled(not converting)

    def _update_ui_state(self) -> None:
        has_files = self._file_list.count() > 0
        self._convert_btn.setEnabled(has_files)
        self._clear_btn.setEnabled(has_files)