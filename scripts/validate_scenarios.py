"""Generate contrasting, explicitly authored synthetic investigation exercises."""
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sentinel_soc_dashboard.core import Alert, triage, write_html
from sentinel_soc_dashboard.ingestion import AlertInputError, load_alerts_report


def main():
    start = datetime(2026, 10, 28, 10, tzinfo=timezone.utc)
    rows = []
    for i in range(6):
        rows.append(Alert(start + timedelta(minutes=i), 'Synthetic failed login' if i < 5 else 'Synthetic successful login',
                          'high' if i < 5 else 'critical', '203.0.113.44', 'identity-lab', 'lab-admin',
                          'Credential Access' if i < 5 else 'Initial Access',
                          analyst_note='No approved activity in the exercise context. Verify identity and endpoint telemetry.'))
    for i in range(3):
        rows.append(Alert(start + timedelta(minutes=i), 'Synthetic scanner finding', 'high',
                          '198.51.100.20', 'maintenance-lab', '-', 'Reconnaissance',
                          false_positive_hint='Authored ticket LAB-043 authorises this source and target from 10:00 to 10:15 UTC.'))
    for i in range(2):
        rows.append(Alert(start + timedelta(minutes=i), 'Synthetic encoded administration command', 'medium',
                          '192.0.2.50', 'unresolved-lab', 'lab-operator', 'Execution',
                          analyst_note='The exercise provides no parent process, command contents, or verified change ticket.',
                          false_positive_hint='An administrator says this may be maintenance; the claim is not corroborated.'))
    serial = [dict(asdict(row), timestamp=row.timestamp.isoformat()) for row in rows]
    serial += [dict(serial[0]), dict(serial[0], timestamp='not-a-time'),
               dict(serial[0], severity='urgent'), {key: value for key, value in serial[0].items() if key != 'title'}]
    fixture = ROOT / 'sample_data' / 'investigation_scenarios.json'
    fixture.write_text(json.dumps(serial, indent=2) + '\n', encoding='utf-8')
    try:
        load_alerts_report(fixture)
    except AlertInputError:
        strict_rejected = True
    else:
        strict_rejected = False
    loaded = load_alerts_report(fixture, skip_invalid=True)
    cases = triage(loaded.alerts)
    by_host = {case['host']: case for case in cases}
    decisions = {
        'identity-lab': {'hypothesis': 'Possible account compromise', 'review_decision': 'Escalate for investigation',
                         'reason': 'Failures followed by success, privileged account, and no authorised activity context; compromise is not confirmed.'},
        'maintenance-lab': {'hypothesis': 'Possible hostile scanning', 'review_decision': 'Authorised activity within this exercise',
                            'reason': 'Authored ticket matches source, target, and time. Preserve context; do not create a permanent blanket allowlist.'},
        'unresolved-lab': {'hypothesis': 'Possible suspicious execution or administration', 'review_decision': 'Unresolved: collect more evidence',
                           'reason': 'A verbal maintenance explanation without command contents or parent-process evidence is insufficient for closure.'},
    }
    checks = {
        'strict_mode_rejects_invalid_rows': strict_rejected,
        'input_rows_15': loaded.input_rows == 15,
        'accepted_alerts_11': len(loaded.alerts) == 11,
        'one_duplicate_removed': loaded.duplicates_removed == 1,
        'three_rejected_rows_diagnosed': len(loaded.issues) == 3,
        'three_distinct_cases': len(cases) == 3,
        'suspicious_sequence_retained': by_host['identity-lab']['alert_count'] == 6,
        'maintenance_context_retained': 'LAB-043' in by_host['maintenance-lab']['false_positive_handling'],
        'ambiguous_context_retained': 'not corroborated' in by_host['unresolved-lab']['false_positive_handling'],
        'all_rows_accounted_for': loaded.input_rows == len(loaded.alerts) + loaded.duplicates_removed + len(loaded.issues),
    }
    target = ROOT / 'docs' / 'validation'
    output = dict(scope='Synthetic authored exercises. Review decisions are narrative interpretations, not automated classifications.',
                  input_quality=loaded.diagnostics(), checks=checks,
                  passed=sum(checks.values()), total=len(checks),
                  cases=[dict(case, exercise_review=decisions[case['host']]) for case in cases])
    (target / 'scenario-results.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    write_html(loaded.alerts, cases, target / 'scenario-report.html')
    print(json.dumps(dict(loaded.diagnostics(), cases=len(cases), checks_passed=sum(checks.values()), checks_total=len(checks))))
    if not all(checks.values()):
        raise SystemExit('Scenario checks failed')


if __name__ == '__main__':
    main()
