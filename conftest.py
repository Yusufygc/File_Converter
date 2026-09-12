"""Proje kökünü sys.path'e ekler — `core`/`ui`/`tests` namespace paketleri
pytest'in çağırılma biçiminden (`pytest` vs `python -m pytest`) bağımsız
olarak import edilebilsin diye."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
