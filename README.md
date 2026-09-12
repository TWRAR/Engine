<p align="center">
  <img src="assets/logo.png" width="300" alt="TWRAR — The Website Recorder And Replayer">
</p>

# TWRAR — The Website Recorder And Replayer

A desktop GUI records your clicks, form input, and navigation on a real page
into a launchable step profile — save it as YAML, then replay it any time to
QA/regression-test or scrape **Stux.Group** sites. A profile is a list of
steps to run and optional named macros to group steps; hand-writing the
YAML instead of recording it works just as well.

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

On Windows, `browser.channel: default` reads the OS's registered default
browser (Brave/Chrome/Edge/Firefox all supported); on Linux/macOS it falls
back to Brave, then Playwright's own bundled Chromium - see
`browser.channel` below to force a specific one on any platform.

### Standalone executable (no Python required)

```
python src/build/build_release_files.py
```

Builds `dist/TWRAR` with PyInstaller - `.exe` on Windows, a macOS `.app`
bundle, a plain binary on Linux - hand it to someone without Python
installed. PyInstaller can't cross-compile, so build on each platform you
want a native executable for (prebuilt Windows/macOS/Linux executables
are also published on the
[Releases page](https://github.com/TWRAR/Engine/releases) for every
tagged version). Since the default `browser.channel` launches the
machine's own already-installed browser (not Playwright's bundled
Chromium), the build works out of the box for the normal case; only a
config that leaves Playwright to use its own Chromium needs
`playwright install chromium` run once on the target machine.

## Usage

```
python gui.py
```

1. Fill in **Start URL** and **Browser**, click **Start Browser**.
2. Click **● Record**, then click/type/navigate on the real page as normal -
   each interaction appears as a step in the list on the left.
3. Click **● Record** again to stop. Reorder, edit (selector/value/timeout),
   delete, or select a run of steps and **Group into Macro**.
4. **Add Action** inserts a step type the recorder can't capture (e.g.
   `assert`, `sleep`, `scrape`, `evaluate`, `click_coords`) by hand.
5. **Save Config** writes everything to a YAML profile you can reopen with
   **Load Config**; **▶ Play** replays the current steps right there in the
   GUI, with **⏸ Pause** / **⏹ Stop** controlling a run in progress.

Recorded selectors are a best-effort guess (id, then `data-testid`/`name`/
`aria-label`, then a DOM path) - review them in the editor before relying on
a recording for regression testing.

Config validation (unknown actions, missing required fields, dangling
`run_macro` references) runs automatically before every Play, so a typo
fails immediately instead of mid-run. Copy `configs/example.yaml` per
site/task as a starting point. See its comments for the full config shape.

## Config shape

- `browser.channel`: `default` (on Windows, auto-detects and launches the
  OS's registered default browser - Brave/Chrome/Edge/Firefox; on
  Linux/macOS, falls back to Brave then bundled Chromium), or force one
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
- `output.results_file`: where `scrape`/`evaluate` values get dumped as JSON.
- `output.report_dir`: writes `report.json` and `report.html` here after the
  run - a pass/fail/continued summary per step, with timings, and a
  screenshot auto-captured for any step that failed (or failed and
  continued). The GUI has the same field ("Report dir") on the config bar.

## Available actions

See `src/actions.py` for the full, authoritative list and each
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
`src/actions.py` decorated with `@action("name")` — nothing else needs
to change.

## Steam artwork

`assets/steam/` has a full set of custom Steam library artwork (grid
capsules, hero, logo, icon) for adding TWRAR to your Steam library as a
non-Steam game.

**[⬇ Download TWRAR_Steam_Assets.zip](https://github.com/TWRAR/Engine/raw/steam_assets/TWRAR_Steam_Assets.zip)**
— always up to date with the latest release, no need to clone the repo.
Also available from **[twrar.stuxie.dev/steam](https://twrar.stuxie.dev/steam)**,
the GUI's **Save Steam artwork (.zip)...** button, or as an asset on any
[Release](https://github.com/TWRAR/Engine/releases).

## Notes

- The `press` action sends a simulated key combo to the page itself (e.g.
  a site's own keyboard shortcut), using Playwright's format:
  `Control+Shift+K`.
- Credentials referenced in configs should use `${env:VAR_NAME}` rather
  than being hardcoded, so config files stay safe to commit.

## License

Copyright (C) 2026 StuxieDev

Licensed under the GNU General Public License v3.0 or later - see
[`LICENSE.md`](LICENSE.md) for the full text.

---

*Written & Maintained by <img src="https://github.com/StuxieDev.png" height="14" alt="StuxieDev" valign="middle"> [StuxieDev](https://stuxie.dev).*

*[A StuxieDev Project](https://projects.stuxie.dev)*
