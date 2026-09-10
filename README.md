<p align="center">
  <img src="assets/logo.png" width="500" alt="TWRAR — The Website Recorder And Replayer">
</p>

# TWRAR — The Website Recorder And Replayer

*<a href="https://projects.stuxie.dev">A <img src="https://github.com/StuxieDev.png" height="16" alt="StuxieDev" valign="middle"> StuxieDev Project</a>*

A desktop GUI records your clicks, form input, and navigation on a real page
into a launchable step profile — save it as YAML, then replay it any time to
QA/regression-test or scrape **Stux.Group** sites. A profile is a list of
steps to run, optional named macros to group steps, and optional global
hotkeys; hand-writing the YAML instead of recording it works just as well.

Website: https://twrar.stuxie.dev  
Repository: https://github.com/TWRAR/Engine  
License: [GPL-3.0-or-later](LICENSE.md)

> This tool is intended for sites and content you own or otherwise have
> explicit authorization to automate. Do not point it at third-party sites
> without permission.

## Setup

```
pip install -r requirements.txt
playwright install chromium   # only needed if you don't set browser.executable_path
```

By default the tool launches whatever browser is set as the Windows
default (Brave/Chrome/Edge/Firefox all supported) - see `browser.channel`
below to force a specific one instead.

### Standalone .exe (no Python required)

```
build.bat
```

Builds `dist\TWRAR.exe` (the GUI) and `dist\TWRARCLI.exe`
(the CLI) with PyInstaller - hand either one to someone without Python
installed. Since the default `browser.channel` launches the machine's own
already-installed browser (not Playwright's bundled Chromium), the exe
works out of the box for the normal case; only a config that leaves
Playwright to use its own Chromium needs `playwright install chromium` run
once on the target machine.

## Usage

### GUI (recorder + step editor)

```
python gui_main.py
```

1. Fill in **Start URL** and **Browser**, click **Start Browser**.
2. Click **● Record**, then click/type/navigate on the real page as normal -
   each interaction appears as a step in the list on the left.
3. Click **● Record** again to stop. Reorder, edit (selector/value/timeout),
   delete, or select a run of steps and **Group into Macro**.
4. **Add Action** inserts a step type the recorder can't capture (e.g.
   `assert`, `sleep`, `scrape`, `evaluate`, `click_coords`) by hand.
5. **Save Config** writes everything to a YAML file compatible with
   `main.py`; **▶ Play** replays the current steps right there in the GUI,
   with **⏸ Pause** / **⏹ Stop** controlling a run in progress.

Recorded selectors are a best-effort guess (id, then `data-testid`/`name`/
`aria-label`, then a DOM path) - review them in the editor before relying on
a recording for regression testing.

### CLI (existing configs, no GUI)

```
python main.py --config configs/example.yaml
python main.py --config configs/example.yaml --validate   # check it, don't run it
```

`--validate` checks every step's action name and required fields (and every
`run_macro`/hotkey reference) against the action registry and exits - no
browser is launched. The same check also runs automatically before a normal
run, so a typo fails in milliseconds instead of mid-run.

Copy `configs/example.yaml` per site/task. See its comments for the full
config shape.

## Config shape

- `browser.channel`: `default` (auto-detects and launches whatever browser
  is set as the Windows default - Brave/Chrome/Edge/Firefox), or force one
  with `brave` | `chrome` | `edge` | `firefox`, or bypass detection entirely
  with `browser.executable_path`. Plus `headless`, `viewport`, `args`,
  `load_extension` (Chromium-based browsers only), and `record_video_dir`
  (records a `.webm` of the run; `record_video_size` defaults to `viewport`).
- `user_data_dir`: persistent Chrome profile dir (keeps logins between runs).
  Omit for a fresh temp profile every run.
- `start_url`: first page to load.
- `default_delay_ms`: pause after every step by default (e.g. to watch a run
  happen, or go easy on a site's rate limits). Any step can override it with
  its own `delay_after` and/or `delay_before` (both in ms).
- `macros`: named step lists, invoked with `{action: run_macro, name: <key>}`.
- `steps`: the top-level sequence that runs when the script starts. Any step
  can also set `retry: {times: N, delay_ms: N}` to retry a flaky step before
  giving up, and/or `continue_on_error: true` to log a failure and move on
  instead of aborting the whole run over one step.
- `hotkeys`: `<key combo>: pause | quit | [<steps>]`. These are **global**
  (system-wide, via the `keyboard` package), so they work even while the
  browser window has focus. Useful for pausing a run, taking an ad-hoc
  screenshot, or re-running a verification macro without restarting.
  Only used by the CLI (`main.py`) - the GUI is controlled via its own
  Play/Pause/Stop buttons instead, to avoid a hotkey firing steps into the
  page while a GUI-driven run is already in progress.
- `output.results_file`: where `scrape`/`evaluate` values get dumped as JSON.
- `output.report_dir`: writes `report.json` and `report.html` here after the
  run - a pass/fail/continued summary per step, with timings, and a
  screenshot auto-captured for any step that failed (or failed and
  continued). The GUI has the same field ("Report dir") on the config bar.

## Available actions

See `twrar/actions.py` for the full, authoritative list and each
action's fields. Highlights:

- **Navigation**: `goto`, `reload`, `go_back`, `go_forward`
- **Mouse**: `click`, `dblclick`, `click_coords`, `hover`, `drag_and_drop`,
  `scroll`
- **Forms/keyboard**: `fill`, `type` (real keystrokes), `press`, `check`,
  `uncheck`, `select_option`, `upload_file`
- **Waiting**: `wait_for_selector`, `wait_for_url`, `wait_for_load_state`,
  `sleep`
- **Capture**: `screenshot`, `scrape`, `evaluate` (run arbitrary JS)
- **QA assertions**: `assert` with `type: visible|hidden|text_equals|
  text_contains|url_equals|url_contains|count_equals`
- **Composition**: `log`, `repeat`, `run_macro`

New action types are added by writing one small async function in
`twrar/actions.py` decorated with `@action("name")` — nothing else in
the runner needs to change.

## Two kinds of "hotkey"

- **Global control hotkeys** (`hotkeys` in the config): real keypresses on
  your machine, handled by the `keyboard` package, that pause/resume/quit
  the run or fire a step list.
- **Simulated key presses sent to the page** (`press` action in a step or
  macro): Playwright sends the key combo to the browser itself, as part of
  the automation sequence (e.g. a site's own keyboard shortcut).

These use different key-name formats: `keyboard` combos look like `f8` or
`ctrl+shift+k`; Playwright's `press` action uses `Control+Shift+K`.

## Notes

- `keyboard`'s global hook can require running the terminal as
  Administrator in some locked-down environments.
- Credentials referenced in configs should use `${env:VAR_NAME}` rather
  than being hardcoded, so config files stay safe to commit.

## License

Copyright (C) 2026 StuxieDev

Licensed under the GNU General Public License v3.0 or later - see
[`LICENSE.md`](LICENSE.md) for the full text.

---

*Built & Maintained by <img src="https://github.com/StuxieDev.png" height="14" alt="StuxieDev" valign="middle"> [StuxieDev](https://stuxie.dev).*
