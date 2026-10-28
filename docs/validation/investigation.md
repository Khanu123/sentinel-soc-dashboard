# Investigation exercise: a high-priority scanner case

This is a newly constructed synthetic lab exercise, not a workplace incident or a claim that the portfolio owner personally handled a real compromise. The context below is deliberately authored fixture data. Results come from running `scripts/validate_extended.py` against the implementation in this repository.

## Initial hypothesis

Six high-severity reconnaissance alerts arrive from 198.51.100.20 against portal-lab, between 12:00 and 12:05 UTC on 1 October 2026. The tool assigns priority 100 and recommends escalation. The initial hypothesis is hostile reconnaissance requiring investigation. The score alone does not confirm that hypothesis.

## Evidence and competing explanation

The fixture includes exercise change ticket LAB-042, authorising that exact source and target from 12:00 to 12:15 UTC. Its reference is preserved in `false_positive_handling` in the generated results. A competing explanation is approved security testing.

| Check | Exercise evidence | Meaning |
| --- | --- | --- |
| Source | 198.51.100.20 matches LAB-042 | Supports approved scanner explanation |
| Target | portal-lab matches the exercise scope | No out-of-scope target in this fixture |
| Time | 12:00-12:05 falls within 12:00-12:15 | Supports the approved activity explanation |
| Corroboration | No real ticket system, endpoint telemetry, or network capture | Limits the conclusion to the constructed exercise |

## Revised conclusion

Given the authored ticket context, classify this exercise case as authorised activity after checking source, scope, and timing. Record the ticket reference and review decision. Do not automatically allowlist every event from the source: a compromised scanner or activity outside the approved interval would require investigation.

The program has **not** automatically cleared the case. It still assigns priority 100. This is an observed false-positive prioritisation limitation, and manual review is required. A possible future improvement is verified, expiring maintenance context; no such integration is claimed here.

## Control case

A separate six-event sequence at 14:00-14:05 from 203.0.113.44 against identity-lab contains five synthetic failed logins followed by a critical successful-login alert. It also scores 100. Unlike the scanner, it has no approved-testing context in the fixture. The appropriate exercise decision is to escalate for identity and endpoint review, not to conclude compromise solely from the score. Isolation or account changes would require corroboration and an authorised response process.

## Engineering finding and change

The background fixture contains 50 source/host identities, each with two alerts per day across ten days. Unbounded grouping combines each identity's ten daily sessions into one case. The revised default separates activity into fixed 30-minute windows anchored to the first event. The entire fixture produces 504 cases with bounded grouping versus 54 with the unbounded comparison mode. Both modes apply the new safeguard that incomplete identities remain separate; the comparison isolates time-window behaviour rather than reproducing the entire old implementation.

This increase in case count is not proof of better detection. It shows that the defined daily sessions are no longer merged. Fixed windows can split a long-running incident, and sophisticated correlation remains future work.

## Reproduce and review

Run from the repository root:

```bash
python scripts/validate_extended.py
```

The script writes `sample_data/extended_alerts.json` and [extended-results.json](extended-results.json). A fixed seed makes input order reproducible; the report records the fixture SHA-256. It checks alert preservation, separate daily sessions, incomplete identities, retained scanner context, and the control sequence. Separate unit tests cover window boundaries, shuffled input, timezone offsets, invalid windows, and input immutability.

Local validation: 1,014 synthetic alerts, 10/10 exercise checks, and 34/34 unit tests. These are regression results, not precision/recall, production throughput, or Splunk/Sentinel execution evidence. File ingestion now validates rows and removes exact normalised duplicates. See [the input-quality walkthrough](walkthrough.md) for diagnostics and contrasting scenarios; richer platform telemetry remains future work.
