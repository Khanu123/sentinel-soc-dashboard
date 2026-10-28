# From input to investigation: three contrasting cases

These are authored synthetic exercises, not workplace incidents. The tool calculates scores; the review decisions below are documented interpretations of fixture context, not automated verdicts.

## Reproduce

From a clean checkout, using Python 3.10 or newer:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux alternative: source .venv/bin/activate
python -m pip install .
python -m unittest discover -s tests -v
python scripts/validate_extended.py
python scripts/validate_scenarios.py
python -m sentinel_soc_dashboard.cli --alerts sample_data/investigation_scenarios.json --skip-invalid --diagnostics input-quality.json
```

The last command deliberately opts into partial loading: this fixture contains invalid rows to exercise diagnostics. Normal runs fail on invalid input unless `--skip-invalid` is provided. Generated files are written to the current directory. Input paths are supplied explicitly, so the CLI can also run outside the source checkout.

Open `soc_report.html`, inspect `input-quality.json`, and compare with [scenario-results.json](scenario-results.json). The generator also writes [scenario-report.html](scenario-report.html). The larger fixture is generated deterministically rather than stored as a large committed file.

## 1. Suspicious privileged login

**Initial hypothesis:** possible account compromise. Five failed logins are followed by a critical successful-login alert from the same source against the same host. The synthetic context has no approved testing explanation.

**Tool output:** six alerts, priority 100, one case. This groups the supplied alerts; it does not independently prove malicious intent or discover a real intrusion.

**Review decision:** escalate for identity and endpoint investigation. Check sign-in origin, MFA, device history, session activity, and process telemetry. The exercise lacks those sources, so compromise remains unconfirmed. Containment needs corroboration and authorisation.

## 2. Approved maintenance

**Initial hypothesis:** hostile scanning. Three high-severity scanner findings also produce priority 100.

**Competing evidence:** the authored exercise ticket LAB-043 matches source 198.51.100.20, target maintenance-lab, and the 10:00-10:15 UTC window. All three fixture events occur within scope.

**Revised decision:** authorised activity within this exercise, with the reference recorded. The tool preserves the ticket hint but still gives the case a high score. Do not permanently suppress a source just because one scan was approved.

## 3. Unresolved administration activity

**Initial hypothesis:** encoded execution may represent malicious activity or legitimate administration.

**Available evidence:** two medium-severity alerts, priority 66. A maintenance explanation is uncorroborated; command contents, parent process, and a verified change ticket are absent.

**Review decision:** keep the case unresolved and request the missing evidence. Do not close it as benign because of a plausible story, and do not describe the score as proof of compromise.

## Input quality is part of the evidence

The scenario file has **15 rows**: **11 accepted alerts**, **1 exact duplicate removed**, and **3 rejected rows**. The rejected rows have a malformed timestamp, an unsupported severity, and a missing title. Row numbers and field-level reasons are recorded. Normalisation converts timestamps to UTC and supports equivalent timezone representations. Deduplication compares all normalised alert fields, including context; distinct timestamps and distinct analyst notes remain separate.

Missing source or host identity is allowed as incomplete context and remains separate during correlation. Non-empty source IPs must be valid IP addresses. Supported status values are `open` and `closed`; an adapter is needed for other platform schemas. JSON must be an array of objects. IOC fields must be lists of strings. No valid rows remaining causes a failure, even in partial mode. An empty array is an intentional empty input.

Deduplication occurs at file ingestion. Code that constructs `Alert` objects and calls `triage` directly is responsible for its own validation. This is a bounded educational schema, not a universal SIEM connector. HTML output escapes alert-derived text so it cannot become active markup.

## Validation evidence

Verified locally on Windows with Python 3.12.14 in a new virtual environment: a non-editable `pip install .`, 34 passing unit tests, and a CLI run outside the source tree with `PYTHONPATH` removed. The original eight-alert fixture still produces five cases. Both synthetic exercises pass 10 checks each. CI repeats the unit tests and exercises; its status is linked in the README.

This does not establish detection precision/recall, deployment readiness, or live Splunk/Sentinel execution. Fixed correlation windows, simplified ATT&CK mapping, and scores that over-prioritise benign activity remain known limits.

