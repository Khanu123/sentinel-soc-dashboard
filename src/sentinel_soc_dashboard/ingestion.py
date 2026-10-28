"""Explicit input validation and auditable exact-event deduplication."""
from dataclasses import dataclass
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path


class AlertInputError(ValueError):
    """An input file or row does not satisfy the alert schema."""


@dataclass
class LoadResult:
    alerts: list
    input_rows: int
    duplicates_removed: int
    issues: list[dict]

    def diagnostics(self):
        return dict(input_rows=self.input_rows, accepted_alerts=len(self.alerts),
                    duplicates_removed=self.duplicates_removed,
                    rejected_rows=len(self.issues), issues=self.issues)


def parse_row(row, row_number):
    from .core import Alert
    if not isinstance(row, dict):
        raise AlertInputError(f'Row {row_number}: expected a JSON object')

    def text(key, default=None, required=False):
        value = row.get(key, default)
        if not isinstance(value, str) or (required and not value.strip()):
            raise AlertInputError(f'Row {row_number}: {key} must be a ' + ('non-empty string' if required else 'string'))
        return value.strip()

    raw_timestamp = text('timestamp', required=True)
    if 'T' not in raw_timestamp and ' ' not in raw_timestamp:
        raise AlertInputError(f'Row {row_number}: timestamp must include a date and time')
    try:
        stamp = datetime.fromisoformat(raw_timestamp.replace('Z', '+00:00'))
        stamp = stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise AlertInputError(f'Row {row_number}: timestamp must be a valid ISO-8601 date and time') from None
    severity = text('severity', required=True).lower()
    if severity not in {'low', 'medium', 'high', 'critical'}:
        raise AlertInputError(f'Row {row_number}: severity must be low, medium, high, or critical')
    source_ip = text('source_ip', '')
    if source_ip:
        try:
            source_ip = str(ipaddress.ip_address(source_ip))
        except ValueError:
            raise AlertInputError(f'Row {row_number}: source_ip must be an IP address or empty') from None
    status = text('status', 'open').lower()
    if status not in {'open', 'closed'}:
        raise AlertInputError(f'Row {row_number}: status must be open or closed')
    confidence = text('confidence', 'medium').lower()
    if confidence not in {'low', 'medium', 'high'}:
        raise AlertInputError(f'Row {row_number}: confidence must be low, medium, or high')
    iocs = row.get('iocs', [])
    if not isinstance(iocs, list) or any(not isinstance(value, str) for value in iocs):
        raise AlertInputError(f'Row {row_number}: iocs must be a list of strings')
    return Alert(timestamp=stamp, title=text('title', required=True), severity=severity,
                 source_ip=source_ip, host=text('host', ''), user=text('user', ''),
                 tactic=text('tactic', 'unknown'), status=status,
                 source=text('source', 'siem'), confidence=confidence,
                 false_positive_hint=text('false_positive_hint', ''),
                 analyst_note=text('analyst_note', ''), iocs=tuple(value.strip() for value in iocs))


def load_alerts_report(path, *, skip_invalid=False, deduplicate=True):
    """Strict by default; skip_invalid is an explicit, diagnosed partial-load mode.

    Deduplication compares every normalised Alert field, including timestamps and
    analyst context. It never merges alerts solely because their titles match.
    Unknown fields are ignored; this is the supported lab schema, not a SIEM adapter.
    """
    try:
        rows = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except json.JSONDecodeError as exc:
        raise AlertInputError(f'Invalid JSON at line {exc.lineno}, column {exc.colno}') from None
    if not isinstance(rows, list):
        raise AlertInputError('Alert input must be a JSON array')
    alerts, issues, seen = [], [], set()
    duplicates = 0
    for number, row in enumerate(rows, 1):
        try:
            alert = parse_row(row, number)
        except AlertInputError as exc:
            issues.append(dict(row=number, error=str(exc)))
            continue
        if deduplicate and alert in seen:
            duplicates += 1
            continue
        seen.add(alert)
        alerts.append(alert)
    if issues and not skip_invalid:
        raise AlertInputError(f'{len(issues)} invalid row(s); no report generated. ' + issues[0]['error'])
    if rows and not alerts:
        raise AlertInputError('No valid alerts remain; no report generated')
    return LoadResult(alerts, len(rows), duplicates, issues)
