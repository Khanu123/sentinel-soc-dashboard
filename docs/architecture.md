# Architecture

```mermaid
flowchart LR
    A[Alert JSON] --> B[Load Alerts]
    B --> C[Normalize Alert Objects]
    C --> D[Group by Source IP and Host]
    D --> E[Calculate Priority Score]
    E --> F[Map MITRE Context]
    F --> G[Export Reports]
    G --> H[HTML]
    G --> I[CSV]
    G --> J[JSON]
    G --> K[Markdown]
```

## Components

| Component | Purpose |
| --- | --- |
| `cli.py` | Command-line entry point and report options |
| `core.py` | Parsing, triage, scoring, MITRE mapping, and report writing |
| `sample_data/alerts.json` | Safe demo alert data |
| `config.example.json` | Adjustable scoring and SLA configuration |
| `tests/` | Unit tests for prioritization and reporting context |

## Scoring Model

```text
priority = top severity score + volume score + tactic diversity score
```

The final score is capped at `100`.

This intentionally simple model is explainable in an interview and easy to tune for a team.
