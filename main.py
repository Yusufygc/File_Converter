"""
FileConvert — Giriş Noktası (QML Sürümü)
============================================
PySide6 QML motorunu başlatır, AppBridge ve UpdateBridge köprülerini QML
context'ine bağlar.

Paketlenmiş exe bu dosyayı `packaging/launcher.py` üzerinden çağırır; o dosya
exe özetine girdiği için değişmez, değişen mantık burada durur.
"""

import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMessageBox

from core.utils.logging_setup import configure_logging, current_log_path
from core.utils.resource_helper import get_resource_path
from ui_qml.bridge.app_bridge import AppBridge
from ui_qml.bridge.app_settings import APP_NAME, ORG_NAME, QmlAppSettings
from ui_qml.bridge.update_bridge import UpdateBridge
from version import __version__

STARTUP_UPDATE_CHECK_DELAY_MS = 3000


def _handle_exception(exc_type, exc_value, exc_tb):
    """
    Yakalanmamış exception'ı günlüğe yazar, kullanıcıya teknik terim
    içermeyen bir mesaj gösterir. Traceback ve exception metni önceden
    doğrudan pencerede görünüyordu; artık yalnızca günlük dosyasında.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    logging.getLogger("fileconvert").critical(
        "Yakalanmamış hata", exc_info=(exc_type, exc_value, exc_tb)
    )
    box = QMessageBox()
    box.setWindowTitle("Beklenmeyen Hata")
    box.setText(
        "Beklenmeyen bir hata oluştu. Uygulamayı yeniden başlatmanız gerekebilir."
    )
    box.setInformativeText(
        f"Sorunu bildirmek isterseniz günlük dosyasını ekleyin:\n{current_log_path()}"
    )
    box.setIcon(QMessageBox.Icon.Critical)
    box.exec()


def main() -> int:
    try:
        configure_logging()
    except OSError:
        # Günlük klasörü oluşturulamazsa (izin/salt okunur profil) uygulama
        # yine de açılmalı; yalnızca dosyaya kayıt olmaz.
        pass
    logging.getLogger("fileconvert").info("FileConvert %s başlatılıyor", __version__)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

    # Windows Görev Çubuğunda Özel İkonu Göstermek için AppUserModelID
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = "yusufygc.fileconvert.app.1.0.0"
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
    update_bridge = UpdateBridge()
    update_bridge.quitRequested.connect(app.quit)
    app.aboutToQuit.connect(update_bridge.shutdown)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("bridge", bridge)
    engine.rootContext().setContextProperty("updateBridge", update_bridge)

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

    # Pencere çizildikten sonra tek istekle yeni sürüm denetimi (testlerde değil, yalnızca burada).
    QTimer.singleShot(STARTUP_UPDATE_CHECK_DELAY_MS, update_bridge.startupCheck)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
