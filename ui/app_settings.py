"""
Kullanıcı Tercihleri (QSettings)
==================================
Pencere geometrisi, son seçilen dönüşüm türü ve seçenek paneli durumunu
kalıcı olarak saklar. Tamamen UI-katmanına özeldir — `core/` bu dosyayı
hiç bilmez, `QSettings` gibi Qt'ye özgü bir mekanizma `core/`'a sızmaz.

`main.py`'de `QApplication.setOrganizationName`/`setApplicationName`
zaten çağrıldığı için `QSettings()` bare constructor'ı bunları otomatik
kullanır — burada ayrıca belirtmeye gerek yok.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtCore import QByteArray, QSettings

# Org/app adı için tek kaynak — main.py (QApplication kurulumu) ve
# theme.py (tema tercihini QApplication'dan bağımsız, import zamanında
# okumak için) burayı kullanır. İki yerde ayrı ayrı hardcoded olmasını
# önler.
ORG_NAME = "YusufDev"
APP_NAME = "FileConvert Pro"

THEME_MODE_KEY = "theme/mode"


class AppSettings:
    """`QSettings`'i sarmalayan, uygulamaya özel anahtarlarla çalışan ince katman."""

    def __init__(self):
        self._qs = QSettings()

    # ------------------------------------------------------------------ #
    #  Pencere geometrisi                                                  #
    # ------------------------------------------------------------------ #

    def save_window_geometry(self, geometry: QByteArray) -> None:
        self._qs.setValue("window/geometry", geometry)

    def load_window_geometry(self) -> Optional[QByteArray]:
        value = self._qs.value("window/geometry")
        return value if value else None

    # ------------------------------------------------------------------ #
    #  Aktif converter                                                     #
    # ------------------------------------------------------------------ #

    def save_converter_key(self, source_ext: str, target_ext: str) -> None:
        self._qs.setValue("converter/source_ext", source_ext)
        self._qs.setValue("converter/target_ext", target_ext)

    def load_converter_key(self) -> Optional[Tuple[str, str]]:
        source_ext = self._qs.value("converter/source_ext")
        target_ext = self._qs.value("converter/target_ext")
        if not source_ext or not target_ext:
            return None
        return (str(source_ext), str(target_ext))

    # ------------------------------------------------------------------ #
    #  Seçenek paneli durumu                                               #
    # ------------------------------------------------------------------ #

    def save_output_dir(self, path: Optional[Path]) -> None:
        self._qs.setValue("options/output_dir", str(path) if path else "")

    def load_output_dir(self) -> Optional[Path]:
        value = self._qs.value("options/output_dir", "")
        return Path(value) if value else None

    def save_quality_options(self, dpi: int, quality: int, overwrite: bool) -> None:
        self._qs.setValue("options/dpi", dpi)
        self._qs.setValue("options/quality", quality)
        self._qs.setValue("options/overwrite", overwrite)

    def load_quality_options(self) -> Tuple[int, int, bool]:
        dpi = int(self._qs.value("options/dpi", 150))
        quality = int(self._qs.value("options/quality", 90))
        overwrite_raw = self._qs.value("options/overwrite", True)
        # QSettings backend'e göre bool bazen "true"/"false" string'i olarak dönebilir.
        if isinstance(overwrite_raw, bool):
            overwrite = overwrite_raw
        else:
            overwrite = str(overwrite_raw).strip().lower() == "true"
        return dpi, quality, overwrite

    # ------------------------------------------------------------------ #
    #  Tema                                                                #
    # ------------------------------------------------------------------ #

    def save_theme_mode(self, mode: str) -> None:
        self._qs.setValue(THEME_MODE_KEY, mode)

    def load_theme_mode(self) -> str:
        return str(self._qs.value(THEME_MODE_KEY, "dark")).lower()
