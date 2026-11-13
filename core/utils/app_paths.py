"""
Kullanıcı Veri Klasörü
========================
Günlük dosyası, güncelleme tercihleri (`updates.json`) ve LibreOffice
profili gibi uygulamaya ait kullanıcı verisinin tek kökü:
`%LOCALAPPDATA%\\FileConvert`.

`FILECONVERT_HOME` ortam değişkeni bu kökü değiştirir. Testler ve derleme
sonrası exe denemesi (`build_verify.py`) bununla gerçek kullanıcı verisine
ve kayıt defterindeki ayarlara dokunmadan çalışır.

SRP : Yalnızca kullanıcı veri klasörünün yerini belirlemekten sorumlu.
"""

from __future__ import annotations

import os
from pathlib import Path

HOME_ENV = "FILECONVERT_HOME"


def home_override() -> Path | None:
    """`FILECONVERT_HOME` ayarlıysa o klasör, değilse None."""
    value = os.environ.get(HOME_ENV, "").strip()
    return Path(value) if value else None


def user_data_dir() -> Path:
    """Kullanıcı veri klasörü (yoksa oluşturulur)."""
    path = home_override()
    if path is None:
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".cache")
        path = Path(base) / "FileConvert"
    path.mkdir(parents=True, exist_ok=True)
    return path
