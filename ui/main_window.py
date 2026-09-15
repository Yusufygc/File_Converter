"""
Main Window
===========
Tüm widget'ları ve servisleri bir araya getirir.
Controller rolü üstlenir: UI event → Service → UI güncellemesi.
"""

from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import (
    QApplication,
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
    IConverter,
)
from ui.adapters.qt_conversion_runner import QtConversionRunner
from ui.app_settings import AppSettings
from ui.dialogs.summary_dialog import SummaryDialog
from ui.styles.theme import PALETTE
from ui.widgets.drop_zone import DropZoneWidget
from ui.widgets.file_list import FileListWidget
from ui.widgets.options_panel import OptionsPanelWidget
from core.converters.registry import ConverterRegistry
from core.converters.discovery import register_all
from core.interfaces.engine_interface import IEngineSelectable
from core.interfaces.merge_interface import IMergeConverter
from core.interfaces.page_range_interface import IPageRangeSelectable
from core.utils.resource_helper import get_resource_path
from ui.converter_catalog import catalog_entries


class MainWindow(QMainWindow):
    """
    Uygulamanın ana penceresi.
    Composition Root görevi görür: tüm bağımlılıklar burada oluşturulur.
    """

    def __init__(self):
        super().__init__()
        self._settings = AppSettings()

        # ── Dependency Composition ─────────────────────────────────
        # Converter'lar elle import/instantiate edilmez — core/converters/
        # paketi otomatik taranır (bkz. discovery.py). Yeni bir dönüşüm
        # eklemek için tek yapılması gereken: o pakete bir dosya eklemek.
        self._registry = ConverterRegistry()
        register_all(self._registry)
        self._converters: List[IConverter] = catalog_entries(self._registry)

        # Aktif converter — başlangıçta katalogdaki ilk sıradaki (bkz.
        # ui/converter_catalog.py _PREFERRED_ORDER)
        self._active_converter: IConverter = self._converters[0]

        self._service = QtConversionRunner(self._registry)
        self._converting = False
        self._cancel_requested = False
        self._last_conversion_was_merge = False

        # ── Window Setup ───────────────────────────────────────────
        self.setWindowTitle("FileConvert Pro")
        self.setWindowIcon(QIcon(get_resource_path("assets/icons/app_icon.svg")))
        self.setMinimumSize(960, 680) # 4 bölümlü options panel için yükseklik artırıldı
        self.resize(1100, 760)

        self._build_ui()
        self._connect_signals()
        self._populate_engines()
        self._update_ui_state()

        # Converter türleri event loop başladıktan sonra eklenir —
        # DPI bağlamı o noktada hazır olur, QFont uyarısı oluşmaz.
        QTimer.singleShot(0, self._on_ui_ready)

    def _on_ui_ready(self) -> None:
        self._options_panel.populate_converter_types(self._converters)
        self._restore_settings()

    def _restore_settings(self) -> None:
        """Önceki oturumdan kalan pencere/dönüşüm türü/seçenek durumunu geri yükler."""
        geometry = self._settings.load_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

        converter_key = self._settings.load_converter_key()
        if converter_key:
            match = next(
                (
                    c for c in self._converters
                    if (c.source_extension, c.target_extension) == converter_key
                ),
                None,
            )
            if match is not None:
                self._options_panel.select_converter(match)

        self._options_panel.set_output_dir(self._settings.load_output_dir())
        dpi, quality, overwrite = self._settings.load_quality_options()
        self._options_panel.set_quality_options(dpi, quality, overwrite)

    def closeEvent(self, event) -> None:
        """Pencere kapanırken mevcut durumu kalıcı olarak saklar."""
        self._settings.save_window_geometry(self.saveGeometry())
        self._settings.save_converter_key(
            self._active_converter.source_extension,
            self._active_converter.target_extension,
        )
        options = self._options_panel.get_options()
        self._settings.save_output_dir(options.output_dir)
        self._settings.save_quality_options(
            options.dpi, options.quality, options.overwrite_existing
        )
        super().closeEvent(event)

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

        logo = QLabel()
        logo.setPixmap(QIcon(get_resource_path("assets/icons/app_icon.svg")).pixmap(24, 24))
        logo.setStyleSheet("background: transparent; margin-right: 8px;")

        title = QLabel("FileConvert Pro")
        title.setObjectName("appTitle")

        self._format_badge = QLabel(self._active_converter.display_name.upper())
        self._format_badge.setObjectName("formatBadge")
        badge = self._format_badge

        self._theme_btn = QPushButton(self._theme_button_icon())
        self._theme_btn.setObjectName("themeBtn")
        self._theme_btn.setFixedSize(32, 32)
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.setToolTip("Tema değiştir")
        self._theme_btn.clicked.connect(self._on_theme_toggle_clicked)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(badge)
        layout.addStretch()
        layout.addWidget(self._theme_btn)
        return header

    def _theme_button_icon(self) -> str:
        return "☀️" if self._settings.load_theme_mode() == "light" else "🌙"

    def _on_theme_toggle_clicked(self) -> None:
        """
        Tema tercihini kaydeder ve anında uygular. `ui/styles/theme.py`
        `apply_theme()` çağrısı `PALETTE`'i yerinde günceller (nesne
        kimliği korunur) ve yeni QSS'i döner — bu, `QApplication`
        genelinde tüm objectName tabanlı stilleri anında yeniler.
        Duruma göre renklenen (başarı/hata/uyarı) birkaç widget QSS'e
        taşınamıyor; onlar `_refresh_engine_display()`/
        `FileListWidget.retheme()` ile son durumlarını güncel PALETTE
        ile yeniden çizer. Bkz. docs/wiki/ui-katmani.md.
        """
        current = self._settings.load_theme_mode()
        new_mode = "light" if current == "dark" else "dark"
        self._settings.save_theme_mode(new_mode)

        from ui.styles import theme as theme_module
        new_qss = theme_module.apply_theme(new_mode)
        QApplication.instance().setStyleSheet(new_qss)

        self._theme_btn.setText(self._theme_button_icon())
        self._refresh_engine_display()
        self._file_list.retheme()

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

        # Drop Zone — başlangıçta aktif converter'ın kabul ettiği uzantı(lar)
        self._drop_zone = DropZoneWidget(
            accepted_extensions=self._active_converter.accepted_extensions
        )
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

        add_btn = QPushButton(" Dosya Ekle")
        add_btn.setIcon(QIcon(get_resource_path("assets/icons/add.svg")))
        add_btn.setObjectName("addBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setMinimumWidth(120)
        add_btn.clicked.connect(self._open_file_dialog)

        self._remove_btn = QPushButton(" Kaldır")
        self._remove_btn.setIcon(QIcon(get_resource_path("assets/icons/remove.svg")))
        self._remove_btn.setObjectName("dangerBtn")
        self._remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._remove_btn.setEnabled(False)
        self._remove_btn.setMinimumWidth(90)
        self._remove_btn.setToolTip("Seçili dosyaları listeden kaldır")
        self._remove_btn.clicked.connect(self._file_list.remove_selected)

        self._clear_btn = QPushButton(" Temizle")
        self._clear_btn.setIcon(QIcon(get_resource_path("assets/icons/clear.svg")))
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setMinimumWidth(90)
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
        footer.setObjectName("footerBar")
        footer.setMinimumHeight(32)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(16, 0, 16, 0)

        self._status_label = QLabel("Hazır")
        self._status_label.setObjectName("statusLabel")

        engine_name = self._active_converter.active_engine_name
        is_ok = self._active_converter.is_available
        self._engine_footer_label = QLabel(f"●  {engine_name}")
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
        """Motor seçimi destekleyen converter için mevcut motorları options panel'e bildirir."""
        converter = self._active_converter
        self._options_panel.populate_engines(
            available=converter.available_engines(),
            active=converter.active_engine,
        )
        self._update_footer_engine(converter.active_engine_name, converter.is_available)

    def _refresh_engine_display(self) -> None:
        """
        Motor bölümünü (options panel + footer) `self._active_converter`'ın
        güncel durumuna göre yeniden çizer — capability protokolüyle
        (`IEngineSelectable`), belirli bir dönüşüm türünü hardcode etmeden.
        Hem converter değişiminde hem de tema geçişinde (dinamik
        başarı/hata renklerini güncel PALETTE ile yeniden boyamak için)
        çağrılır.
        """
        if isinstance(self._active_converter, IEngineSelectable):
            self._options_panel.restore_engine_combo()
            self._populate_engines()
        else:
            self._options_panel.set_engine_status(
                self._active_converter.active_engine_name,
                self._active_converter.is_available,
            )
            self._update_footer_engine(
                self._active_converter.active_engine_name,
                self._active_converter.is_available,
            )

    def _on_engine_changed(self, engine) -> None:
        """
        Kullanıcı motor seçimini değiştirdiğinde çağrılır.
        engine=None → Otomatik. `set_preferred_engine(None)` converter'ın
        kendi resolver'ında zaten "ilk müsait motoru seç" anlamına gelir —
        UI'ın converter'ın özel/private durumuna dokunmasına gerek yok.
        """
        from core.converters.pptx_to_pdf import ConversionEngine
        from PySide6.QtWidgets import QMessageBox

        converter = self._active_converter
        success = converter.set_preferred_engine(engine)
        if engine is not None and not success:
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
        self._update_footer_engine(converter.active_engine_name, converter.is_available)
        self._update_ui_state()

    # ================================================================== #
    #  Signal Connections                                                  #
    # ================================================================== #

    def _connect_signals(self) -> None:
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        self._file_list.list_changed.connect(self._on_list_changed)
        self._file_list.selection_changed.connect(self._on_selection_changed)
        self._convert_btn.clicked.connect(self._on_convert_button_clicked)
        self._options_panel.engine_changed.connect(self._on_engine_changed)
        self._options_panel.converter_type_changed.connect(self._on_converter_type_changed)

    # ================================================================== #
    #  Slots                                                               #
    # ================================================================== #

    def _on_converter_type_changed(self, converter: IConverter) -> None:
        """Kullanıcı dönüşüm türünü değiştirdiğinde çağrılır."""
        self._active_converter = converter

        # Drop zone güncelle
        self._drop_zone.set_accepted_extensions(converter.accepted_extensions)

        # Dosya listesini temizle (uyumsuz dosyalar kalmasın)
        self._file_list.clear_all()

        # Badge güncelle
        self._format_badge.setText(
            self._active_converter.display_name.upper()
        )

        # Birleştirme onay kutusu — yalnızca IMergeConverter destekleyen
        # converter'lar seçiliyken görünür
        self._options_panel.set_merge_mode_available(
            isinstance(converter, IMergeConverter)
        )

        # Sayfa aralığı alanı — yalnızca IPageRangeSelectable destekleyen
        # converter'lar seçiliyken görünür
        self._options_panel.set_page_range_available(
            isinstance(converter, IPageRangeSelectable)
        )

        self._refresh_engine_display()

        self._update_ui_state()

    def _on_files_dropped(self, paths: List[Path]) -> None:
        if not paths:
            # Drop zone'a tıklama → dosya diyaloğu
            self._open_file_dialog()
            return
        self._file_list.add_files(paths)

    def _open_file_dialog(self) -> None:
        display_name = self._active_converter.display_name.split("→")[0].strip()

        patterns = " ".join(f"*{ext}" for ext in self._active_converter.accepted_extensions)
        filters = (
            f"{display_name} Dosyaları ({patterns});;"
            "Tüm Dosyalar (*.*)"
        )
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            f"{display_name} Dosyaları Seç",
            str(Path.home()),
            filters,
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

    def _on_convert_button_clicked(self) -> None:
        """
        Dönüştür/İptal Et butonu tek bir buton — davranışı `self._converting`
        durumuna göre dallanır (ayrı bir iptal butonu eklemek yerine daha
        az arayüz kalabalığı).
        """
        if self._converting:
            self._cancel_requested = True
            self._service.cancel()
            self._convert_btn.setEnabled(False)  # durana kadar tekrar tıklamayı engelle
        else:
            self._start_conversion()

    def _start_conversion(self) -> None:
        files = self._file_list.all_paths()
        if not files:
            return

        if not self._active_converter.is_available:
            name = self._active_converter.display_name
            QMessageBox.critical(
                self,
                "Motor Bulunamadı",
                f"{name} dönüşümü için gerekli araç kurulu değil.\n\n"
                + self._active_converter.unavailable_hint,
            )
            return

        options = self._options_panel.get_options()
        self._cancel_requested = False
        self._set_converting_state(True)
        self._file_list.reset_statuses()
        self._progress_bar.setMaximum(len(files))
        self._progress_bar.setValue(0)

        self._last_conversion_was_merge = (
            self._options_panel.is_merge_mode()
            and isinstance(self._active_converter, IMergeConverter)
        )

        if self._last_conversion_was_merge:
            # Birleştirme modu: N dosya → tek çıktı. Dosya-bazlı progress/
            # durum güncellemesi anlamsız (tek bir sonuç var) — doğrudan
            # _on_batch_done'a gider. İptal desteklenmez (bkz. MergeWorker.cancel()).
            self._service.start_merge_conversion(
                files=files,
                converter=self._active_converter,
                options=options,
                on_done=self._on_batch_done,
            )
        else:
            self._service.start_batch_conversion(
                files=files,
                converter=self._active_converter,
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

        if self._last_conversion_was_merge:
            status = (
                "✅ Dosyalar tek çıktıda birleştirildi"
                if batch.all_succeeded
                else f"⚠ Birleştirme başarısız: {batch.results[0].error_message}"
            )
        elif self._cancel_requested:
            total_files = len(self._file_list.all_paths())
            status = f"⚠ İptal edildi — {batch.total}/{total_files} dosya işlendi"
        elif batch.all_succeeded:
            status = f"✅ {batch.success_count}/{batch.total} dosya başarıyla dönüştürüldü"
        else:
            status = f"⚠ {batch.success_count} başarılı, {batch.failure_count} hatalı"
        self._status_label.setText(status)

        dialog = SummaryDialog(batch, self)
        dialog.exec()

    def _update_footer_engine(self, engine_name: str, is_available: bool) -> None:
        color = PALETTE['success'] if is_available else PALETTE['error']
        self._engine_footer_label.setText(f"●  {engine_name}")
        self._engine_footer_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 600; background: transparent;"
        )

    # ================================================================== #
    #  State Management                                                    #
    # ================================================================== #

    def _set_converting_state(self, converting: bool) -> None:
        self._converting = converting

        if converting:
            self._convert_btn.setText("✕   İptal Et")
            self._convert_btn.setObjectName("dangerBtn")
        else:
            self._convert_btn.setText("⚡   Dönüştür")
            self._convert_btn.setObjectName("primaryBtn")
        # objectName değişince QSS yeniden uygulanmalı (bkz. drop_zone._refresh_style deseni)
        self._convert_btn.style().unpolish(self._convert_btn)
        self._convert_btn.style().polish(self._convert_btn)
        self._convert_btn.setEnabled(True)

        self._progress_bar.setVisible(converting)
        self._drop_zone.setEnabled(not converting)

    def _update_ui_state(self) -> None:
        has_files = self._file_list.count() > 0
        if not self._converting:
            self._convert_btn.setEnabled(has_files)
        self._clear_btn.setEnabled(has_files)