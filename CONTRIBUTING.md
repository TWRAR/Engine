<p align="center">
  <img src="assets/logo.png" width="500" alt="Automater">
</p>

# Contributing to Automater

Personal automation tool for Stux.Group internal QA/regression testing and
first-party data scraping.

## Setup

1. Python 3.10+
2. `pip install -r requirements.txt`
3. `playwright install chromium` (skip if you always point at an external
   Brave/Chrome executable via `browser.executable_path`)

## Adding a new action type

Add a small async function to `automator/actions.py` decorated with
`@action("your_action_name")`. It receives the shared `ExecutionContext`
(page, macros, results dict) and the resolved step dict. No other file
needs to change - the runner and hotkey system dispatch by name
automatically. Add a matching entry to `automator/schema.py`'s
`ACTION_SCHEMA` too, so the GUI's Add Action dialog and config validation
(`automator/validate.py`) both pick it up - `tests/test_schema.py` fails
the build if the two ever drift out of sync.

## Running tests

```
pip install -e ".[dev]"
pytest
```

## Release flow

1. Update `CHANGELOG.md`.
2. Bump `VERSION.md` (semantic versioning).
3. Update `README.md` if behavior changed.
4. Run the test suite (`pytest`) - keep it green.
5. Run `commit.bat "message"` (or `commit.sh` on POSIX) - it commits and
   tags `vX.Y.Z` from `VERSION.md`.
6. Optionally, `build.bat` (or `build.sh`) to refresh the standalone
   `dist/Automater.exe` / `AutomaterCLI.exe` for that release.
