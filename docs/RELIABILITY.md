# Reliability

## Service objectives

For every production service, define availability, latency, correctness, and freshness objectives with measurement windows and data sources.

## Operational requirements

- Startup, shutdown, retry, timeout, and idempotency behavior is explicit.
- Logs are structured and correlate requests or jobs without exposing sensitive data.
- Metrics describe user outcomes as well as resource health.
- Critical journeys have a reproducible local or test-environment probe.
- Alerts link to a runbook and fire on actionable symptoms.
- Incidents produce a durable harness improvement when a missing guardrail contributed.

## Runbooks

Add runbooks under `docs/runbooks/` and link them here. Each runbook should include symptoms, impact, diagnosis, mitigation, validation, and escalation.

