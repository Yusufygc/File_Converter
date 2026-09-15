"""
App Bridge for QML
==================
QML Arayüzü ile Python Backend (`core/`) arasındaki ana denetleyici ve köprü.
QObject türevi olup; Property, Signal ve Slot mekanizmalarıyla reaktif iki yönlü
bağlantı sağlar.
"""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PySide6.QtCore import (
    Property,
    QObject,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtWidgets import QFileDialog

from core.converters.discovery import register_all
from core.converters.pptx_to_pdf import ConversionEngine
from core.converters.registry import ConverterRegistry
from core.interfaces.converter_interface import (
    BatchConversionResult,
    ConversionOptions,
    ConversionResult,
    IConverter,
)
from core.interfaces.engine_interface import IEngineSelectable
from core.interfaces.merge_interface import IMergeConverter
from core.interfaces.page_range_interface import IPageRangeSelectable
from core.utils.resource_helper import get_resource_path
from ui.file_discovery import collect_files
from ui_qml.bridge.app_settings import QmlAppSettings
from ui_qml.bridge.conversion_worker import QmlConversionWorker, QmlMergeWorker
from ui_qml.bridge.file_list_model import FileListModel


_PREFERRED_ORDER: List[Union[Tuple[str, str], Tuple[str, str, str]]] = [
    (".pptx", ".pdf"),
    (".docx", ".pdf"),
    (".docx", ".txt"),
    (".docx", ".odt"),
    (".odt", ".docx"),
    (".pdf", ".docx"),
    (".pdf", ".odt"),
    (".pdf", ".jpg"),
    (".pdf", ".png"),
    (".pdf", ".txt"),
    (".pdf", ".pdf", "PdfCompressConverter"),
    (".pdf", ".pdf", "PdfSplitConverter"),
    (".pdf", ".pdf", "PdfMergeConverter"),
    (".xlsx", ".pdf"),
    (".xlsx", ".csv"),
    (".csv", ".xlsx"),
    (".xlsx", ".ods"),
    (".ods", ".xlsx"),
    (".jpg", ".pdf"),
]


def _sort_key(converter: IConverter):
    two = (converter.source_extension, converter.target_extension)
    three = (*two, converter.__class__.__name__)
    if three in _PREFERRED_ORDER:
        return (0, _PREFERRED_ORDER.index(three))
    if two in _PREFERRED_ORDER:
        return (0, _PREFERRED_ORDER.index(two))
    return (1, converter.display_name)


def _categorize_converter(c: IConverter, index: int) -> Tuple[str, Dict[str, Any]]:
    """Kategori ID ve zenginleştirilmiş dönüştürücü meta verisi döndürür."""
    cls_name = c.__class__.__name__
    s_ext = c.source_extension.lower()
    t_ext = c.target_extension.lower()
    accepted = sorted(c.accepted_extensions)

    if "Compress" in cls_name:
        cat_id = "pdf_tools"
        short_name = "PDF Sıkıştır"
        icon = "🗜️"
        badge = "PDF"
    elif "Split" in cls_name:
        cat_id = "pdf_tools"
        short_name = "PDF Böl"
        icon = "✂️"
        badge = "PDF"
    elif "Merge" in cls_name:
        cat_id = "pdf_tools"
        short_name = "PDF Birleştir"
        icon = "📑"
        badge = "PDF"
    elif s_ext == ".pdf" and t_ext == ".txt":
        cat_id = "pdf_tools"
        short_name = "PDF ➔ TXT"
        icon = "📝"
        badge = "TXT"
    elif s_ext in (".jpg", ".jpeg", ".png") or t_ext in (".jpg", ".jpeg", ".png"):
        cat_id = "images"
        short_name = f"{s_ext.replace('.', '').upper()} ➔ {t_ext.replace('.', '').upper()}"
        icon = "🖼️"
        badge = t_ext.replace(".", "").upper()
    elif s_ext in (".xlsx", ".csv", ".ods") or t_ext in (".xlsx", ".csv", ".ods"):
        cat_id = "spreadsheets"
        short_name = f"{s_ext.replace('.', '').upper()} ➔ {t_ext.replace('.', '').upper()}"
        icon = "📊"
        badge = t_ext.replace(".", "").upper()
    else:
        cat_id = "documents"
        short_name = f"{s_ext.replace('.', '').upper()} ➔ {t_ext.replace('.', '').upper()}"
        icon = "📄"
        badge = t_ext.replace(".", "").upper()

    item_data = {
        "index": index,
        "displayName": c.display_name,
        "shortName": short_name,
        "sourceExt": c.source_extension,
        "targetExt": c.target_extension,
        "className": cls_name,
        "icon": icon,
        "badge": badge,
        "acceptedExts": list(accepted),
        "acceptedExtsStr": "  ·  ".join(e.upper() for e in accepted),
        "isAvailable": c.is_available,
        "unavailableHint": c.unavailable_hint,
        "activeEngineName": c.active_engine_name,
        "supportsMerge": isinstance(c, IMergeConverter),
        "supportsPageRange": isinstance(c, IPageRangeSelectable),
        "supportsEngineSelect": isinstance(c, IEngineSelectable),
    }
    return cat_id, item_data


class AppBridge(QObject):
    """QML ile haberleşen ana Bridge sınıfı."""

    # ── Signals ───────────────────────────────────────────────────────
    themeModeChanged = Signal(str)
    convertersChanged = Signal()
    currentConverterIndexChanged = Signal(int)
    currentConverterChanged = Signal()
    engineListChanged = Signal()
    selectedEngineIndexChanged = Signal(int)
    engineStatusChanged = Signal()
    outputDirChanged = Signal(str)
    dpiChanged = Signal(int)
    qualityChanged = Signal(int)
    overwriteExistingChanged = Signal(bool)
    isMergeModeChanged = Signal(bool)
    pageRangeChanged = Signal(str)
    isConvertingChanged = Signal(bool)
    progressChanged = Signal()
    statusMessageChanged = Signal(str)
    summaryDataChanged = Signal()
    showSummaryModalChanged = Signal(bool)
    fileCountChanged = Signal()
    notificationRequested = Signal(str, str)  # (title, message)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._settings = QmlAppSettings()

        # ── Backend Keşif ─────────────────────────────────────────────
        self._registry = ConverterRegistry()
        register_all(self._registry)
        self._converters: List[IConverter] = sorted(
            self._registry.all_converters(), key=_sort_key
        )

        self._active_index: int = 0
        self._active_converter: IConverter = self._converters[0]

        # ── State ─────────────────────────────────────────────────────
        self._theme_mode: str = self._settings.load_theme_mode()
        self._output_dir: Optional[Path] = self._settings.load_output_dir()
        dpi, quality, overwrite = self._settings.load_quality_options()
        self._dpi: int = dpi
        self._quality: int = quality
        self._overwrite_existing: bool = overwrite
        self._is_merge_mode: bool = False
        self._page_range: str = ""

        self._is_converting: bool = False
        self._progress_val: int = 0
        self._progress_max: int = 0
        self._status_message: str = "Hazır"
        self._cancel_requested: bool = False
        self._active_worker: Optional[Union[QmlConversionWorker, QmlMergeWorker]] = None
        self._last_was_merge: bool = False

        self._summary_data: Dict[str, Any] = {}
        self._show_summary_modal: bool = False

        # ── Dosya Listesi Modeli ──────────────────────────────────────
        self._file_model = FileListModel(self)
        self._file_model.countChanged.connect(lambda _: self.fileCountChanged.emit())

        # ── Kaydedilmiş Converter Geri Yükleme ─────────────────────────
        saved_conv = self._settings.load_converter_info()
        if saved_conv:
            s_ext, t_ext, cls_name = saved_conv
            for idx, c in enumerate(self._converters):
                if (
                    c.source_extension == s_ext
                    and c.target_extension == t_ext
                    and (cls_name is None or c.__class__.__name__ == cls_name)
                ):
                    self._active_index = idx
                    self._active_converter = c
                    break

    # ================================================================== #
    #  PROPERTIES                                                          #
    # ================================================================== #

    @Property(QObject, constant=True)
    def fileListModel(self) -> FileListModel:
        return self._file_model

    @Property(str, notify=themeModeChanged)
    def themeMode(self) -> str:
        return self._theme_mode

    @Property(int, notify=fileCountChanged)
    def fileCount(self) -> int:
        return self._file_model.count()

    @Property(bool, notify=fileCountChanged)
    def hasFiles(self) -> bool:
        return self._file_model.count() > 0

    @Property(list, notify=convertersChanged)
    def converters(self) -> List[Dict[str, Any]]:
        result = []
        for i, c in enumerate(self._converters):
            accepted = sorted(c.accepted_extensions)
            result.append(
                {
                    "index": i,
                    "displayName": c.display_name,
                    "sourceExt": c.source_extension,
                    "targetExt": c.target_extension,
                    "className": c.__class__.__name__,
                    "acceptedExts": list(accepted),
                    "acceptedExtsStr": "  ·  ".join(e.upper() for e in accepted),
                    "isAvailable": c.is_available,
                    "unavailableHint": c.unavailable_hint,
                    "activeEngineName": c.active_engine_name,
                    "supportsMerge": isinstance(c, IMergeConverter),
                    "supportsPageRange": isinstance(c, IPageRangeSelectable),
                    "supportsEngineSelect": isinstance(c, IEngineSelectable),
                }
            )
        return result


    @Property(list, notify=convertersChanged)
    def categorizedConverters(self) -> List[Dict[str, Any]]:
        cats = {
            "documents": {"id": "documents", "title": "Belgeler", "icon": "📄", "items": []},
            "spreadsheets": {"id": "spreadsheets", "title": "Tablolar", "icon": "📊", "items": []},
            "images": {"id": "images", "title": "Görseller", "icon": "🖼️", "items": []},
            "pdf_tools": {"id": "pdf_tools", "title": "PDF Araçları", "icon": "⚡", "items": []},
        }
        for i, c in enumerate(self._converters):
            cat_id, item = _categorize_converter(c, i)
            if cat_id in cats:
                cats[cat_id]["items"].append(item)
        return list(cats.values())

    @Property(int, notify=currentConverterIndexChanged)
    def currentConverterIndex(self) -> int:
        return self._active_index

    @Property(dict, notify=currentConverterChanged)
    def currentConverter(self) -> Dict[str, Any]:
        c = self._active_converter
        accepted = sorted(c.accepted_extensions)
        return {
            "index": self._active_index,
            "displayName": c.display_name,
            "sourceExt": c.source_extension,
            "targetExt": c.target_extension,
            "className": c.__class__.__name__,
            "acceptedExts": list(accepted),
            "acceptedExtsStr": "  ·  ".join(e.upper() for e in accepted),
            "isAvailable": c.is_available,
            "unavailableHint": c.unavailable_hint,
            "activeEngineName": c.active_engine_name,
            "supportsMerge": isinstance(c, IMergeConverter),
            "supportsPageRange": isinstance(c, IPageRangeSelectable),
            "supportsEngineSelect": isinstance(c, IEngineSelectable),
        }

    @Property(list, notify=engineListChanged)
    def engineList(self) -> List[Dict[str, Any]]:
        c = self._active_converter
        if not isinstance(c, IEngineSelectable):
            return []

        available_engines = c.available_engines()
        return [
            {
                "id": "auto",
                "name": "🔄  Otomatik (önerilen)",
                "available": True,
                "engine": None,
            },
            {
                "id": "msoffice",
                "name": ("✅  Microsoft Office" if ConversionEngine.MS_OFFICE in available_engines
                         else "❌  Microsoft Office (kurulu değil)"),
                "available": ConversionEngine.MS_OFFICE in available_engines,
                "engine": ConversionEngine.MS_OFFICE,
            },
            {
                "id": "libreoffice",
                "name": ("✅  LibreOffice" if ConversionEngine.LIBREOFFICE in available_engines
                         else "❌  LibreOffice (kurulu değil)"),
                "available": ConversionEngine.LIBREOFFICE in available_engines,
                "engine": ConversionEngine.LIBREOFFICE,
            },
        ]

    @Property(int, notify=selectedEngineIndexChanged)
    def selectedEngineIndex(self) -> int:
        c = self._active_converter
        if not isinstance(c, IEngineSelectable):
            return 0
        active = c.active_engine
        if active == ConversionEngine.MS_OFFICE:
            return 1
        elif active == ConversionEngine.LIBREOFFICE:
            return 2
        return 0

    @Property(str, notify=engineStatusChanged)
    def engineStatusText(self) -> str:
        c = self._active_converter
        return f"●  {c.active_engine_name}"

    @Property(bool, notify=engineStatusChanged)
    def engineIsAvailable(self) -> bool:
        return self._active_converter.is_available

    @Property(bool, constant=True)
    def isOcrAvailable(self) -> bool:
        from core.converters.ocr_engine import OcrEngine
        return OcrEngine().is_available()

    @Property(str, notify=outputDirChanged)
    def outputDir(self) -> str:
        return str(self._output_dir) if self._output_dir else ""

    @Property(int, notify=dpiChanged)
    def dpi(self) -> int:
        return self._dpi

    @Property(int, notify=qualityChanged)
    def quality(self) -> int:
        return self._quality

    @Property(bool, notify=overwriteExistingChanged)
    def overwriteExisting(self) -> bool:
        return self._overwrite_existing

    @Property(bool, notify=isMergeModeChanged)
    def isMergeMode(self) -> bool:
        return self._is_merge_mode and isinstance(self._active_converter, IMergeConverter)

    @Property(str, notify=pageRangeChanged)
    def pageRange(self) -> str:
        return self._page_range

    @Property(bool, notify=isConvertingChanged)
    def isConverting(self) -> bool:
        return self._is_converting

    @Property(int, notify=progressChanged)
    def progressValue(self) -> int:
        return self._progress_val

    @Property(int, notify=progressChanged)
    def progressMax(self) -> int:
        return self._progress_max

    @Property(int, notify=progressChanged)
    def progressPercent(self) -> int:
        if self._progress_max <= 0:
            return 0
        return int((self._progress_val / self._progress_max) * 100)

    @Property(str, notify=statusMessageChanged)
    def statusMessage(self) -> str:
        return self._status_message

    @Property(dict, notify=summaryDataChanged)
    def summaryData(self) -> Dict[str, Any]:
        return self._summary_data

    @Property(bool, notify=showSummaryModalChanged)
    def showSummaryModal(self) -> bool:
        return self._show_summary_modal

    @Property(str, constant=True)
    def appIconUrl(self) -> str:
        path = get_resource_path("assets/icons/app_icon.svg")
        return QUrl.fromLocalFile(path).toString()

    # ================================================================== #
    #  SLOTS                                                               #
    # ================================================================== #

    @Slot()
    def toggleTheme(self) -> None:
        new_mode = "light" if self._theme_mode == "dark" else "dark"
        self.setTheme(new_mode)

    @Slot(str)
    def setTheme(self, mode: str) -> None:
        mode = mode.lower()
        if mode not in ("dark", "light"):
            return
        if self._theme_mode != mode:
            self._theme_mode = mode
            self._settings.save_theme_mode(mode)
            self.themeModeChanged.emit(mode)

    @Slot(int)
    def selectConverter(self, index: int) -> None:
        if not (0 <= index < len(self._converters)):
            return
        if self._active_index == index:
            return

        self._active_index = index
        self._active_converter = self._converters[index]

        # Temizlik ve resetleme
        self._file_model.clear()
        self._is_merge_mode = False
        self._page_range = ""

        # Tercih kaydı
        self._settings.save_converter_info(
            self._active_converter.source_extension,
            self._active_converter.target_extension,
            self._active_converter.__class__.__name__,
        )

        self.currentConverterIndexChanged.emit(self._active_index)
        self.currentConverterChanged.emit()
        self.engineListChanged.emit()
        self.selectedEngineIndexChanged.emit(self.selectedEngineIndex)
        self.engineStatusChanged.emit()
        self.isMergeModeChanged.emit(self.isMergeMode)
        self.pageRangeChanged.emit(self._page_range)

    @Slot(int)
    def selectEngine(self, index: int) -> None:
        c = self._active_converter
        if not isinstance(c, IEngineSelectable):
            return

        engine = None
        if index == 1:
            engine = ConversionEngine.MS_OFFICE
        elif index == 2:
            engine = ConversionEngine.LIBREOFFICE

        success = c.set_preferred_engine(engine)
        if engine is not None and not success:
            hint = (
                "pip install pywin32"
                if engine == ConversionEngine.MS_OFFICE
                else "https://www.libreoffice.org/download"
            )
            self.notificationRequested.emit(
                "Motor Kullanılamıyor",
                f"Seçilen motor bu sistemde mevcut değil.\n\n{hint}",
            )

        self.selectedEngineIndexChanged.emit(index)
        self.engineStatusChanged.emit()

    @Slot(int)
    def setDpi(self, dpi: int) -> None:
        if self._dpi != dpi:
            self._dpi = max(72, min(600, dpi))
            self._settings.save_quality_options(
                self._dpi, self._quality, self._overwrite_existing
            )
            self.dpiChanged.emit(self._dpi)

    @Slot(int)
    def setQuality(self, quality: int) -> None:
        if self._quality != quality:
            self._quality = max(1, min(100, quality))
            self._settings.save_quality_options(
                self._dpi, self._quality, self._overwrite_existing
            )
            self.qualityChanged.emit(self._quality)

    @Slot(bool)
    def setOverwriteExisting(self, val: bool) -> None:
        if self._overwrite_existing != val:
            self._overwrite_existing = val
            self._settings.save_quality_options(
                self._dpi, self._quality, self._overwrite_existing
            )
            self.overwriteExistingChanged.emit(val)

    @Slot(bool)
    def setIsMergeMode(self, val: bool) -> None:
        if self._is_merge_mode != val:
            self._is_merge_mode = val
            self.isMergeModeChanged.emit(self.isMergeMode)

    @Slot(str)
    def setPageRange(self, val: str) -> None:
        if self._page_range != val:
            self._page_range = val
            self.pageRangeChanged.emit(val)

    # ── Dosya Ekleme / Kaldırma ───────────────────────────────────────
    @Slot(list)
    def addFilesFromUrls(self, urls: List[Any]) -> None:
        """QML DropZone veya FileDialog'dan gelen QUrl/string listesini işler."""
        paths: List[Path] = []
        accepted = {e.lower() for e in self._active_converter.accepted_extensions}

        for u in urls:
            local_path_str = ""
            if isinstance(u, QUrl):
                local_path_str = u.toLocalFile()
            elif isinstance(u, str):
                if u.startswith("file:///"):
                    local_path_str = QUrl(u).toLocalFile()
                else:
                    local_path_str = u

            if not local_path_str:
                continue

            p = Path(local_path_str)
            if p.is_dir():
                paths.extend(collect_files(p, accepted))
            elif p.suffix.lower() in accepted:
                paths.append(p)

        if paths:
            self._file_model.add_files(paths)

    @Slot(int)
    def removeFile(self, index: int) -> None:
        self._file_model.remove_at(index)

    @Slot()
    def clearFiles(self) -> None:
        self._file_model.clear()

    @Slot()
    def openFileDialog(self) -> None:
        """Native dosya seçici penceresi açar."""
        display_name = self._active_converter.display_name.split("→")[0].strip()
        patterns = " ".join(
            f"*{ext}" for ext in self._active_converter.accepted_extensions
        )
        filters = f"{display_name} Dosyaları ({patterns});;Tüm Dosyalar (*.*)"
        file_paths, _ = QFileDialog.getOpenFileNames(
            None,
            f"{display_name} Dosyaları Seç",
            str(Path.home()),
            filters,
        )
        if file_paths:
            self._file_model.add_files([Path(p) for p in file_paths])

    @Slot()
    def browseOutputDir(self) -> None:
        """Çıktı klasörü seçici penceresi açar."""
        selected_dir = QFileDialog.getExistingDirectory(
            None,
            "Çıktı Klasörü Seç",
            str(self._output_dir or Path.home()),
        )
        if selected_dir:
            self._output_dir = Path(selected_dir)
            self._settings.save_output_dir(self._output_dir)
            self.outputDirChanged.emit(str(self._output_dir))

    @Slot()
    def clearOutputDir(self) -> None:
        """Çıktı klasörünü varsayılana döndürür."""
        self._output_dir = None
        self._settings.save_output_dir(None)
        self.outputDirChanged.emit("")

    # ── Dönüşüm Kontrolü ──────────────────────────────────────────────
    @Slot()
    def startConversion(self) -> None:
        files = self._file_model.all_paths()
        if not files or self._is_converting:
            return

        if not self._active_converter.is_available:
            self.notificationRequested.emit(
                "Motor Bulunamadı",
                f"{self._active_converter.display_name} dönüşümü için gerekli araç kurulu değil.\n\n"
                + self._active_converter.unavailable_hint,
            )
            return

        options = ConversionOptions(
            output_dir=self._output_dir,
            dpi=self._dpi,
            quality=self._quality,
            overwrite_existing=self._overwrite_existing,
            page_range=self._page_range.strip() or None,
        )

        self._cancel_requested = False
        self._set_converting(True)
        self._file_model.reset_statuses()
        self._progress_val = 0
        self._progress_max = len(files)
        self._status_message = f"Dönüştürülüyor... 0/{len(files)}"
        self.progressChanged.emit()
        self.statusMessageChanged.emit(self._status_message)

        self._last_was_merge = (
            self.isMergeMode and isinstance(self._active_converter, IMergeConverter)
        )

        if self._last_was_merge:
            worker = QmlMergeWorker(files, self._active_converter, options, self)
            worker.merge_completed.connect(self._on_batch_done)
            self._active_worker = worker
            worker.start()
        else:
            worker = QmlConversionWorker(files, self._active_converter, options, self)
            worker.progress.connect(self._on_progress)
            worker.file_completed.connect(self._on_file_done)
            worker.batch_completed.connect(self._on_batch_done)
            self._active_worker = worker
            worker.start()

    @Slot()
    def cancelConversion(self) -> None:
        if self._is_converting and self._active_worker:
            self._cancel_requested = True
            self._active_worker.cancel()
            self._status_message = "İptal ediliyor..."
            self.statusMessageChanged.emit(self._status_message)

    def _on_progress(self, completed: int, total: int) -> None:
        self._progress_val = completed
        self._progress_max = total
        self._status_message = f"Dönüştürülüyor... {completed}/{total}"
        self.progressChanged.emit()
        self.statusMessageChanged.emit(self._status_message)

    def _on_file_done(self, result: ConversionResult) -> None:
        self._file_model.mark_result(result)

    def _on_batch_done(self, batch: BatchConversionResult) -> None:
        self._set_converting(False)
        self._progress_val = batch.total
        self.progressChanged.emit()

        if self._last_was_merge:
            status = (
                "✅ Dosyalar tek çıktıda birleştirildi"
                if batch.all_succeeded
                else f"⚠ Birleştirme başarısız: {batch.results[0].error_message}"
            )
        elif self._cancel_requested:
            total_files = self._file_model.count()
            status = f"⚠ İptal edildi — {batch.total}/{total_files} dosya işlendi"
        elif batch.all_succeeded:
            status = f"✅ {batch.success_count}/{batch.total} dosya başarıyla dönüştürüldü"
        else:
            status = f"⚠ {batch.success_count} başarılı, {batch.failure_count} hatalı"

        self._status_message = status
        self.statusMessageChanged.emit(self._status_message)

        # SummaryModal verisi hazırla
        results_list = []
        for r in batch.results:
            results_list.append(
                {
                    "fileName": r.file_name,
                    "success": r.success,
                    "outputPath": str(r.output_path) if r.output_path else "",
                    "outputName": r.output_path.name if r.output_path else "",
                    "errorMessage": r.error_message or "",
                    "elapsedSeconds": r.elapsed_seconds,
                    "pageCount": r.page_count,
                }
            )

        self._summary_data = {
            "total": batch.total,
            "successCount": batch.success_count,
            "failureCount": batch.failure_count,
            "allSucceeded": batch.all_succeeded,
            "results": results_list,
        }
        self.summaryDataChanged.emit()
        self._show_summary_modal = True
        self.showSummaryModalChanged.emit(True)

    def _set_converting(self, converting: bool) -> None:
        self._is_converting = converting
        self.isConvertingChanged.emit(converting)

    # ── Summary Modal & Dışarı Açma ───────────────────────────────────
    @Slot()
    def closeSummaryModal(self) -> None:
        self._show_summary_modal = False
        self.showSummaryModalChanged.emit(False)

    @Slot()
    def openFirstOutputFolder(self) -> None:
        results = self._summary_data.get("results", [])
        for r in results:
            if r.get("success") and r.get("outputPath"):
                out_p = Path(r["outputPath"])
                self.openFolder(str(out_p.parent))
                break

    @Slot(str)
    def openFolder(self, path_str: str) -> None:
        if not path_str:
            return
        p = Path(path_str)
        if not p.exists():
            return
        system = platform.system()
        folder = str(p if p.is_dir() else p.parent)
        if system == "Windows":
            subprocess.Popen(["explorer", folder])
        elif system == "Darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    @Slot(int, int, int, int)
    def saveWindowGeometry(self, x: int, y: int, width: int, height: int) -> None:
        self._settings.save_window_rect(x, y, width, height)
