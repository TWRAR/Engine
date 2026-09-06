import asyncio
import sys
from pathlib import Path

import qasync
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog

from automator.settings import confirm_disclaimer, load_settings
from gui.disclaimer import DisclaimerDialog
from gui.main_window import MainWindow

ICON_PATH = Path(__file__).resolve().parent / "assets" / "icon.ico"


def main() -> None:
    if sys.platform == "win32":
        # Without an explicit AppUserModelID, Windows groups this window's
        # taskbar button under the launching python.exe's own icon instead
        # of the one set below via setWindowIcon() - this is what actually
        # controls the taskbar/Alt-Tab icon, setWindowIcon() alone does not.
        import ctypes

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("StuxieDev.SiteAutomator")
        except OSError:
            pass

    app = QApplication(sys.argv)
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    if not load_settings()["disclaimer_confirmed"]:
        if DisclaimerDialog().exec() != QDialog.Accepted:
            return
        confirm_disclaimer()

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    if ICON_PATH.exists():
        window.setWindowIcon(QIcon(str(ICON_PATH)))
    window.resize(1300, 850)
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
