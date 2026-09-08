"""Dynamic edit form for a step, built from automater.schema.ACTION_SCHEMA."""
from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QWidget,
)

from automater.schema import ACTION_SCHEMA

# Fields every action accepts, regardless of type - shown after the
# action-specific fields.
_COMMON_FIELDS = [
    {"name": "delay_before", "type": "int"},
    {"name": "delay_after", "type": "int"},
]


class StepForm(QWidget):
    def __init__(self, action_name: str, initial: Optional[dict] = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.action_name = action_name
        self.fields = list(ACTION_SCHEMA.get(action_name, [])) + _COMMON_FIELDS
        self.widgets: dict[str, QWidget] = {}
        initial = initial or {}

        layout = QFormLayout(self)
        for field in self.fields:
            widget = self._make_widget(field, initial.get(field["name"]))
            self.widgets[field["name"]] = widget
            label = field["name"] + (" *" if field.get("required") else "")
            layout.addRow(label, widget)

    def _make_widget(self, field: dict, value) -> QWidget:
        field_type = field["type"]

        if field_type == "bool":
            widget = QCheckBox()
            widget.setChecked(bool(value))
            return widget

        if field_type == "choice":
            widget = QComboBox()
            widget.addItem("")
            widget.addItems(field["choices"])
            if value:
                idx = widget.findText(str(value))
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            return widget

        if field_type == "text":
            widget = QPlainTextEdit()
            if value is not None:
                widget.setPlainText(str(value))
            return widget

        widget = QLineEdit()
        if value is not None:
            widget.setText(str(value))
        return widget

    def collect(self) -> dict:
        step: dict = {"action": self.action_name}
        for field in self.fields:
            name = field["name"]
            field_type = field["type"]
            widget = self.widgets[name]

            if field_type == "bool":
                if widget.isChecked():
                    step[name] = True
                continue

            if field_type == "choice":
                text = widget.currentText()
                if text:
                    step[name] = text
                continue

            if field_type == "text":
                text = widget.toPlainText()
                if text:
                    step[name] = text
                elif field.get("required"):
                    raise ValueError(f"{name} is required for action {self.action_name!r}")
                continue

            text = widget.text().strip()
            if not text:
                if field.get("required"):
                    raise ValueError(f"{name} is required for action {self.action_name!r}")
                continue
            if field_type == "int":
                step[name] = int(text)
            elif field_type == "float":
                step[name] = float(text)
            else:
                step[name] = text

        return step
