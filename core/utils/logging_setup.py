"""
Günlük (Log) Dosyası Kurulumu
===============================
Teknik hata ayrıntıları (traceback, kütüphane mesajları, harici program
çıktısı) kullanıcıya gösterilmez; bunun yerine dönen bir günlük dosyasına
yazılır. Konsolsuz exe'de `stderr` görünmediği için hata ayıklamanın tek
kaynağı bu dosyadır.

Konum, LibreOffice profiliyle aynı uygulama klasörü:
`%LOCALAPPDATA%\\FileConvert\\logs\\fileconvert.log`.

SRP : Yalnızca günlük yapılandırmasından sorumlu.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from core.utils.app_paths import user_data_dir

_configured_path: Optional[Path] = None


def log_dir() -> Path:
    return user_data_dir() / "logs"


def configure_logging(directory: Optional[Path] = None) -> Path:
    """
    Kök logger'a dönen dosya handler'ı ekler (1 MB × 3 dosya). Birden çok
    çağrıda handler çoğaltmaz. Günlük dosyasının yolunu döner.
    """
    global _configured_path
    if _configured_path is not None:
        return _configured_path

    target_dir = directory or log_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / "fileconvert.log"

    handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.addHandler(handler)
    if root.level == logging.NOTSET or root.level > logging.INFO:
        root.setLevel(logging.INFO)

    _configured_path = path
    return path


def current_log_path() -> Path:
    """Yapılandırılmışsa gerçek yol, değilse varsayılan konum."""
    return _configured_path or (log_dir() / "fileconvert.log")
