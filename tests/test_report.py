import json
from pathlib import Path

from twrar.actions import StepResult
from twrar.report import generate_report


def _results():
    return [
        StepResult(index=1, action="goto", status="passed", duration_ms=120.0, attempts=1),
        StepResult(index=2, action="click", status="failed", duration_ms=50.0, attempts=2, error="boom", screenshot="out/step-002.png"),
        StepResult(index=3, action="scrape", status="continued", duration_ms=10.0, attempts=1, error="meh"),
    ]


def test_generate_report_writes_json_and_html(tmp_path):
    json_path, html_path = generate_report(_results(), str(tmp_path), run_name="My Run")

    assert Path(json_path).exists()
    assert Path(html_path).exists()
    assert json_path == str(tmp_path / "report.json")
    assert html_path == str(tmp_path / "report.html")


def test_report_json_summary_counts_are_correct(tmp_path):
    json_path, _ = generate_report(_results(), str(tmp_path))
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    assert data["summary"]["total"] == 3
    assert data["summary"]["passed"] == 1
    assert data["summary"]["failed"] == 1
    assert data["summary"]["continued"] == 1
    assert data["summary"]["total_duration_ms"] == 180.0
    assert len(data["steps"]) == 3
    assert data["steps"][1]["error"] == "boom"


def test_report_html_contains_status_and_error(tmp_path):
    _, html_path = generate_report(_results(), str(tmp_path), run_name="My Run")
    html = Path(html_path).read_text(encoding="utf-8")

    assert "My Run" in html
    assert "goto" in html
    assert "boom" in html
    assert "Passed: 1" in html
    assert "Failed: 1" in html
    assert "Continued: 1" in html


def test_report_html_escapes_error_text(tmp_path):
    results = [StepResult(index=1, action="click", status="failed", duration_ms=1.0, attempts=1, error="<script>alert(1)</script>")]
    _, html_path = generate_report(results, str(tmp_path))
    html = Path(html_path).read_text(encoding="utf-8")

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_generate_report_creates_report_dir(tmp_path):
    nested = tmp_path / "nested" / "report"
    generate_report(_results(), str(nested))
    assert nested.exists()


def test_empty_step_results_still_produces_a_report(tmp_path):
    json_path, html_path = generate_report([], str(tmp_path))
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    assert data["summary"]["total"] == 0
    assert Path(html_path).exists()


def test_screenshot_link_is_relative_to_the_report_dir(tmp_path):
    # Mirrors ExecutionContext's real layout: screenshot_dir = report_dir/screenshots.
    screenshot_dir = tmp_path / "screenshots"
    screenshot_dir.mkdir()
    screenshot_path = screenshot_dir / "step-002-failure.png"
    screenshot_path.write_bytes(b"fake-png")

    results = [
        StepResult(index=2, action="click", status="failed", duration_ms=50.0, attempts=1, error="boom", screenshot=str(screenshot_path)),
    ]
    _, html_path = generate_report(results, str(tmp_path))
    html = Path(html_path).read_text(encoding="utf-8")

    assert 'href="screenshots/step-002-failure.png"' in html
    # The buggy version doubled the report_dir prefix into the href - guard against regressing that.
    assert str(tmp_path.name) not in html.split('href="')[1].split('"')[0]


def test_screenshot_outside_report_dir_falls_back_to_a_file_uri(tmp_path):
    outside_dir = tmp_path.parent / "elsewhere_screenshots"
    outside_dir.mkdir(exist_ok=True)
    screenshot_path = outside_dir / "step-001.png"
    screenshot_path.write_bytes(b"fake-png")

    report_dir = tmp_path / "report"
    results = [
        StepResult(index=1, action="click", status="failed", duration_ms=1.0, attempts=1, error="boom", screenshot=str(screenshot_path)),
    ]
    _, html_path = generate_report(results, str(report_dir))
    html = Path(html_path).read_text(encoding="utf-8")

    assert 'href="file:' in html
