# Case Study: Prioritizing SOC Alerts Into Analyst Cases

## Scenario

A small security team receives alerts from several tools: authentication monitoring, endpoint detection, and web telemetry. The team does not have enough time to investigate every alert in the order it arrives, so they need a lightweight way to group related activity and decide what should be handled first.

## Problem

Raw alerts are noisy. A single source IP may generate multiple events across the same host, and the most important signal is often the relationship between alerts rather than one alert alone.

This project answers:

- Which alerts appear related?
- Which case should an analyst open first?
- What MITRE ATT&CK context helps explain the behavior?
- What response SLA should be used?

## Approach

Sentinel SOC Dashboard loads alert JSON, normalizes each alert into an `Alert` object, groups related alerts by source IP and host, and calculates a priority score.

The scoring model uses:

- top severity
- number of related alerts
- tactic diversity
- configurable SLA mapping

The output is designed for analysts and managers:

- HTML for quick review
- CSV for spreadsheet workflows
- JSON for automation
- Markdown for tickets or case notes

## Example

An IP that generates repeated failed logins followed by a successful login receives high priority because the activity combines Credential Access and Initial Access. This is more urgent than a single low-severity scanner user-agent alert.

## Security Value

This project demonstrates practical SOC thinking:

- alert grouping
- prioritization
- escalation logic
- MITRE mapping
- evidence-based recommendations

## Limitations

This is a portfolio project, not a replacement for a SIEM. It does not ingest live telemetry, enrich IPs, deduplicate over long time windows, or connect to EDR systems.

## Production Improvements

- Add Sigma rule support.
- Add enrichment from threat intelligence sources.
- Add analyst disposition tracking.
- Store cases in SQLite or PostgreSQL.
- Add a small web dashboard.
- Add authentication if deployed.
