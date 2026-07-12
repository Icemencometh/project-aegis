from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from .allocation_adapter import AllocationParityAdapter
from .execution_adapter import ExecutionParityAdapter
from .portfolio_adapter import PortfolioParityAdapter
from .regime_adapter import RegimeParityAdapter
from .risk_adapter import RiskParityAdapter
from .scoring_adapter import ScoringParityAdapter


def run_all() -> List[dict]:
    adapters = [
        ScoringParityAdapter(),
        RiskParityAdapter(),
        AllocationParityAdapter(),
        RegimeParityAdapter(),
        ExecutionParityAdapter(),
        PortfolioParityAdapter(),
    ]
    return [asdict(adapter.run()) for adapter in adapters]


def write_reports(results: List[dict], output_dir: str = "artifacts/parity") -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out / f"parity_{timestamp}.json"
    md_path = out / f"parity_{timestamp}.md"

    summary = {
        "timestamp": timestamp,
        "total": len(results),
        "passed": sum(1 for item in results if item.get("ok")),
        "failed": sum(1 for item in results if not item.get("ok")),
        "results": results,
    }

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Parity Report",
        "",
        f"- Timestamp: {timestamp}",
        f"- Total: {summary['total']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        "",
        "## Details",
    ]
    for item in results:
        status = "PASS" if item.get("ok") else "FAIL"
        lines.append(f"- {item['name']}: {status} (diff={item['diff']:.4f}, threshold={item['threshold']:.4f})")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"json": str(json_path), "markdown": str(md_path), "summary": summary}


def main() -> int:
    report = write_reports(run_all())
    print("Parity report JSON:", report["json"])
    print("Parity report Markdown:", report["markdown"])
    failed = int(report["summary"]["failed"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
