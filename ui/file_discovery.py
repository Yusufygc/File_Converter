"""
Klasör Tarama
==============
Sürüklenen bir klasörden uygun uzantılı dosyaları toplar. Saf
`pathlib` mantığı, Qt'den bağımsız — `DropZoneWidget` bunu çağırır
ama mantığın kendisi Qt gerektirmediği için `tests/`'teki hızlı,
Qt'siz test paketine katılabilir (`ui/icon_map.py`'nin de izlediği
"UI-katmanında yaşayan ama Qt'siz saf mantık" deseni).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


def collect_files(directory: Path, accepted_extensions: Iterable[str]) -> List[Path]:
    """Klasördeki (alt klasörler dahil) uygun uzantılı dosyaları sıralı döndürür."""
    accepted = {ext.lower() for ext in accepted_extensions}
    return sorted(
        p for p in directory.rglob("*")
        if p.is_file() and p.suffix.lower() in accepted
    )
