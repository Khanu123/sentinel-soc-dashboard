from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ingestion import load_alerts_report
from .core import load_config, triage, write_csv, write_html, write_json, write_markdown


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Prioritize SOC alerts into analyst-ready cases.")
    parser.add_argument("--alerts", default=str(ROOT / "sample_data" / "alerts.json"))
    parser.add_argument("--config", help="Optional triage scoring config JSON.")
    parser.add_argument("--html", default="soc_report.html")
    parser.add_argument("--csv", default="soc_cases.csv")
    parser.add_argument("--json", default="soc_cases.json")
    parser.add_argument("--markdown", default="soc_report.md")
    parser.add_argument("--skip-invalid", action="store_true", help="Skip invalid rows with diagnostics instead of failing.")
    parser.add_argument("--keep-duplicates", action="store_true", help="Retain exact duplicate alerts for comparison.")
    parser.add_argument("--diagnostics", help="Optional path for input-quality diagnostics JSON.")
    args = parser.parse_args()

    try:
        loaded = load_alerts_report(args.alerts, skip_invalid=args.skip_invalid,
                                    deduplicate=not args.keep_duplicates)
        alerts = loaded.alerts
        cases = triage(alerts, load_config(args.config))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.diagnostics:
        Path(args.diagnostics).write_text(json.dumps(loaded.diagnostics(), indent=2) + "\n", encoding="utf-8")
    write_html(alerts, cases, args.html)
    write_csv(cases, args.csv)
    write_json(cases, args.json)
    write_markdown(cases, args.markdown)

    print(f"Input rows: {loaded.input_rows}; duplicates removed: {loaded.duplicates_removed}; rejected rows: {len(loaded.issues)}.")
    for issue in loaded.issues:
        print(issue['error'])
    print(f"Loaded {len(alerts)} alerts.")
    print(f"Created {len(cases)} prioritized cases.")
    print(f"HTML report: {args.html}")
    print(f"CSV report: {args.csv}")
    print(f"JSON report: {args.json}")
    print(f"Markdown report: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
