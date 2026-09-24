"""
FileConvert — Giriş Noktası (QML Sürümü)
============================================
PySide6 QML motorunu başlatır, AppBridge köprüsünü QML context'ine bağlar.
Eski UI dosyaları yedek olarak ui/ altında korunmuştur.
"""

import os
import sys
import traceback
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMessageBox

from core.utils.resource_helper import get_resource_path
from ui_qml.bridge.app_bridge import AppBridge
from ui_qml.bridge.app_settings import APP_NAME, ORG_NAME, QmlAppSettings


def _handle_exception(exc_type, exc_value, exc_tb):
    """Yakalanmamış exception'ları kullanıcıya gösterir."""
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(msg, file=sys.stderr)
    box = QMessageBox()
    box.setWindowTitle("Beklenmeyen Hata")
    box.setText(str(exc_value))
    box.setDetailedText(msg)
    box.setIcon(QMessageBox.Icon.Critical)
    box.exec()


def main() -> int:
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

    # Windows Görev Çubuğunda Özel İkonu Göstermek için AppUserModelID
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = "yusufygc.fileconvertpro.app.1.0.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)

    # İkon Yükleme (Öncelik: .ico -> .png -> .svg)
    ico_path = get_resource_path("assets/icons/app_icon.ico")
    png_path = get_resource_path("assets/icons/app_icon.png")
    svg_path = get_resource_path("assets/icons/app_icon.svg")

    if Path(ico_path).exists():
        app.setWindowIcon(QIcon(ico_path))
    elif Path(png_path).exists():
        app.setWindowIcon(QIcon(png_path))
    elif Path(svg_path).exists():
        app.setWindowIcon(QIcon(svg_path))

    sys.excepthook = _handle_exception

    settings = QmlAppSettings()
    x, y, width, height = settings.load_window_rect()

    bridge = AppBridge()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("bridge", bridge)

    from PySide6.QtCore import QUrl
    qml_file = get_resource_path("ui_qml/qml/Main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        print("Hata: QML dosyası yüklenemedi!", file=sys.stderr)
        return -1

    root_window = engine.rootObjects()[0]
    if x is not None and y is not None:
        root_window.setProperty("x", x)
        root_window.setProperty("y", y)
    root_window.setProperty("width", width)
    root_window.setProperty("height", height)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
