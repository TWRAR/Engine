<p align="center">
  <img src="assets/logo.png" width="500" alt="TWRAR">
</p>

# Contributing to TWRAR

Personal automation tool for Stux.Group internal QA/regression testing and
first-party data scraping.

## Setup

1. Python 3.10+
2. `pip install -r requirements.txt`
3. `playwright install chromium` (skip if you always point at an external
   Brave/Chrome executable via `browser.executable_path`)

## Adding a new action type

Add a small async function to `src/actions.py` decorated with
`@action("your_action_name")`. It receives the shared `ExecutionContext`
(page, macros, results dict) and the resolved step dict. No other file
needs to change - the GUI's playback dispatches by name automatically.
Add a matching entry to `src/schema.py`'s
`ACTION_SCHEMA` too, so the GUI's Add Action dialog and config validation
(`src/validate.py`) both pick it up - `tests/test_schema.py` fails
the build if the two ever drift out of sync.

## Running tests

```
pip install -r requirements.txt
pip install pytest pytest-asyncio
pytest
```

## Release flow

1. Update `CHANGELOG.md`.
2. Bump `VERSION.md` (semantic versioning).
3. Update `README.md` if behavior changed.
4. Run the test suite (`pytest`) - keep it green.
5. Run `commit.bat` (or `commit.sh` on POSIX) - it commits everything
   staged/unstaged as `Release vX.Y.Z` and tags `vX.Y.Z`, both read from
   `VERSION.md`.
6. Pushing the `vX.Y.Z` tag triggers the Release workflow, which builds
   and publishes Windows/macOS/Linux executables automatically. To build
   locally instead (e.g. to test before pushing), run
   `python src/scripts/build_release_files.py` to refresh the standalone
   `dist/TWRAR` for this platform.
7. If `assets/icon.png` or `assets/logo.png` changed, regenerate the Steam
   library artwork with `python src/build/steam_asset_builder.py` (writes
   `assets/steam/`) — the Release workflow also rebuilds and publishes
   `TWRAR_Steam_Assets.zip` to the `steam_assets` branch automatically.
