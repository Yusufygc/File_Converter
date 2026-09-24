"""
QML App Settings
================
QSettings sarmalayıcısı. Tema, pencere boyutu, son seçilen converter ve
seçenek durumlarını kalıcı olarak saklar.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtCore import QSettings

ORG_NAME = "YusufDev"
APP_NAME = "FileConvert"

THEME_MODE_KEY = "theme/mode"


class QmlAppSettings:
    """Kullanıcı tercihlerini saklayan QSettings katmanı."""

    def __init__(self):
        self._qs = QSettings(ORG_NAME, APP_NAME)

    # ── Tema ──────────────────────────────────────────────────────────
    def save_theme_mode(self, mode: str) -> None:
        self._qs.setValue(THEME_MODE_KEY, mode.lower())

    def load_theme_mode(self) -> str:
        mode = self._qs.value(THEME_MODE_KEY, "dark")
        return str(mode).lower() if mode else "dark"

    # ── Pencere Geometrisi ────────────────────────────────────────────
    def save_window_rect(self, x: int, y: int, width: int, height: int) -> None:
        self._qs.setValue("window/x", x)
        self._qs.setValue("window/y", y)
        self._qs.setValue("window/width", width)
        self._qs.setValue("window/height", height)

    def load_window_rect(self) -> Tuple[Optional[int], Optional[int], int, int]:
        x = self._qs.value("window/x", None)
        y = self._qs.value("window/y", None)
        width = int(self._qs.value("window/width", 1100))
        height = int(self._qs.value("window/height", 760))
        return (int(x) if x is not None else None,
                int(y) if y is not None else None,
                max(960, width),
                max(680, height))

    # ── Aktif Converter ───────────────────────────────────────────────
    def save_converter_info(self, source_ext: str, target_ext: str, class_name: str) -> None:
        self._qs.setValue("converter/source_ext", source_ext)
        self._qs.setValue("converter/target_ext", target_ext)
        self._qs.setValue("converter/class_name", class_name)

    def load_converter_info(self) -> Optional[Tuple[str, str, Optional[str]]]:
        source_ext = self._qs.value("converter/source_ext")
        target_ext = self._qs.value("converter/target_ext")
        class_name = self._qs.value("converter/class_name", None)
        if not source_ext or not target_ext:
            return None
        return (str(source_ext), str(target_ext), str(class_name) if class_name else None)

    # ── Seçenekler ────────────────────────────────────────────────────
    def save_output_dir(self, path: Optional[Path]) -> None:
        self._qs.setValue("options/output_dir", str(path) if path else "")

    def load_output_dir(self) -> Optional[Path]:
        val = self._qs.value("options/output_dir", "")
        return Path(val) if val else None

    def save_quality_options(self, dpi: int, quality: int, overwrite: bool) -> None:
        self._qs.setValue("options/dpi", dpi)
        self._qs.setValue("options/quality", quality)
        self._qs.setValue("options/overwrite", overwrite)

    def load_quality_options(self) -> Tuple[int, int, bool]:
        dpi = int(self._qs.value("options/dpi", 150))
        quality = int(self._qs.value("options/quality", 90))
        overwrite_raw = self._qs.value("options/overwrite", True)
        if isinstance(overwrite_raw, bool):
            overwrite = overwrite_raw
        else:
            overwrite = str(overwrite_raw).strip().lower() == "true"
        return dpi, quality, overwrite
