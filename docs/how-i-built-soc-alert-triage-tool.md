# How I Built a SOC Alert Triage Tool

When I started improving my cybersecurity portfolio, I wanted one project that felt close to real SOC work. A lot of beginner security projects stop at "detect something suspicious", but analysts also need to decide what matters first, explain the risk, and recommend an action.

That is why I built Sentinel SOC Dashboard.

## The Problem

Security teams often receive many alerts from different tools. Some are urgent, some are noise, and some only become important when viewed together.

For example:

- failed SSH logins may be medium priority by themselves
- a successful login after those failures is much more serious
- a suspicious command on an endpoint may require escalation
- a low-severity scanner user-agent may only need monitoring

The goal was to turn raw alert data into prioritized cases.

## The Design

The tool follows a simple pipeline:

1. Load alert JSON.
2. Normalize each alert into an `Alert` object.
3. Group related alerts by source IP and host.
4. Score each case using severity, volume, and tactic diversity.
5. Map tactics to MITRE ATT&CK context.
6. Export reports for analysts.

I intentionally kept the first version explainable. In an interview, I can walk through every line of the scoring model and explain the tradeoffs.

## What I Added For Professional Polish

To make the project more employer-ready, I added:

- unit tests
- GitHub Actions
- HTML, CSV, JSON, and Markdown output
- configurable scoring
- SLA mapping
- MITRE ATT&CK context
- architecture documentation
- a case study
- interview notes

Those extras matter because real security work is not just code. It is documentation, communication, and repeatable process.

## What I Learned

The most important lesson was that prioritization is a security skill. A tool that produces 100 alerts without context can make an analyst slower. A tool that groups evidence and explains the next action is much more useful.

## What I Would Build Next

If I continued developing this into a production-style project, I would add:

- time-window grouping
- IP reputation enrichment
- Sigma rule support
- analyst notes and case status
- SQLite or PostgreSQL storage
- a Flask or FastAPI dashboard

## Why This Project Represents Me

This project shows the kind of cybersecurity work I want to keep improving at: defensive tooling, clear investigation logic, and practical automation that helps people make better decisions.
