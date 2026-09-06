import asyncio
import sys
from pathlib import Path

import qasync
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

ICON_PATH = Path(__file__).resolve().parent / "assets" / "icon.ico"


def main() -> None:
    app = QApplication(sys.argv)
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
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
