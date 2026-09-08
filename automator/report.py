"""Generates a JSON + HTML run report from ExecutionContext.step_results.

Written for the QA/regression use case: after a run, you want a pass/fail
summary with timings and failure screenshots, not just a scrollback log.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from automator.actions import StepResult

_STATUS_COLOR = {"passed": "#2da44e", "failed": "#cf222e", "continued": "#bf8700"}


def _summary(step_results: list[StepResult]) -> dict:
    counts = {"passed": 0, "failed": 0, "continued": 0}
    for r in step_results:
        counts[r.status] = counts.get(r.status, 0) + 1
    return {
        "total": len(step_results),
        **counts,
        "total_duration_ms": sum(r.duration_ms for r in step_results),
    }


def _screenshot_href(screenshot: str, report_dir: Path) -> str:
    """report.html lives at the root of report_dir, so links must be relative
    to *that*, not to the working directory the screenshot path was recorded
    against - otherwise the href resolves to a doubly-nested, nonexistent path.
    """
    resolved = Path(screenshot).resolve()
    try:
        return resolved.relative_to(report_dir).as_posix()
    except ValueError:
        return resolved.as_uri()


def _render_html(run_name: str, generated_at: str, step_results: list[StepResult], summary: dict, report_dir: Path) -> str:
    rows = []
    for r in step_results:
        color = _STATUS_COLOR.get(r.status, "#57606a")
        screenshot_html = ""
        if r.screenshot:
            screenshot_html = f'<br><a href="{escape(_screenshot_href(r.screenshot, report_dir))}">screenshot</a>'
        error_html = f"<br><code>{escape(r.error)}</code>{screenshot_html}" if r.error else ""
        rows.append(
            "<tr>"
            f"<td>{r.index}</td>"
            f"<td>{escape(r.action)}</td>"
            f'<td style="color:{color};font-weight:600">{r.status}</td>'
            f"<td>{r.attempts}</td>"
            f"<td>{r.duration_ms:.0f}</td>"
            f"<td>{error_html}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{escape(run_name)} - run report</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1f2328; }}
  h1 {{ margin-bottom: 0.2rem; }}
  .meta {{ color: #57606a; margin-bottom: 1.5rem; }}
  .summary {{ display: flex; gap: 1.5rem; margin-bottom: 1.5rem; }}
  .summary div {{ font-size: 1.1rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #f6f8fa; }}
  code {{ font-size: 0.85em; }}
</style>
</head>
<body>
<h1>{escape(run_name)}</h1>
<div class="meta">Generated {escape(generated_at)}</div>
<div class="summary">
  <div>Total: {summary['total']}</div>
  <div style="color:{_STATUS_COLOR['passed']}">Passed: {summary['passed']}</div>
  <div style="color:{_STATUS_COLOR['failed']}">Failed: {summary['failed']}</div>
  <div style="color:{_STATUS_COLOR['continued']}">Continued: {summary['continued']}</div>
  <div>Duration: {summary['total_duration_ms']:.0f} ms</div>
</div>
<table>
  <thead><tr><th>#</th><th>Action</th><th>Status</th><th>Attempts</th><th>ms</th><th>Error</th></tr></thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
</body>
</html>
"""


def generate_report(step_results: list[StepResult], report_dir: str, run_name: str = "Automater run") -> tuple[str, str]:
    """Writes report.json and report.html into report_dir. Returns (json_path, html_path)."""
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir_resolved = out_dir.resolve()

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = _summary(step_results)

    json_path = out_dir / "report.json"
    json_path.write_text(
        json.dumps(
            {
                "run_name": run_name,
                "generated_at": generated_at,
                "summary": summary,
                "steps": [r.as_dict() for r in step_results],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    html_path = out_dir / "report.html"
    html_path.write_text(
        _render_html(run_name, generated_at, step_results, summary, out_dir_resolved), encoding="utf-8"
    )

    return str(json_path), str(html_path)
