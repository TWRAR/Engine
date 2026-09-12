"""Red-tinted light/dark theme for the GUI, matching twrar.stuxie.dev's
palette (same tokens, translated from CSS custom properties to QSS).
"""
from __future__ import annotations

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

_LIGHT = {
    "bg": "#fbf6f6",
    "bg_alt": "#f5eae9",
    "panel": "#ffffff",
    "text": "#201717",
    "text_dim": "#5a4c4c",
    "muted": "#8c7c7c",
    "border": "#ecd8d7",
    "accent": "#dc2626",
    "accent_hover": "#b91c1c",
    "accent_contrast": "#ffffff",
}

_DARK = {
    "bg": "#1a1414",
    "bg_alt": "#201818",
    "panel": "#251c1c",
    "text": "#f5efee",
    "text_dim": "#c4a9a9",
    "muted": "#8c7373",
    "border": "#3a2a2a",
    "accent": "#f87171",
    "accent_hover": "#fca5a5",
    "accent_contrast": "#1a1414",
}

_QSS_TEMPLATE = """
QWidget {{
    background-color: {bg};
    color: {text};
    selection-background-color: {accent};
    selection-color: {accent_contrast};
}}
QMainWindow, QDialog {{
    background-color: {bg};
}}
QTabWidget::pane {{
    border: 1px solid {border};
    background: {bg};
    top: -1px;
}}
QTabBar::tab {{
    background: {bg_alt};
    color: {text_dim};
    padding: 6px 16px;
    border: 1px solid {border};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background: {panel};
    color: {text};
    /* Qt's QSS engine doesn't reliably apply a pseudo-state rule that only
       overrides one sub-property (border-color) of a shorthand (border)
       set in the base rule -- redeclaring the full "border" shorthand
       here, not just its color, is what actually takes effect. */
    border: 1px solid {accent};
    border-bottom: none;
}}
QTabBar::tab:hover:!selected {{
    color: {text};
}}
QPushButton {{
    background: {panel};
    color: {text};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    /* See QTabBar::tab:selected above - same border-shorthand gotcha. */
    border: 1px solid {accent};
}}
QPushButton:pressed {{
    background: {bg_alt};
}}
QPushButton:disabled {{
    color: {muted};
    border: 1px solid {border};
}}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit,
QListWidget, QTableWidget {{
    background: {panel};
    color: {text};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 2px 4px;
}}
QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {accent};
}}
QComboBox::drop-down {{
    border: none;
}}
QHeaderView::section {{
    background: {bg_alt};
    color: {text_dim};
    border: 1px solid {border};
    padding: 4px 6px;
}}
QListWidget::item:selected, QTableWidget::item:selected {{
    background: {accent};
    color: {accent_contrast};
}}
QCheckBox, QRadioButton, QLabel {{
    color: {text};
}}
QGroupBox {{
    border: 1px solid {border};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 6px;
}}
QGroupBox::title {{
    color: {text_dim};
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}
QScrollBar:vertical {{
    background: {bg_alt};
    width: 12px;
}}
QScrollBar:horizontal {{
    background: {bg_alt};
    height: 12px;
}}
QScrollBar::handle {{
    background: {border};
    border-radius: 5px;
    min-height: 20px;
    min-width: 20px;
}}
QScrollBar::handle:hover {{
    background: {muted};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
    width: 0;
}}
QSplitter::handle {{
    background: {border};
}}
"""


def is_dark_mode(app: QApplication) -> bool:
    """Best-effort dark-mode detection that works across PySide6 versions:
    prefers Qt 6.5+'s color-scheme hint, falls back to checking the
    inherited palette's window lightness.
    """
    style_hints = app.styleHints()
    color_scheme = getattr(style_hints, "colorScheme", None)
    if color_scheme is not None:
        scheme = color_scheme()
        if scheme.name == "Dark":
            return True
        if scheme.name == "Light":
            return False
    return app.palette().color(QPalette.ColorRole.Window).lightness() < 128


def tokens(app: QApplication) -> dict[str, str]:
    return _DARK if is_dark_mode(app) else _LIGHT


def stylesheet(app: QApplication) -> str:
    return _QSS_TEMPLATE.format(**tokens(app))


def accent_color(app: QApplication) -> str:
    return tokens(app)["accent"]
