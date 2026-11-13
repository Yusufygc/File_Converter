"""
PyInstaller ile FileConvert.exe derler ("kararlı exe": her sürümde bayt bayt aynı çıktı).

Kararlı exe yalnızca sabit başlatıcıyı (`packaging/launcher.py`) içerir; uygulama kodu `_internal` altında `.pyc`
olarak durur (`--debug=noarchive`). `SOURCE_DATE_EPOCH` ve sabit sürüm kaynağı PE zaman damgasını/sürüm bilgisini
sabitler. Çıktının SHA-256 özeti `packaging/launcher.sha256` ile karşılaştırılır; farklıysa derleme DURUR
(bkz. docs/wiki/paketleme.md, "Kararlı exe").

Önceki `fileconvert.spec` bunun yerini aldı: bağımsız değişkenler burada, testle sabitlenir
(tests/test_release_packaging.py). Bağımsız değişken eklemek/çıkarmak exe özetini değiştirebilir.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
APP_EXE_NAME = "FileConvert"
LAUNCHER_EPOCH = 1700000000  # DEĞİŞTİRME (bilerek yeni özet denemenin tek yolu)
HASH_FILE = ROOT / "packaging" / "launcher.sha256"

# Converter'lar `pkgutil` ile dinamik keşfedilir, PDF→Markdown/Excel paketleri geç import edilir:
# statik analiz göremez, açıkça toplanır.
COLLECT_SUBMODULES = ("core", "ui_qml", "pdf2docx", "pymupdf4llm", "openpyxl", "tabulate")
COLLECT_DATA = ("pdf2docx", "pymupdf4llm", "openpyxl")
HIDDEN_IMPORTS = ("win32com", "win32com.client", "fitz", "docx", "pytesseract", "PIL")

# Uygulamanın kullanmadığı modüller paketten çıkarılır (boyut). QML'in kullandığı modüller (Quick, Controls,
# Layouts) ve QtWidgets (QMessageBox, QFileDialog) çıkarılmaz.
# pymupdf.layout (ONNX düzen modeli) ve yalnızca onun çektiği onnxruntime/sympy/networkx/mpmath da çıkarılır:
# PDF→Markdown klasik modda çalışır (bkz. core/converters/pdf_to_markdown.py).
EXCLUDED_MODULES = (
    "tkinter", "matplotlib", "scipy", "pytest",
    "pymupdf.layout", "onnxruntime", "sympy", "networkx", "mpmath",
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineQuick", "PySide6.QtWebEngineWidgets", "PySide6.QtWebChannel",
    "PySide6.QtWebSockets", "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DInput", "PySide6.Qt3DLogic",
    "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras", "PySide6.QtQuick3D", "PySide6.QtCharts",
    "PySide6.QtDataVisualization", "PySide6.QtGraphs", "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtDesigner", "PySide6.QtHelp", "PySide6.QtLocation",
    "PySide6.QtPositioning", "PySide6.QtBluetooth", "PySide6.QtNfc", "PySide6.QtSensors", "PySide6.QtSerialPort",
    "PySide6.QtSerialBus", "PySide6.QtTest", "PySide6.QtSql", "PySide6.QtTextToSpeech", "PySide6.QtRemoteObjects",
    "PySide6.QtSpatialAudio", "PySide6.QtVirtualKeyboard",
)  # fmt: skip

# PyInstaller'ın Qt kancası `PySide6/qml` klasörünün tamamını ve bağlı DLL'leri toplar. Kullanılmayanlar
# derlemeden sonra silinir; silinenler exe'nin dışındadır, kararlı exe özeti etkilenmez.
UNUSED_QML_DIRS = (
    "Qt3D", "Qt5Compat", "QtCharts", "QtDataVisualization", "QtGraphs", "QtLocation", "QtMultimedia",
    "QtPositioning", "QtQuick3D", "QtRemoteObjects", "QtScxml", "QtSensors", "QtTest", "QtTextToSpeech",
    "QtWebChannel", "QtWebEngine", "QtWebSockets", "QtWebView",
)  # fmt: skip
UNUSED_DLL_PREFIXES = (
    "Qt6WebEngine", "Qt6Pdf", "Qt63D", "Qt6Quick3D", "Qt6Charts", "Qt6DataVisualization", "Qt6Graphs",
    "Qt6Location", "Qt6Multimedia", "Qt6Positioning", "Qt6RemoteObjects", "Qt6Scxml", "Qt6Sensors",
    "Qt6TextToSpeech", "Qt6WebChannel", "Qt6WebSockets", "Qt6WebView", "Qt6SpatialAudio", "Qt6Test",
    "Qt6Designer", "Qt6Help", "Qt6Bluetooth", "Qt6Nfc", "Qt6SerialPort", "Qt6SerialBus", "Qt6Sql",
    "QtWebEngineProcess",
)  # fmt: skip
UNUSED_PACKAGE_DIRS = ("translations", "resources")  # Qt çevirileri yüklenmiyor; WebEngine kaynakları


def executable_path() -> Path:
    return ROOT / "dist" / APP_EXE_NAME / f"{APP_EXE_NAME}.exe"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pyinstaller_arguments(root: Path = ROOT) -> list[str]:
    """Özeti belirleyen bağımsız değişkenler (testle sabitlenir)."""
    sep = os.pathsep
    return [
        str(root / "packaging" / "launcher.py"),
        f"--paths={root}",  # giriş betiği packaging/ altında: uygulama modülleri (main, core, ui_qml) kökten bulunur
        f"--name={APP_EXE_NAME}",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--noupx",  # UPX DLL imzalarını bozar, antivirüs yanlış pozitifini artırır
        "--debug=noarchive",  # modüller .pyc olarak _internal altında: sürümle değişen kod exe'yi değiştirmez
        *(f"--collect-submodules={package}" for package in COLLECT_SUBMODULES),
        *(f"--collect-data={package}" for package in COLLECT_DATA),
        *(f"--hidden-import={module}" for module in HIDDEN_IMPORTS),
        *(f"--exclude-module={module}" for module in EXCLUDED_MODULES),
        f"--icon={root / 'assets' / 'icons' / 'app_icon.ico'}",
        f"--version-file={root / 'packaging' / 'launcher_version_info.txt'}",
        f"--distpath={root / 'dist'}",
        f"--workpath={root / 'build'}",
        f"--specpath={root / 'build'}",
        f"--add-data={root / 'assets'}{sep}assets",
        f"--add-data={root / 'ui_qml' / 'qml'}{sep}ui_qml/qml",
    ]


def is_unused(relative: str) -> bool:
    """`PySide6/...` altındaki bağıl yol kullanılmayan bir Qt parçasına mı ait."""
    parts = relative.replace("\\", "/").split("/")
    if len(parts) < 2 or parts[0] != "PySide6":
        return False
    if parts[1] in UNUSED_PACKAGE_DIRS:
        return True
    if parts[1] == "qml":
        return len(parts) > 2 and parts[2] in UNUSED_QML_DIRS
    return len(parts) == 2 and parts[1].startswith(UNUSED_DLL_PREFIXES)


def prune(app_dir: Path) -> None:
    """Kullanılmayan Qt parçalarını `_internal/PySide6` altından siler (exe etkilenmez)."""
    internal = app_dir / "_internal"
    package = internal / "PySide6"
    if not package.is_dir():
        return
    qml_dir = package / "qml"
    candidates = [*package.iterdir(), *(qml_dir.iterdir() if qml_dir.is_dir() else [])]
    for path in candidates:
        if not is_unused(path.relative_to(internal).as_posix()):
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def check_launcher_hash(exe: Path, update: bool = False, hash_file: Path = HASH_FILE) -> None:
    """Derlenen exe özetini onaylanmışla karşılaştırır; farklıysa/dosya yoksa derlemeyi durdurur (`sys.exit(1)`)."""
    actual = sha256_of(exe)
    line = f"{actual} *{exe.name}\n"
    if update:
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(line, encoding="utf-8", newline="\n")
        print(f"[kapı] Onaylı exe özeti güncellendi: {actual}")
        return

    if not hash_file.is_file():
        print(
            "HATA: packaging/launcher.sha256 yok.\n"
            "  İlk kez derliyorsan: exe'yi bu makinede aç (build_verify.launch_check), sonra\n"
            "  `python build_installer.py --update-launcher-hash` ile özeti onayla ve commit'le.",
            file=sys.stderr,
        )
        sys.exit(1)

    approved = hash_file.read_text(encoding="utf-8").split()[0].lower()
    if approved != actual.lower():
        print(
            "HATA: Kararlı exe özeti DEĞİŞTİ; derleme ve yayın durduruldu.\n"
            f"  onaylanan: {approved}\n  derlenen : {actual}\n"
            "  Nedenleri: PyInstaller/Python sürümü, satır sonları, simge, sürüm kaynağı, giriş betiği,\n"
            "  PyInstaller bağımsız değişkenleri. Bilerek değiştirdiysen docs/wiki/paketleme.md\n"
            "  'Exe'yi bilerek değiştirmek' bölümünü uygula; bilmeden değiştiyse nedenini bul.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"[kapı] Kararlı exe özeti onaylananla aynı: {actual}")


def build_executable(update_hash: bool = False) -> Path:
    """PyInstaller'ı çalıştırır, özet kapısından geçirir ve exe yolunu döndürür."""
    import PyInstaller.__main__

    os.environ["SOURCE_DATE_EPOCH"] = str(LAUNCHER_EPOCH)  # PyInstaller'ı çalıştırmadan hemen önce
    PyInstaller.__main__.run(pyinstaller_arguments())
    prune(executable_path().parent)
    exe = executable_path()
    if not exe.is_file():
        print(f"HATA: exe oluşmadı: {exe}", file=sys.stderr)
        sys.exit(1)
    check_launcher_hash(exe, update=update_hash)
    return exe


if __name__ == "__main__":
    build_executable(update_hash="--update-launcher-hash" in sys.argv)
