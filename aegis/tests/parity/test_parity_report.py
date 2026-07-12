from __future__ import annotations

from pathlib import Path

from aegis.parity.report import run_all, write_reports


def test_parity_report_generation(tmp_path: Path):
    results = run_all()
    report = write_reports(results, output_dir=str(tmp_path))
    assert Path(report["json"]).exists()
    assert Path(report["markdown"]).exists()
    assert report["summary"]["total"] == 6
    assert report["summary"]["failed"] == 0
    assert report["summary"]["passed"] == 6
