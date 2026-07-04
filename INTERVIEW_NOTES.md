# Interview Notes

## 30-Second Explanation

Sentinel SOC Dashboard is a Python blue-team project that takes raw alert JSON, groups related alerts into cases, prioritizes them using severity, volume, and MITRE tactic diversity, then exports analyst-friendly reports.

## Why I Built It

I wanted to show that cybersecurity work is not just detecting bad activity. Analysts need to decide what matters first, explain why, and recommend the next action.

## Technical Decisions

- I used the Python standard library to keep the project easy to run.
- I grouped by source IP and host because that is a simple, explainable starting point for case creation.
- I made the scoring configurable because every SOC has different SLAs and risk appetite.
- I included HTML, CSV, JSON, and Markdown outputs because different teams consume reports differently.

## Tradeoffs

- Grouping by IP and host is simple, but real SOCs may also group by user, hostname, device ID, or time window.
- The MITRE mapping is lightweight and manually defined.
- The sample data is small so the project is easy to understand quickly.

## How I Would Improve It

- Add time-window grouping.
- Add IP reputation enrichment.
- Add Sigma rule support.
- Add analyst case status and notes.
- Add a Flask or FastAPI dashboard.
- Store cases in a database.

## What This Shows Employers

- Python programming
- SOC workflow understanding
- Alert triage logic
- Security reporting
- MITRE ATT&CK awareness
- Testing and documentation discipline
