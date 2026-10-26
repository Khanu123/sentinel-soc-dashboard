"""Deterministic synthetic regression exercise; not a detection benchmark."""
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sentinel_soc_dashboard.core import Alert, triage


def build_fixture():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    rows = []
    for identity in range(50):
        for day in range(10):
            for minute in (0, 5):
                rows.append(Alert(start + timedelta(days=day, minutes=minute),
                    'Synthetic routine authentication failure', 'low',
                    f'192.0.2.{identity + 1}', f'lab-{identity:02}', 'lab-user', 'Credential Access'))
    for minute in range(6):
        rows.append(Alert(start + timedelta(hours=12, minutes=minute),
            'Synthetic approved scanner finding', 'high', '198.51.100.20', 'portal-lab', '-',
            'Reconnaissance', false_positive_hint='Exercise ticket LAB-042 authorises this source and target between 12:00 and 12:15 UTC. Verify scope and timing.'))
        rows.append(Alert(start + timedelta(hours=14, minutes=minute),
            'Synthetic failed login' if minute < 5 else 'Synthetic successful login',
            'high' if minute < 5 else 'critical', '203.0.113.44', 'identity-lab', 'lab-admin',
            'Credential Access' if minute < 5 else 'Initial Access'))
    rows.extend(Alert(start + timedelta(minutes=i), 'Synthetic incomplete identity', 'medium', '', '', '-', 'Discovery') for i in (1, 2))
    random.Random(42).shuffle(rows)
    return rows


def main():
    rows = build_fixture()
    serialised = [dict(asdict(row), timestamp=row.timestamp.isoformat()) for row in rows]
    fixture = json.dumps(serialised, indent=2) + '\n'
    legacy = triage(rows, window_minutes=None)
    bounded = triage(rows)
    background = [c for c in bounded if c['host'].startswith('lab-')]
    scanner = next(c for c in bounded if c['host'] == 'portal-lab')
    attack = next(c for c in bounded if c['host'] == 'identity-lab')
    checks = {
        'fixture_has_1014_alerts': len(rows) == 1014,
        'bounded_has_504_cases': len(bounded) == 504,
        'legacy_has_54_cases': len(legacy) == 54,
        'daily_background_sessions_separated': len(background) == 500 and all(c['alert_count'] == 2 for c in background),
        'all_alerts_preserved': sum(c['alert_count'] for c in bounded) == len(rows),
        'unknown_identities_kept_separate': len([c for c in bounded if not c['host']]) == 2,
        'scanner_context_preserved': 'LAB-042' in scanner['false_positive_handling'],
        'scanner_still_requires_manual_review': scanner['priority'] == 100,
        'attack_sequence_still_prioritised': attack['priority'] == 100 and attack['alert_count'] == 6,
        'shuffle_preserves_case_count': len(triage(list(reversed(rows)))) == len(bounded),
    }
    report = {
        'scope': 'Deterministic synthetic regression exercise, not operational detection accuracy or a performance benchmark.',
        'fixture_sha256': hashlib.sha256(fixture.encode()).hexdigest(),
        'alerts': len(rows), 'legacy_cases': len(legacy), 'bounded_cases': len(bounded),
        'checks': checks, 'passed': sum(checks.values()), 'total': len(checks),
        'scanner_case': scanner, 'attack_case': attack,
        'limitations': ['No Splunk or Sentinel execution.', 'No real incidents or employee data.',
            'High-volume benign activity can still reach priority 100.',
            'Fixed windows can split related activity across a boundary.',
            'Duplicate alerts are retained; upstream deduplication is not implemented.'],
    }
    (ROOT / 'sample_data' / 'extended_alerts.json').write_text(fixture, encoding='utf-8')
    target = ROOT / 'docs' / 'validation'
    target.mkdir(parents=True, exist_ok=True)
    (target / 'extended-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('alerts', 'legacy_cases', 'bounded_cases', 'passed', 'total')}))
    if not all(checks.values()):
        raise SystemExit('Validation failed: ' + ', '.join(k for k, v in checks.items() if not v))


if __name__ == '__main__':
    main()
