from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SEVERITY_WEIGHT = {"critical": 100, "high": 75, "medium": 45, "low": 20}


@dataclass(frozen=True)
class Alert:
    timestamp: datetime
    title: str
    severity: str
    source_ip: str
    host: str
    user: str
    tactic: str
    status: str = "open"


def load_alerts(path: str | Path) -> list[Alert]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        Alert(
            timestamp=datetime.fromisoformat(row["timestamp"]),
            title=row["title"],
            severity=row["severity"].lower(),
            source_ip=row.get("source_ip", ""),
            host=row.get("host", ""),
            user=row.get("user", ""),
            tactic=row.get("tactic", "unknown"),
            status=row.get("status", "open"),
        )
        for row in rows
    ]


def triage(alerts: list[Alert]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[Alert]] = defaultdict(list)
    for alert in alerts:
        grouped[(alert.source_ip, alert.host)].append(alert)

    cases = []
    for (source_ip, host), items in grouped.items():
        severity_score = max(SEVERITY_WEIGHT.get(item.severity, 0) for item in items)
        volume_score = min(len(items) * 8, 40)
        tactics = sorted({item.tactic for item in items})
        priority = min(severity_score + volume_score + len(tactics) * 5, 100)
        cases.append(
            {
                "source_ip": source_ip,
                "host": host,
                "alert_count": len(items),
                "top_severity": max(items, key=lambda item: SEVERITY_WEIGHT.get(item.severity, 0)).severity,
                "tactics": ", ".join(tactics),
                "priority": priority,
                "recommended_action": recommendation(priority),
            }
        )
    return sorted(cases, key=lambda item: item["priority"], reverse=True)


def recommendation(priority: int) -> str:
    if priority >= 90:
        return "Escalate immediately, isolate host, preserve evidence, and review account activity."
    if priority >= 70:
        return "Investigate within SLA, enrich source IP, and validate endpoint telemetry."
    if priority >= 45:
        return "Queue for analyst review and correlate with recent authentication events."
    return "Monitor and close if no additional suspicious activity appears."


def summary(alerts: list[Alert]) -> dict[str, object]:
    return {
        "total_alerts": len(alerts),
        "by_severity": dict(Counter(alert.severity for alert in alerts)),
        "by_tactic": dict(Counter(alert.tactic for alert in alerts)),
        "open_alerts": sum(1 for alert in alerts if alert.status == "open"),
    }


def write_csv(cases: list[dict[str, object]], path: str | Path) -> None:
    fieldnames = ["source_ip", "host", "alert_count", "top_severity", "tactics", "priority", "recommended_action"]
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cases)


def write_html(alerts: list[Alert], cases: list[dict[str, object]], path: str | Path) -> None:
    counts = summary(alerts)
    rows = "\n".join(
        f"<tr><td>{case['priority']}</td><td>{case['source_ip']}</td><td>{case['host']}</td>"
        f"<td>{case['top_severity']}</td><td>{case['alert_count']}</td><td>{case['tactics']}</td>"
        f"<td>{case['recommended_action']}</td></tr>"
        for case in cases
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SOC Triage Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #14213d; }}
    .metrics {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .metric {{ border: 1px solid #d8dee9; border-radius: 8px; padding: 16px; min-width: 150px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 24px; }}
    th, td {{ border-bottom: 1px solid #d8dee9; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f7; }}
  </style>
</head>
<body>
  <h1>SOC Alert Triage Report</h1>
  <div class="metrics">
    <div class="metric"><strong>Total Alerts</strong><br>{counts['total_alerts']}</div>
    <div class="metric"><strong>Open Alerts</strong><br>{counts['open_alerts']}</div>
    <div class="metric"><strong>Cases</strong><br>{len(cases)}</div>
  </div>
  <h2>Prioritized Cases</h2>
  <table>
    <thead><tr><th>Priority</th><th>Source IP</th><th>Host</th><th>Severity</th><th>Alerts</th><th>Tactics</th><th>Action</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>
"""
    Path(path).write_text(html, encoding="utf-8")
