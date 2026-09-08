# Changelog

All notable changes to this project are documented here.

## [1.1.3] - 2026-09-08
### Fixed
- `commit.bat`/`commit.sh` didn't match the Stux.Group reference pattern
  (see Stuxs.Tools/Downl.one): they required a hand-typed commit message
  and always ran `git commit` even with nothing staged. Now they take no
  argument, auto-generate `Release vX.Y.Z` (from `VERSION.md`) as the
  commit message, skip the commit (but still tag) when there's nothing to
  commit, and resolve `VERSION.md` relative to the script's own location
  instead of assuming the caller's cwd.

## [1.1.2] - 2026-09-08
### Fixed
- Logo (`assets/logo.png`) cursor mark looked blurry/low-res - it was
  upscaled from the small 256px `icon.png` raster. Now drawn as a crisp
  vector shape (the same coordinates as `scripts/generate_icon.py`'s
  `draw_glyph()`) at high resolution instead.

## [1.1.1] - 2026-09-08
### Fixed
- Standardized the project's display name to **Automater** everywhere -
  window title, GUI tab label, About tab, standalone exe names
  (`Automater.exe`/`AutomaterCLI.exe`), and docs previously read "Site
  Automator" or "Automator" inconsistently.
- Full text logo (`assets/logo.png`) - previously just the square icon
  upscaled, now the mark plus the "Automater" wordmark.
- Renamed the `automator` Python package to `automater` (import paths,
  `pyproject.toml` package/script name, PyInstaller `--paths`) so the
  module name matches the project name everywhere.

## [1.1.0] - 2026-09-07
### Added
- Config pre-flight validation (`automator/validate.py`): checks every
  step's action name and required fields, plus `run_macro`/hotkey
  references, before a browser is ever launched. Runs automatically before
  every run and is also available standalone via `--validate` (CLI) or a
  confirmation dialog before Play (GUI).
- Per-step `retry: {times, delay_ms}` and `continue_on_error: true`, so a
  flaky step can retry before failing, and one soft failure doesn't have to
  abort an entire regression run.
- Automatic failure screenshots and HTML/JSON run reports
  (`automator/report.py`): set `output.report_dir` (CLI config) or the
  GUI's "Report dir" field to get a `report.html`/`report.json` per run,
  with a pass/fail/continued summary, per-step timings, and a screenshot
  captured for any step that failed.
- Video recording of the whole browser session via `browser.record_video_dir`
  (`record_video_size` defaults to `viewport`).
- `automator/actions.py`: `ExecutionContext.step_results` and the
  `StepResult` dataclass now track every step's outcome (status, attempts,
  duration, error, screenshot), feeding both the report and the retry logic.
- Standalone Windows executables (`build.bat`/`build.sh` + `scripts/
  build_exe.py`, PyInstaller): `SiteAutomator.exe` (GUI) and
  `SiteAutomatorCLI.exe` (CLI) - no Python install required on the target
  machine for the default (existing-browser) setup. `automator/paths.py`'s
  new `APP_ROOT` resolves bundled `assets/`, `CHANGELOG.md`, and
  `VERSION.md` correctly under PyInstaller's onefile bootloader (via
  `sys._MEIPASS`) as well as when run from source, so the GUI's window
  icon, About-tab logo, and changelog viewer all work in the packaged exe.

## [1.0.0] - 2026-09-07
First stable release - no functional changes since 0.3.0. The action
registry, GUI, config format, and packaging have held steady long enough
to commit to semantic versioning going forward: breaking changes to the
YAML config shape or the action registry's public surface will bump the
major version from here on.

## [0.3.0] - 2026-09-06
### Added
- About tab in the GUI: logo, project name/version, blurb, disclaimer text,
  a link to the repo, and a live `CHANGELOG.md` viewer with a Reload button.
  The existing recorder/editor UI now lives in its own "Automator" tab
  alongside it.
- First-launch disclaimer dialog (`gui/disclaimer.py`), shown before the
  main window until accepted; acceptance is persisted so it only shows once.
- Local GUI settings persistence (`automator/paths.py`, `automator/
  settings.py`): stored at `%APPDATA%\Automater\configs\settings.json`
  (Windows) / `~/.local/share/Automater/configs/settings.json` (Linux),
  deep-merged against defaults so older files backfill new keys. Currently
  persists the disclaimer acknowledgment, default browser channel/headless/
  profile dir, and the last config path used for Load/Save Config.
- `automator/metadata.py`: single source of truth for project name, repo
  URL, and disclaimer text, read by the About tab and disclaimer dialog.
- Packaging (`pyproject.toml`): pip-installable (`pip install -e .`), with
  the version read dynamically from `VERSION.md` so it never drifts from
  the release flow.
- Test suite (`tests/`, pytest + pytest-asyncio): 38 tests covering the
  action registry, `ACTION_SCHEMA`/registry consistency, browser
  default-detection, settings load/save/merge, and the GUI recorder's
  event-to-step mapping.
- GitHub Actions CI (`.github/workflows/ci.yml`), running the test suite on
  `windows-latest` (required by `automator/browser.py`'s use of `winreg`).
- `LICENSE.md`: GNU General Public License v3.0.

## [0.2.0] - 2026-09-06
### Added
- Desktop GUI (`gui_main.py`, PySide6 + qasync): records clicks/form input/
  navigation into steps live, a step editor (reorder, edit, delete, group
  selected steps into a macro), an "Add Action" dialog for step types the
  recorder can't capture, and Play/Pause/Stop playback with a log panel.
  Config load/save is fully interoperable with the CLI's YAML format.
- Browser default-detection (`automator/browser.py`): `browser.channel:
  default` reads the Windows default-browser registration and launches
  Brave/Chrome/Edge/Firefox accordingly; explicit channels and
  `executable_path` still override it.
- Per-step and global delays: `default_delay_ms` config option plus
  per-step `delay_before`/`delay_after` (ms).
- App icon/logo (`assets/icon.ico`, `assets/icon.png`, `assets/logo.png`),
  generated via `scripts/generate_icon.py`; wired into the GUI window icon.

## [0.1.0] - 2026-09-06
### Added
- Initial standalone Python + Playwright automation script for Stux.Group site QA/regression testing and own-data scraping.
- Extensible action registry (`automator/actions.py`): goto/reload/back/forward, click, dblclick, click_coords, hover, drag_and_drop, scroll, fill, type, press, check/uncheck, select_option, upload_file, wait_for_selector/url/load_state, sleep, screenshot, scrape, evaluate, assert (visible/hidden/text/url/count), log, repeat, run_macro.
- Named macros: reusable step groups referenced from `steps`, other macros, or hotkeys.
- Brave browser support via a persistent Playwright context (also works with plain Chrome or any Chromium executable).
- Global system-wide hotkeys (pause/resume, quit, or run an arbitrary list of steps), plus in-page simulated key presses via the `press` action.
- `${env:VAR_NAME}` substitution in config values, so credentials never need to live in the YAML file.
