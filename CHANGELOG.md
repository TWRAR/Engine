# Changelog

All notable changes to this project are documented here.

## [3.5.1] - 2026-09-12

### Removed
- **`assets/author.png`** — dead, unreferenced file; the About tab has no
  author-avatar element (unlike the sibling TS4RLS project's), so nothing
  ever loaded it.

### Fixed
- README never documented the Steam artwork feature added in v3.5.0 at
  all — added a "Steam artwork" section.
- `.gitignore` was missing `.pytest_cache/` explicitly (still ignored via
  a global excludesfile, but not documented in this repo's own file).
- CONTRIBUTING.md's release flow didn't mention regenerating Steam
  artwork with `scripts/steam_asset_builder.py`.

## [3.5.0] - 2026-09-12
### Added
- **Steam library artwork**, matching the sibling TS4RLS project's
  feature: `scripts/steam_asset_builder.py` generates
  `assets/steam/{cover,wide_cover,background,logo,logo_horizontal,icon}.png`
  from the app's own `icon.png`/`logo.png`, so the Steam art never drifts
  out of sync with the app's branding. The About tab's new **"Save Steam
  artwork (.zip)..."** button exports it directly. `.github/workflows/
  release.yml` gets a `steam-assets` job that zips it and publishes to a
  `steam_assets` branch (and attaches it to the GitHub Release) on every
  tagged release, same as TS4RLS.

## [3.4.1] - 2026-09-12
### Fixed
- **QSS pseudo-state border-shorthand bug** (`src/gui/theme.py`): Qt's QSS
  engine doesn't reliably apply a pseudo-state rule that only overrides
  one sub-property (`border-color`) of a shorthand (`border`) set in the
  base rule. `QPushButton:hover`, `QTabBar::tab:selected`, and
  `QPushButton:disabled` now redeclare the full `border` shorthand
  instead, so their hover/selected/disabled colors actually take effect
  (found via a cross-project audit against the sibling TS4RLS project,
  which hit and fixed the same bug class in its own theme.py).
- `.github/workflows/release.yml`'s Linux build job didn't install Qt's
  runtime libraries (`libegl1`/`libopengl0`) before running PyInstaller,
  unlike `ci.yml` - PyInstaller's analysis phase imports PySide6, so a
  release build was likely to fail on a fresh Ubuntu runner. Added the
  same apt-get install step.

### Added
- `QLineEdit:focus`/`QComboBox:focus` styling (`src/gui/theme.py`) - there
  was previously no focus-state rule for either.

## [3.4.0] - 2026-09-12
### Changed
- **`build.bat`/`build.sh` are gone.** `scripts/build_exe.py` is renamed
  `scripts/build_release_files.py` and now installs its own dependencies
  (`requirements.txt` + PyInstaller) before building, so it's run directly
  (`python scripts/build_release_files.py`) instead of through an OS-specific
  wrapper. `.github/workflows/release.yml` calls it the same way. The now
  fully-automatic `[build]` extra in `pyproject.toml` is removed as
  redundant.

## [3.3.3] - 2026-09-12
### Changed
- `scripts/generate_icon.py` now writes `favicon.ico` straight into the
  sibling `Website/assets/` checkout instead of this repo's `assets/`
  (skipped with a message if no sibling checkout is found), since it's
  purely a Website asset that has no reason to exist here at all - not
  even gitignored. `.gitignore`'s now-unneeded `assets/favicon.ico` entry
  is removed along with it.

## [3.3.2] - 2026-09-12
### Changed
- **Icon/logo window is now an actual rectangle** (`scripts/generate_icon.py`):
  previously a heavily-rounded square ("squircle"); now a wide, slightly
  rounded-corner rectangle letterboxed within the square icon canvas, closer
  to a real browser window's proportions.
- `assets/logo.png`'s wordmark text now aligns to the icon's visible
  window instead of the padded square it's drawn on - previously the text
  sat noticeably higher than the icon once the window was letterboxed.

### Fixed
- `assets/favicon.ico` is no longer committed in this repo - the Engine
  app itself never uses it (only `icon.ico`/`icon.icns`), it's purely a
  Website asset. `scripts/generate_icon.py` still (re)generates it
  locally (now gitignored) so it stays reproducible from the same glyph;
  copy it into `Website/assets/` by hand same as `icon.png`/`logo.png`.

## [3.3.1] - 2026-09-12
### Changed
- **Icon/logo (`assets/icon.*`, `assets/logo.png`) redrawn as a browser
  window** instead of a plain rounded square: a chrome/tab bar (three dots)
  across the top, with the recording dot, play triangle, and cursor inside
  it. `scripts/generate_icon.py` also now generates `assets/favicon.ico`
  (16/32/48) from the same glyph, so the website favicon no longer has to
  be hand-maintained separately from the app icon.

## [3.3.0] - 2026-09-10
### Changed
- **Blank Profile dir/Results file/Report dir now default under TWRAR's
  own per-user app-data folder** (`%APPDATA%\TWRAR\profiles\<config
  name>\` and `%APPDATA%\TWRAR\output\<config name>\` on Windows, the
  platform equivalent elsewhere) instead of a throwaway OS temp profile
  and silently skipping results/reports. Each config gets its own
  subfolder (named after its `name` field) so different configs don't
  collide. An explicit path in the config or GUI field still overrides
  this, unchanged.
- `src/paths.py`: added `PROFILES_DIR` and `OUTPUT_DIR`, alongside the
  existing `CONFIGS_DIR`/`USER_DATA_DIR`.

## [3.2.0] - 2026-09-10
### Changed
- **Reorganized the project layout to match TIGHC/TS4RLS's convention.**
  The `twrar/` package is now `src/`, the `gui/` package is now
  `src/gui/`, and `gui_main.py` is now `gui.py` at the repo root. Running
  from a clone is now `python gui.py` (previously `python gui_main.py`).
  Purely a structural rename - no behavior changes.
- The GUI's window title now reads "TWRAR (The Website Recorder And
  Replayer) — v3.2.0" (name, full name, and version) instead of just
  "TWRAR".

## [3.1.1] - 2026-09-10
### Fixed
- The About tab's repo link and "Update available" link now use the
  theme's accent color instead of Qt's default (system-themed) link
  color, matching the "Terms and Ethics of Use" link in the disclaimer
  dialog.

## [3.1.0] - 2026-09-10
### Added
- **Update checker** (`twrar/update_check.py`): the About tab now checks
  GitHub for a newer Engine release on launch (and via a "Check now"
  button), showing a clickable link to the release when one's available.
  Best-effort - any network failure is treated as "up to date" rather
  than shown as an error.

## [3.0.0] - 2026-09-10
### Removed
- **The CLI (`main.py`/`TWRARCLI`) is discontinued.** TWRAR is GUI-only
  from here on. Also removed as a consequence: the `hotkeys` config key
  (global system-wide hotkeys only ever took effect via the CLI - the GUI
  has always used its own Play/Pause/Stop buttons instead) and the
  `keyboard` dependency. The GUI's Macros panel is unaffected; only the
  Hotkeys editor next to it is gone.

### Added
- **Linux and macOS support.** `twrar/browser.py`'s Windows-only `winreg`
  import is now conditional, with Brave/Chrome/Edge/Firefox path
  candidates added for both platforms; `channel: default` still only
  reads the actual OS default browser on Windows (falls back to
  Brave/bundled Chromium elsewhere). `scripts/build_exe.py` now builds
  correctly on all three platforms (per-OS icon selection, `.icns`
  generated by `scripts/generate_icon.py`).
- **`.github/workflows/release.yml`**: pushing a `vX.Y.Z` tag now builds
  and publishes Windows/macOS/Linux executables to a GitHub Release
  automatically.
- CI (`ci.yml`) now runs the test suite on Windows, macOS, and Linux.

## [2.1.0] - 2026-09-10
### Added
- `gui/theme.py`: a red-tinted light/dark QSS theme matching
  twrar.stuxie.dev's palette, applied app-wide at startup. Auto-detects
  light/dark from the system.

### Changed
- Disclaimer dialog heading now reads "Before you continue" (previously
  "TWRAR"); added a "By continuing, you agree to our Terms and Ethics of
  Use" line, linking to twrar.stuxie.dev/legal/terms in the accent color.
- Changelog viewer's `##` heading color now follows the active theme's
  accent instead of a hardcoded purple.

## [2.0.2] - 2026-09-10
### Changed
- Wordmark logo (`assets/logo.png`): tagline is now bold and the same
  red as the icon/acronym, instead of a lighter/darker shade.

## [2.0.1] - 2026-09-10
### Changed
- Refined the icon/wordmark logo (`assets/icon.*`, `assets/logo.png`):
  the cursor, recording dot, and play triangle are now laid out as a
  clean two-row grid instead of overlapping, and the wordmark's tagline
  is a darker red for better contrast on white.
- README footer now reads "Written & Maintained by StuxieDev" followed
  by "A StuxieDev Project" (previously "Built & Maintained by", reversed
  order).

## [2.0.0] - 2026-09-10
### Changed
- **Renamed the project to TWRAR** (The Website Recorder And Replayer) and
  moved it to its own GitHub organization/repo
  (`github.com/TWRAR/Engine`, formerly `github.com/StuxieDev/Automater`).
  This is a breaking rename: the `automater` Python package, the
  `automater` console script, the `AUTOMATER_*` env var convention, and the
  `Automater.exe`/`AutomaterCLI.exe` standalone executables are now
  `twrar`, `twrar`, `TWRAR_*`, and `TWRAR.exe`/`TWRARCLI.exe` respectively.
- New icon and wordmark logo (`assets/icon.*`, `assets/logo.png`), themed
  red, in the same house style as TIGHC/TS4RLS: a cursor (recording) paired
  with a play triangle (replaying).

## [1.1.6] - 2026-09-10
### Fixed
- `automater/paths.py` resolved macOS's per-user data directory using the
  Linux `~/.local/share` convention instead of the actual macOS one. Now
  branches on `sys.platform` (`win32`/`darwin`/other) so macOS correctly
  uses `~/Library/Application Support/Automater/`.

## [1.1.5] - 2026-09-09
### Changed
- About tab's changelog viewer now renders `CHANGELOG.md` as rich text
  (headings, bullet points, **bold**, and `code` spans) instead of showing
  raw markdown, matching the TIGHC project's changelog viewer.

## [1.1.4] - 2026-09-08
### Fixed
- `LICENSE.md` was a plain-text dump of GPLv3 (hard-wrapped lines, no
  headings) that rendered as a wall of text. Replaced with the FSF's own
  Markdown transcription (gnu.org/licenses/gpl-3.0.md) - identical legal
  text, proper `#`/`##`/`###` headings and paragraph formatting.

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
