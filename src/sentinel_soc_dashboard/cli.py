from __future__ import annotations

import argparse
from pathlib import Path

from .core import load_alerts, triage, write_csv, write_html


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Prioritize SOC alerts into analyst-ready cases.")
    parser.add_argument("--alerts", default=str(ROOT / "sample_data" / "alerts.json"))
    parser.add_argument("--html", default="soc_report.html")
    parser.add_argument("--csv", default="soc_cases.csv")
    args = parser.parse_args()

    alerts = load_alerts(args.alerts)
    cases = triage(alerts)
    write_html(alerts, cases, args.html)
    write_csv(cases, args.csv)

    print(f"Loaded {len(alerts)} alerts.")
    print(f"Created {len(cases)} prioritized cases.")
    print(f"HTML report: {args.html}")
    print(f"CSV report: {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
