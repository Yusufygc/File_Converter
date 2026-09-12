"""
FileConvert Pro — Giriş Noktası
================================
Uygulamayı başlatır, global exception handler kurar.
"""

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from ui.styles.theme import MAIN_STYLE
from ui.app_settings import ORG_NAME, APP_NAME


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
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setStyleSheet(MAIN_STYLE)

    sys.excepthook = _handle_exception

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
