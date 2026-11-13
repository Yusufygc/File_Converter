"""Proje kökünü sys.path'e ekler — `core`/`ui`/`tests` namespace paketleri
pytest'in çağırılma biçiminden (`pytest` vs `python -m pytest`) bağımsız
olarak import edilebilsin diye.

Ayrıca testlerin gerçek kullanıcı verisine (günlük, `updates.json`) ve
kayıt defterindeki uygulama ayarlarına dokunmaması için `FILECONVERT_HOME`
geçici bir klasöre yönlendirilir (bkz. core/utils/app_paths.py)."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("FILECONVERT_HOME", tempfile.mkdtemp(prefix="fileconvert_test_home_"))
os.environ.setdefault("FILECONVERT_NO_UPDATE_CHECK", "1")
