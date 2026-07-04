import unittest

from sentinel_soc_dashboard.core import Alert, case_summary, load_config, recommendation, triage
from datetime import datetime


class SocTriageTests(unittest.TestCase):
    def test_critical_case_gets_top_priority(self):
        alerts = [
            Alert(datetime(2026, 7, 4, 9, 0), "fail", "high", "1.1.1.1", "web-01", "admin", "Credential Access"),
            Alert(datetime(2026, 7, 4, 9, 1), "success", "critical", "1.1.1.1", "web-01", "admin", "Initial Access"),
        ]

        cases = triage(alerts)

        self.assertEqual(cases[0]["source_ip"], "1.1.1.1")
        self.assertGreaterEqual(cases[0]["priority"], 90)

    def test_recommendation_escalates_highest_priority(self):
        self.assertIn("Escalate", recommendation(95))

    def test_case_contains_mitre_and_sla_context(self):
        alerts = [
            Alert(
                datetime(2026, 7, 4, 9, 0),
                "Successful login after failures",
                "critical",
                "1.1.1.1",
                "web-01",
                "admin",
                "Initial Access",
            )
        ]

        case = triage(alerts, load_config())[0]

        self.assertIn("T1078", case["mitre"])
        self.assertEqual(case["sla"], "Immediate escalation")
        self.assertIn("Priority", case_summary(case))


if __name__ == "__main__":
    unittest.main()
