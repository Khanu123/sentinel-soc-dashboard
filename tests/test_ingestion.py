from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sentinel_soc_dashboard.core import load_alerts, triage, write_html
from sentinel_soc_dashboard.ingestion import AlertInputError, load_alerts_report


CHILD_ENV = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / 'src'))

ROW = dict(timestamp='2026-10-28T10:00:00Z', title='Synthetic login', severity='high',
           source_ip='192.0.2.1', host='lab-01', user='lab-user', tactic='Credential Access')


class InputQualityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'alerts.json'

    def write(self, rows):
        self.path.write_text(json.dumps(rows), encoding='utf-8')
        return self.path

    def test_missing_required_fields_are_actionable(self):
        for field in ('timestamp', 'title', 'severity'):
            row = deepcopy(ROW)
            del row[field]
            with self.subTest(field=field), self.assertRaisesRegex(AlertInputError, field):
                load_alerts(self.write([row]))

    def test_bad_timestamp_and_date_only_are_rejected(self):
        for stamp in ('yesterday', '2026-02-30T10:00:00Z', '2026-10-28', 12, None):
            with self.subTest(stamp=stamp), self.assertRaisesRegex(AlertInputError, 'timestamp'):
                load_alerts(self.write([dict(ROW, timestamp=stamp)]))

    def test_bad_severity_never_silently_gets_zero_weight(self):
        with self.assertRaisesRegex(AlertInputError, 'severity'):
            load_alerts(self.write([dict(ROW, severity='urgent')]))

    def test_wrong_optional_types_and_invalid_values_rejected(self):
        for field, value in [('source_ip', 'bad-ip'), ('host', None), ('iocs', '192.0.2.1'),
                             ('iocs', [123]), ('status', 'investigating'), ('confidence', 'certain')]:
            with self.subTest(field=field, value=value), self.assertRaisesRegex(AlertInputError, field):
                load_alerts(self.write([dict(ROW, **{field: value})]))

    def test_malformed_json_has_line_number(self):
        self.path.write_text('[{', encoding='utf-8')
        with self.assertRaisesRegex(AlertInputError, 'line 1'):
            load_alerts(self.path)

    def test_top_level_must_be_array_and_rows_must_be_objects(self):
        for value in ({'alerts': []}, [None]):
            with self.subTest(value=value), self.assertRaises(AlertInputError):
                load_alerts(self.write(value))

    def test_equivalent_offsets_deduplicate_after_normalisation(self):
        row = dict(ROW, timestamp='2026-10-28T11:00:00+01:00', severity=' HIGH ')
        result = load_alerts_report(self.write([ROW, row]))
        self.assertEqual((len(result.alerts), result.duplicates_removed), (1, 1))

    def test_different_time_or_context_is_retained(self):
        rows = [ROW, dict(ROW, timestamp='2026-10-28T10:00:01Z'), dict(ROW, analyst_note='Additional context')]
        self.assertEqual(len(load_alerts(self.write(rows))), 3)

    def test_keep_duplicates_is_explicit(self):
        result = load_alerts_report(self.write([ROW, ROW]), deduplicate=False)
        self.assertEqual(len(result.alerts), 2)
        self.assertEqual(result.duplicates_removed, 0)

    def test_partial_load_requires_opt_in_and_accounts_for_every_row(self):
        rows = [ROW, ROW, dict(ROW, severity='urgent')]
        with self.assertRaises(AlertInputError):
            load_alerts_report(self.write(rows))
        result = load_alerts_report(self.path, skip_invalid=True)
        self.assertEqual(result.diagnostics(), dict(input_rows=3, accepted_alerts=1,
            duplicates_removed=1, rejected_rows=1,
            issues=[dict(row=3, error='Row 3: severity must be low, medium, high, or critical')]))

    def test_all_invalid_fails_even_in_partial_mode(self):
        with self.assertRaisesRegex(AlertInputError, 'No valid alerts'):
            load_alerts_report(self.write([{}]), skip_invalid=True)

    def test_missing_identity_is_retained_for_separate_review(self):
        row = {key: value for key, value in ROW.items() if key not in ('host', 'source_ip')}
        self.assertEqual(load_alerts(self.write([row]))[0].host, '')

    def test_empty_file_array_and_utf8_bom(self):
        self.path.write_text('\ufeff[]', encoding='utf-8')
        self.assertEqual(load_alerts(self.path), [])

    def test_html_renders_input_as_text_not_markup(self):
        alerts = load_alerts(self.write([dict(ROW, host='<script>alert(1)</script>',
                                           analyst_note='<img src=x onerror=alert(2)>')]))
        output = Path(self.tmp.name) / 'report.html'
        write_html(alerts, triage(alerts), output)
        html = output.read_text()
        self.assertNotIn('<script>', html)
        self.assertNotIn('<img src=x', html)
        self.assertIn('&lt;script&gt;', html)

    def test_cli_rejects_invalid_input_before_writing_reports(self):
        source = self.write([dict(ROW, severity='urgent')])
        result = subprocess.run([sys.executable, '-m', 'sentinel_soc_dashboard.cli', '--alerts', str(source)],
                                cwd=self.tmp.name, capture_output=True, text=True, env=CHILD_ENV)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Row 1: severity', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse((Path(self.tmp.name) / 'soc_report.html').exists())

    def test_cli_partial_mode_writes_diagnostics(self):
        source = self.write([ROW, dict(ROW, severity='urgent')])
        diagnostic = Path(self.tmp.name) / 'quality.json'
        result = subprocess.run([sys.executable, '-m', 'sentinel_soc_dashboard.cli', '--alerts', str(source),
                                 '--skip-invalid', '--diagnostics', str(diagnostic)],
                                cwd=self.tmp.name, capture_output=True, text=True, env=CHILD_ENV)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(diagnostic.read_text())['rejected_rows'], 1)
        self.assertTrue((Path(self.tmp.name) / 'soc_report.html').exists())
