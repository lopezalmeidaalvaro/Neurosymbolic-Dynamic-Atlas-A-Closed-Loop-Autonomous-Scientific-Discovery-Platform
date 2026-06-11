# Credibility Update Report

**Sprint**: F - Credibility & Academic Outreach Hardening  
**Scope**: Public landing pages and landing-facing metrics/API examples  
**Date**: 2026-05-31

## Summary

AST-OS landing content was revised from a commercial/startup framing to a research/demo framing suitable for CubeSat teams, university laboratories, aerospace professors, and spacecraft thermal engineering researchers.

## Changes Made

### Landing Page Metrics

Removed non-verifiable public metrics:

- Active Satellite Operators
- Active Space Node Keys
- Simulations & EKF Diagnoses as live usage counts
- user/registration/key/growth-style counters

Replaced with technical capability cards:

- 6 Thermal Nodes: Physics-based spacecraft thermal network
- FastAPI REST API: Interactive simulation endpoints
- Real-Time Digital Twin: Dynamic transient thermal simulations

### Hero Messaging

Replaced marketing-heavy copy with:

- Title: Autonomous Spacecraft Thermal Digital Twin
- Subtitle: Physics-informed spacecraft thermal simulation platform for CubeSat and SmallSat mission analysis.
- Supporting text: Interactive thermal modelling, transient orbital simulations, and anomaly analysis through a web interface and REST API.

Removed unsupported language such as mission-ready, production operators, paid subscription scale, and flight-proven-style framing.

### Pricing / Access

Replaced paid subscription cards with:

- Academic Preview: Free
- Research Collaboration: Contact Us
- Enterprise: Coming Soon

The page no longer implies current production customers, paid traction, real operator acquisition, or deployed commercial plans.

### API Quickstart

Replaced hardcoded `http://localhost:8000` examples with configurable `API_BASE_URL`.

Examples now use:

```bash
API_BASE_URL="https://your-api-url"
ASTOS_API_KEY="replace-with-your-api-key"
```

### Demo Explanation

Added a "How the Demo Works" section explaining:

1. Adjust spacecraft thermal parameters.
2. Run the simulation.
3. Observe temperature evolution.
4. Compare different thermal configurations.

### Public Metrics Endpoint

Changed `/v1/public/metrics` from user/API-key/usage counters to static capability descriptors:

- `thermal_nodes`
- `api`
- `simulation_mode`

This prevents a landing integration from presenting local database rows as real adoption metrics.

## Files Updated

- `backend/landing.html`
- `satellite/landing/index.html`
- `backend/thermal_api.py`
- `landing_page_claims_audit.md`
- `credibility_update_report.md`

## Verification Performed

- Searched landing pages for prohibited claims and hardcoded `localhost:8000`.
- Confirmed quickstart snippets use `API_BASE_URL`.
- Confirmed landing metric cards use technical product metrics rather than user/growth metrics.

## Residual Notes

Some repository documents outside the landing page still contain older marketing or qualification claims. They were not modified in this sprint because the requested scope was landing-page credibility and outreach hardening.

