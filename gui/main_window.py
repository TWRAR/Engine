"""Main GUI window: recorder + step editor + playback control."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Optional

import yaml
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from automator.actions import ExecutionContext, available_actions
from gui.session import BrowserSession, PlaybackController
from gui.step_forms import StepForm


def _step_label(step: dict) -> str:
    action = step.get("action", "?")
    for key in ("selector", "url", "keys", "name", "value", "message"):
        if key in step:
            return f"{action}  ({key}={step[key]})"
    return action


class AddActionDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Add action")
        self.result_step: Optional[dict] = None
        self.form: Optional[StepForm] = None

        layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.combo.addItems(available_actions())
        layout.addWidget(self.combo)

        self.form_container = QVBoxLayout()
        layout.addLayout(self.form_container)
        self._rebuild_form(self.combo.currentText())
        self.combo.currentTextChanged.connect(self._rebuild_form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _rebuild_form(self, action_name: str) -> None:
        while self.form_container.count():
            item = self.form_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.form = StepForm(action_name)
        self.form_container.addWidget(self.form)

    def _on_accept(self) -> None:
        try:
            assert self.form is not None
            self.result_step = self.form.collect()
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid step", str(exc))
            return
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Stux.Group Site Automator")

        self.session = BrowserSession()
        self.session.step_recorded.connect(self._on_step_recorded)
        self.session.log.connect(self._append_log)

        self.steps: list[dict] = []
        self.macros: dict[str, list[dict]] = {}
        self.loaded_browser_cfg: dict[str, Any] = {}
        self.current_editor_form: Optional[StepForm] = None
        self.current_editor_row: Optional[int] = None
        self.playback: Optional[PlaybackController] = None

        self._build_ui()

    # ---------------------------------------------------------------- UI

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        root.addWidget(self._build_config_bar())
        root.addWidget(self._build_toolbar())

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_steps_panel())
        splitter.addWidget(self._build_editor_panel())
        splitter.addWidget(self._build_macros_and_hotkeys_panel())
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        root.addWidget(splitter, stretch=1)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(140)
        root.addWidget(self.log_view)

    def _build_config_bar(self) -> QWidget:
        box = QGroupBox("Config")
        layout = QHBoxLayout(box)

        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Start URL:"))
        self.start_url_edit = QLineEdit()
        layout.addWidget(self.start_url_edit, stretch=2)

        layout.addWidget(QLabel("Browser:"))
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["default", "brave", "chrome", "edge", "firefox"])
        layout.addWidget(self.channel_combo)

        self.headless_check = QCheckBox("Headless")
        layout.addWidget(self.headless_check)

        layout.addWidget(QLabel("Profile dir:"))
        self.user_data_dir_edit = QLineEdit()
        layout.addWidget(self.user_data_dir_edit, stretch=1)

        layout.addWidget(QLabel("Default delay (ms):"))
        self.default_delay_edit = QLineEdit("0")
        self.default_delay_edit.setFixedWidth(60)
        layout.addWidget(self.default_delay_edit)

        layout.addWidget(QLabel("Results file:"))
        self.results_file_edit = QLineEdit()
        layout.addWidget(self.results_file_edit, stretch=1)

        return box

    def _build_toolbar(self) -> QWidget:
        box = QWidget()
        layout = QHBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)

        self.start_browser_btn = QPushButton("Start Browser")
        self.start_browser_btn.clicked.connect(self.on_start_browser)
        layout.addWidget(self.start_browser_btn)

        self.stop_browser_btn = QPushButton("Stop Browser")
        self.stop_browser_btn.clicked.connect(self.on_stop_browser)
        layout.addWidget(self.stop_browser_btn)

        self.record_btn = QPushButton("● Record")
        self.record_btn.setCheckable(True)
        self.record_btn.toggled.connect(self.on_toggle_recording)
        layout.addWidget(self.record_btn)

        layout.addSpacing(20)

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.on_play)
        layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(self.on_toggle_pause)
        layout.addWidget(self.pause_btn)

        self.stop_playback_btn = QPushButton("⏹ Stop")
        self.stop_playback_btn.clicked.connect(self.on_stop_playback)
        layout.addWidget(self.stop_playback_btn)

        layout.addSpacing(20)

        load_btn = QPushButton("Load Config")
        load_btn.clicked.connect(self.on_load_config)
        layout.addWidget(load_btn)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.on_save_config)
        layout.addWidget(save_btn)

        layout.addStretch(1)
        return box

    def _build_steps_panel(self) -> QWidget:
        box = QGroupBox("Steps")
        layout = QVBoxLayout(box)

        self.steps_list = QListWidget()
        self.steps_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.steps_list.currentRowChanged.connect(self.on_step_selected)
        layout.addWidget(self.steps_list)

        buttons = QHBoxLayout()
        add_btn = QPushButton("Add Action")
        add_btn.clicked.connect(self.on_add_action)
        buttons.addWidget(add_btn)

        up_btn = QPushButton("↑ Up")
        up_btn.clicked.connect(self.on_move_up)
        buttons.addWidget(up_btn)

        down_btn = QPushButton("↓ Down")
        down_btn.clicked.connect(self.on_move_down)
        buttons.addWidget(down_btn)

        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.on_delete_step)
        buttons.addWidget(del_btn)

        group_btn = QPushButton("Group into Macro")
        group_btn.clicked.connect(self.on_group_into_macro)
        buttons.addWidget(group_btn)

        layout.addLayout(buttons)
        return box

    def _build_editor_panel(self) -> QWidget:
        box = QGroupBox("Step editor")
        layout = QVBoxLayout(box)
        self.editor_layout = QVBoxLayout()
        layout.addLayout(self.editor_layout)
        layout.addStretch(1)

        apply_btn = QPushButton("Apply changes")
        apply_btn.clicked.connect(self.on_apply_edit)
        layout.addWidget(apply_btn)
        return box

    def _build_macros_and_hotkeys_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        macros_box = QGroupBox("Macros")
        macros_layout = QVBoxLayout(macros_box)
        self.macros_list = QListWidget()
        macros_layout.addWidget(self.macros_list)
        del_macro_btn = QPushButton("Delete Macro")
        del_macro_btn.clicked.connect(self.on_delete_macro)
        macros_layout.addWidget(del_macro_btn)
        layout.addWidget(macros_box)

        hotkeys_box = QGroupBox("Hotkeys (saved into config, used by main.py)")
        hotkeys_layout = QVBoxLayout(hotkeys_box)
        self.hotkeys_table = QTableWidget(0, 2)
        self.hotkeys_table.setHorizontalHeaderLabels(["Key combo", "Binding"])
        hotkeys_layout.addWidget(self.hotkeys_table)
        hk_buttons = QHBoxLayout()
        add_hk_btn = QPushButton("Add row")
        add_hk_btn.clicked.connect(self.on_add_hotkey_row)
        hk_buttons.addWidget(add_hk_btn)
        remove_hk_btn = QPushButton("Remove row")
        remove_hk_btn.clicked.connect(self.on_remove_hotkey_row)
        hk_buttons.addWidget(remove_hk_btn)
        hotkeys_layout.addLayout(hk_buttons)
        hint = QLabel("Binding: \"pause\", \"quit\", or a macro name.\nThe GUI itself is controlled by the Play/Pause/Stop buttons above,\nnot these hotkeys - they only take effect via main.py.")
        hint.setWordWrap(True)
        hotkeys_layout.addWidget(hint)
        layout.addWidget(hotkeys_box)

        return container

    # ----------------------------------------------------------- helpers

    def _append_log(self, message: str) -> None:
        self.log_view.appendPlainText(message)

    def _get_default_delay_ms(self) -> int:
        text = self.default_delay_edit.text().strip()
        try:
            return int(text) if text else 0
        except ValueError:
            return 0

    def _refresh_steps_list(self) -> None:
        self.steps_list.clear()
        for i, step in enumerate(self.steps):
            self.steps_list.addItem(f"{i + 1}. {_step_label(step)}")

    def _refresh_macros_list(self) -> None:
        self.macros_list.clear()
        for name, steps in self.macros.items():
            self.macros_list.addItem(f"{name} ({len(steps)} steps)")

    def _refresh_hotkeys_table(self, hotkeys: dict) -> None:
        self.hotkeys_table.setRowCount(0)
        for combo, binding in hotkeys.items():
            row = self.hotkeys_table.rowCount()
            self.hotkeys_table.insertRow(row)
            self.hotkeys_table.setItem(row, 0, QTableWidgetItem(combo))
            label = binding if isinstance(binding, str) else self._binding_to_label(binding)
            self.hotkeys_table.setItem(row, 1, QTableWidgetItem(label))

    @staticmethod
    def _binding_to_label(binding: Any) -> str:
        if isinstance(binding, list) and len(binding) == 1 and binding[0].get("action") == "run_macro":
            return binding[0]["name"]
        return "custom"

    def _collect_hotkeys(self) -> dict:
        hotkeys: dict[str, Any] = {}
        for row in range(self.hotkeys_table.rowCount()):
            combo_item = self.hotkeys_table.item(row, 0)
            binding_item = self.hotkeys_table.item(row, 1)
            if not combo_item or not binding_item:
                continue
            combo = combo_item.text().strip()
            binding_text = binding_item.text().strip()
            if not combo or not binding_text:
                continue
            if binding_text in ("pause", "quit"):
                hotkeys[combo] = binding_text
            elif binding_text in self.macros:
                hotkeys[combo] = [{"action": "run_macro", "name": binding_text}]
            else:
                QMessageBox.warning(
                    self,
                    "Unknown hotkey binding",
                    f"{binding_text!r} is not \"pause\", \"quit\", or a known macro name "
                    f"- skipped for {combo!r}.",
                )
        return hotkeys

    def _clear_editor(self) -> None:
        while self.editor_layout.count():
            item = self.editor_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.current_editor_form = None
        self.current_editor_row = None

    # ------------------------------------------------------------ slots

    @asyncSlot()
    async def on_start_browser(self) -> None:
        browser_cfg = dict(self.loaded_browser_cfg)
        browser_cfg["channel"] = self.channel_combo.currentText()
        browser_cfg["headless"] = self.headless_check.isChecked()

        user_data_dir = self.user_data_dir_edit.text().strip() or tempfile.mkdtemp(prefix="automator-profile-")
        start_url = self.start_url_edit.text().strip() or None

        try:
            await self.session.start(browser_cfg, user_data_dir, start_url)
        except Exception as exc:
            QMessageBox.critical(self, "Failed to start browser", str(exc))

    @asyncSlot()
    async def on_stop_browser(self) -> None:
        self.record_btn.setChecked(False)
        await self.session.stop()

    def on_toggle_recording(self, checked: bool) -> None:
        if not self.session.is_running:
            self.record_btn.setChecked(False)
            QMessageBox.warning(self, "Not started", "Start the browser first.")
            return
        if checked:
            self.session.start_recording()
        else:
            self.session.stop_recording()

    def _on_step_recorded(self, step: dict) -> None:
        self.steps.append(step)
        self._refresh_steps_list()
        self.steps_list.setCurrentRow(len(self.steps) - 1)

    @asyncSlot()
    async def on_play(self) -> None:
        if not self.session.is_running:
            QMessageBox.warning(self, "Not started", "Start the browser first.")
            return
        if not self.steps:
            QMessageBox.information(self, "Nothing to play", "There are no steps to run.")
            return

        results: dict[str, Any] = {}
        ctx = ExecutionContext(
            page=self.session.page,
            macros=self.macros,
            results=results,
            default_delay_ms=self._get_default_delay_ms(),
        )
        self.playback = PlaybackController(ctx)
        self.playback.step_started.connect(
            lambda i, name: self._append_log(f"[step {i + 1}/{len(self.steps)}] {name}")
        )
        self.playback.step_failed.connect(
            lambda i, name, err: self._append_log(f"[step {i + 1}] {name} FAILED: {err}")
        )
        self.playback.finished.connect(
            lambda stopped: self._append_log("Playback stopped early." if stopped else "Playback finished.")
        )

        self.pause_btn.setChecked(False)
        await self.playback.run(list(self.steps))

        output_path = self.results_file_edit.text().strip()
        if output_path and results:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(yaml.safe_dump(results, sort_keys=False), encoding="utf-8")
            self._append_log(f"Results saved to {output_path}")

    def on_toggle_pause(self, checked: bool) -> None:
        if not self.playback:
            return
        if checked:
            self.playback.pause()
        else:
            self.playback.resume()

    def on_stop_playback(self) -> None:
        if self.playback:
            self.playback.stop()

    def on_step_selected(self, row: int) -> None:
        self._clear_editor()
        if row < 0 or row >= len(self.steps):
            return
        step = self.steps[row]
        form = StepForm(step.get("action", ""), step)
        self.editor_layout.addWidget(form)
        self.current_editor_form = form
        self.current_editor_row = row

    def on_apply_edit(self) -> None:
        if self.current_editor_form is None or self.current_editor_row is None:
            return
        try:
            step = self.current_editor_form.collect()
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid step", str(exc))
            return
        self.steps[self.current_editor_row] = step
        row = self.current_editor_row
        self._refresh_steps_list()
        self.steps_list.setCurrentRow(row)

    def on_delete_step(self) -> None:
        row = self.steps_list.currentRow()
        if row < 0:
            return
        del self.steps[row]
        self._refresh_steps_list()
        self._clear_editor()

    def on_move_up(self) -> None:
        row = self.steps_list.currentRow()
        if row <= 0:
            return
        self.steps[row - 1], self.steps[row] = self.steps[row], self.steps[row - 1]
        self._refresh_steps_list()
        self.steps_list.setCurrentRow(row - 1)

    def on_move_down(self) -> None:
        row = self.steps_list.currentRow()
        if row < 0 or row >= len(self.steps) - 1:
            return
        self.steps[row + 1], self.steps[row] = self.steps[row], self.steps[row + 1]
        self._refresh_steps_list()
        self.steps_list.setCurrentRow(row + 1)

    def on_group_into_macro(self) -> None:
        selected = sorted({index.row() for index in self.steps_list.selectedIndexes()})
        if not selected:
            QMessageBox.information(self, "Group into macro", "Select one or more contiguous steps first.")
            return
        if selected != list(range(selected[0], selected[-1] + 1)):
            QMessageBox.warning(self, "Group into macro", "Selection must be contiguous.")
            return

        name, ok = QInputDialog.getText(self, "Macro name", "Name for this macro:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self.macros:
            QMessageBox.warning(self, "Group into macro", f"Macro {name!r} already exists.")
            return

        grouped = self.steps[selected[0]: selected[-1] + 1]
        self.macros[name] = grouped
        self.steps[selected[0]: selected[-1] + 1] = [{"action": "run_macro", "name": name}]
        self._refresh_steps_list()
        self._refresh_macros_list()
        self._clear_editor()
        self._append_log(f"Grouped {len(grouped)} step(s) into macro {name!r}.")

    def on_delete_macro(self) -> None:
        row = self.macros_list.currentRow()
        if row < 0:
            return
        name = list(self.macros.keys())[row]
        del self.macros[name]
        self._refresh_macros_list()
        self._append_log(f"Deleted macro {name!r}. Any run_macro steps referencing it will now fail.")

    def on_add_action(self) -> None:
        dialog = AddActionDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.result_step:
            insert_at = self.steps_list.currentRow() + 1 if self.steps_list.currentRow() >= 0 else len(self.steps)
            self.steps.insert(insert_at, dialog.result_step)
            self._refresh_steps_list()
            self.steps_list.setCurrentRow(insert_at)

    def on_add_hotkey_row(self) -> None:
        row = self.hotkeys_table.rowCount()
        self.hotkeys_table.insertRow(row)
        self.hotkeys_table.setItem(row, 0, QTableWidgetItem("f8"))
        self.hotkeys_table.setItem(row, 1, QTableWidgetItem("pause"))

    def on_remove_hotkey_row(self) -> None:
        row = self.hotkeys_table.currentRow()
        if row >= 0:
            self.hotkeys_table.removeRow(row)

    def on_save_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save config", "configs/", "YAML files (*.yaml *.yml)")
        if not path:
            return

        browser_cfg = dict(self.loaded_browser_cfg)
        browser_cfg["channel"] = self.channel_combo.currentText()
        browser_cfg["headless"] = self.headless_check.isChecked()

        config: dict[str, Any] = {
            "name": self.name_edit.text().strip() or "Untitled",
            "browser": browser_cfg,
            "user_data_dir": self.user_data_dir_edit.text().strip() or None,
            "start_url": self.start_url_edit.text().strip() or None,
            "default_delay_ms": self._get_default_delay_ms(),
            "macros": self.macros,
            "steps": self.steps,
            "hotkeys": self._collect_hotkeys(),
        }
        results_file = self.results_file_edit.text().strip()
        if results_file:
            config["output"] = {"results_file": results_file}

        config = {k: v for k, v in config.items() if v not in (None, {}, [])}

        Path(path).write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        self._append_log(f"Saved config to {path}")

    def on_load_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load config", "configs/", "YAML files (*.yaml *.yml)")
        if not path:
            return

        config = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

        self.name_edit.setText(config.get("name", "") or "")
        browser_cfg = dict(config.get("browser", {}) or {})
        channel = browser_cfg.pop("channel", "default")
        headless = browser_cfg.pop("headless", False)
        self.loaded_browser_cfg = browser_cfg
        idx = self.channel_combo.findText(channel)
        self.channel_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.headless_check.setChecked(bool(headless))

        self.user_data_dir_edit.setText(config.get("user_data_dir", "") or "")
        self.start_url_edit.setText(config.get("start_url", "") or "")
        self.default_delay_edit.setText(str(config.get("default_delay_ms", 0)))

        self.macros = config.get("macros", {}) or {}
        self.steps = config.get("steps", []) or []
        self._refresh_steps_list()
        self._refresh_macros_list()
        self._clear_editor()

        self._refresh_hotkeys_table(config.get("hotkeys", {}) or {})

        output_cfg = config.get("output", {}) or {}
        self.results_file_edit.setText(output_cfg.get("results_file", "") or "")

        self._append_log(f"Loaded config from {path}")

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        if self.session.is_running:
            import asyncio

            asyncio.ensure_future(self.session.stop())
        super().closeEvent(event)
