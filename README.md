# Sentinel SOC Dashboard

Sentinel SOC Dashboard turns raw security alerts into prioritized analyst cases. It is a blue-team portfolio project designed to show alert triage, severity scoring, reporting, and SOC-style thinking.

## Why Employers Like This

Security teams do not only need alerts; they need prioritization. This project shows that you understand analyst workflow, escalation, evidence, and business-friendly reporting.

## Features

- Loads alert data from JSON.
- Groups related alerts into cases by source IP and host.
- Scores cases using severity, volume, and MITRE-style tactic diversity.
- Exports analyst-ready HTML and CSV reports.
- Includes sample data and tests.

## Quick Start

```bash
set PYTHONPATH=src
python -m sentinel_soc_dashboard.cli
python -m unittest discover -s tests -v
```

## Example Output

```text
Loaded 4 alerts.
Created 3 prioritized cases.
HTML report: soc_report.html
CSV report: soc_cases.csv
```

## Skills Demonstrated

- Python data processing
- Alert triage logic
- SOC workflow awareness
- Reporting
- Unit testing

## Responsible Use

This project is defensive. It analyzes alert data and does not perform scanning, exploitation, or intrusive actions.
