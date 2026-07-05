# Sentinel SOC Dashboard

[![tests](https://github.com/Khanu123/sentinel-soc-dashboard/actions/workflows/tests.yml/badge.svg)](https://github.com/Khanu123/sentinel-soc-dashboard/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-portfolio_project-brightgreen)

Sentinel SOC Dashboard turns raw security alerts into prioritized analyst cases. It is a blue-team portfolio project designed to show alert triage, severity scoring, reporting, and SOC-style thinking.

## Why Employers Like This

Security teams do not only need alerts; they need prioritization. This project shows that you understand analyst workflow, escalation, evidence, and business-friendly reporting.

## Features

- Loads alert data from JSON.
- Groups related alerts into cases by source IP and host.
- Scores cases using severity, volume, tactic diversity, and configurable SLA logic.
- Maps tactics to MITRE ATT&CK context.
- Exports analyst-ready HTML, CSV, JSON, and Markdown reports.
- Includes sample data and tests.

## Quick Start

```bash
set PYTHONPATH=src
python -m sentinel_soc_dashboard.cli
python -m unittest discover -s tests -v
```

Use custom scoring:

```bash
python -m sentinel_soc_dashboard.cli --config config.example.json
```

## Example Output

```text
Loaded 4 alerts.
Created 3 prioritized cases.
HTML report: soc_report.html
CSV report: soc_cases.csv
JSON report: soc_cases.json
Markdown report: soc_report.md
```

## Documentation

- [Case Study](docs/case-study.md)
- [Architecture](docs/architecture.md)
- [Blog Writeup](docs/how-i-built-soc-alert-triage-tool.md)
- [Interview Notes](INTERVIEW_NOTES.md)
- [Example Report](docs/examples/example_soc_report.md)

## Skills Demonstrated

- Python data processing
- Alert triage logic
- SOC workflow awareness
- Reporting
- Unit testing

## Responsible Use

This project is defensive. It analyzes alert data and does not perform scanning, exploitation, or intrusive actions.
