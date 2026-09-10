"""First-launch disclaimer gate, shown before the main window until accepted.

Acceptance is persisted via twrar.settings so it only shows once per
install - see gui_main.py for where this is invoked.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from twrar.metadata import DISCLAIMER_TEXT, PROJECT_NAME
from twrar.paths import APP_ROOT

LOGO_PATH = APP_ROOT / "assets" / "logo.png"


class DisclaimerDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Before you continue")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        if LOGO_PATH.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(LOGO_PATH)).scaledToHeight(96, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignHCenter)
            layout.addWidget(logo_label)

        title = QLabel(PROJECT_NAME)
        title.setAlignment(Qt.AlignHCenter)
        font = title.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        body = QLabel(DISCLAIMER_TEXT)
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignHCenter)
        body.setMinimumWidth(420)
        layout.addWidget(body)

        buttons = QDialogButtonBox()
        continue_btn = buttons.addButton("I understand - Continue", QDialogButtonBox.AcceptRole)
        buttons.addButton("Exit", QDialogButtonBox.RejectRole)
        continue_btn.setDefault(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
