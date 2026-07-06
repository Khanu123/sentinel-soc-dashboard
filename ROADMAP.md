# Roadmap: Sentinel SOC Dashboard

This roadmap tracks realistic next improvements for the project. It is intentionally practical and focused on defensive security workflows.

## Planned Improvements

- [ ] Add time-window grouping for related alerts
- [x] Add analyst notes and false-positive handling guidance
- [ ] Add owner and case status fields
- [ ] Add a small Flask/FastAPI dashboard view
- [ ] Add IP reputation enrichment as an optional step
- [ ] Add Sigma-rule style detection metadata
- [ ] Add optional CSV input for exported SIEM alerts
- [ ] Add report filtering by severity, host, and tactic

## Maintenance Approach

- Keep sample data safe and synthetic.
- Add tests with each new feature.
- Keep reports readable for junior analyst and stakeholder review.
- Prefer clear defensive use cases over offensive automation.
- Make small, useful updates over time instead of cosmetic churn.
