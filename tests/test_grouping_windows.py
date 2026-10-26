import unittest
from datetime import datetime, timedelta, timezone
from sentinel_soc_dashboard.core import Alert, triage


def event(minutes=0, source='192.0.2.10', host='lab-01'):
    return Alert(datetime(2026, 10, 1, tzinfo=timezone.utc) + timedelta(minutes=minutes),
                 'Synthetic authentication alert', 'low', source, host, 'lab-user', 'Credential Access')


class GroupingWindowTests(unittest.TestCase):
    def test_separate_days_are_separate_cases(self):
        self.assertEqual(len(triage([event(), event(1440)])), 2)

    def test_legacy_mode_reproduces_unbounded_merge(self):
        self.assertEqual(len(triage([event(), event(1440)], window_minutes=None)), 1)

    def test_exact_boundary_is_inclusive(self):
        self.assertEqual(len(triage([event(), event(30)])), 1)

    def test_just_outside_boundary_splits(self):
        self.assertEqual(len(triage([event(), event(30 + 1/60)])), 2)

    def test_window_does_not_chain_indefinitely(self):
        self.assertEqual(sorted(c['alert_count'] for c in triage([event(), event(20), event(40)])), [1, 2])

    def test_shuffled_input_has_same_output(self):
        rows = [event(), event(10), event(1440)]
        self.assertEqual(triage(rows), triage(list(reversed(rows))))

    def test_missing_source_is_not_correlated(self):
        self.assertEqual(len(triage([event(source=''), event(1, source='')])), 2)

    def test_missing_host_is_not_correlated(self):
        self.assertEqual(len(triage([event(host=''), event(1, host='')])), 2)

    def test_distinct_hosts_stay_separate(self):
        self.assertEqual(len(triage([event(), event(host='lab-02')])), 2)

    def test_naive_and_aware_timestamps_interoperate(self):
        from dataclasses import replace
        aware = event()
        naive = replace(event(1), timestamp=datetime(2026, 10, 1, 0, 1))
        offset = replace(event(2), timestamp=datetime(2026, 10, 1, 1, 2, tzinfo=timezone(timedelta(hours=1))))
        self.assertEqual(triage([offset, naive, aware])[0]['alert_count'], 3)

    def test_invalid_windows_rejected(self):
        for window in [0, -1, float('nan'), float('inf')]:
            with self.subTest(window=window), self.assertRaises(ValueError):
                triage([event()], window_minutes=window)

    def test_empty_input_and_no_input_mutation(self):
        self.assertEqual(triage([]), [])
        rows = [event(10), event()]
        saved = list(rows)
        triage(rows)
        self.assertEqual(rows, saved)
