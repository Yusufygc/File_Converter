"""
PyInstaller paketleme regresyon testleri.

`core/` altındaki paketlerde `__init__.py` yokken (namespace package)
`collect_submodules('core')` alt modülleri listeleyemiyordu; dinamik
keşfedilen converter'lar exe'ye hiç girmiyor, paketlenmiş uygulamada
yalnızca doğrudan import edilen PPTX→PDF görünüyordu.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = PROJECT_ROOT / "core"


def test_every_core_package_is_a_regular_package():
    package_dirs = [
        d for d in [CORE_DIR, *CORE_DIR.rglob("*")]
        if d.is_dir() and d.name != "__pycache__"
    ]
    missing = [str(d.relative_to(PROJECT_ROOT)) for d in package_dirs if not (d / "__init__.py").exists()]
    assert missing == []


def test_pyinstaller_collects_every_converter_module():
    on_disk = {
        f"core.converters.{p.stem}"
        for p in (CORE_DIR / "converters").glob("*.py")
        if p.stem != "__init__"
    }
    collected = set(collect_submodules("core.converters"))

    assert on_disk - collected == set()
