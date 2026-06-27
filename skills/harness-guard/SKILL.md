---
name: harness-guard
description: Audits AI agent implementations for production readiness, including prompt injection exposure, retry loops, observability gaps, and cost-control failures.
license: MIT
allowed-tools: Read Glob Grep Write
---

# HarnessGuard — Production Readiness Audit

Audits AI agent implementations for four key dimensions of production readiness: security, reliability, observability, and cost controls. Returns a structured JSON payload directly.

## Audit Workflow

Execute the following workflow sequentially:

- [ ] **Step 1: Security Scan** — check for prompt injection exposure, especially user or tool output being interpolated directly into system prompts.
> **Conditional Trigger**: Read `references/prompt-injection-checks.md` during Step 1 for injection patterns.
- [ ] **Step 2: Reliability Check** — check for unbounded retries, recursive delegation, or missing depth counters that create loops.
> **Conditional Trigger**: Read `references/reliability-checks.md` during Step 2.
- [ ] **Step 3: Observability Check** — check for missing traces, no per-tool logs, no per-run token accounting, and no eval hooks.
> **Conditional Trigger**: Read `references/observability-checklist.md` during Step 3.
- [ ] **Step 4: Cost Check** — check for cost blowups from oversized tool outputs, expensive default models, and missing token budgets or truncation rules.
> **Conditional Trigger**: Read `references/cost-controls.md` during Step 4.
- [ ] **Step 5: Output JSON** — format and return the structured JSON object matching the schema below.

## Critical Rules

> [!CAUTION]
> Record a **CRITICAL** finding if unbounded retry loops or recursive delegations are identified.

> [!WARNING]
> Record a **HIGH** finding if user input is interpolated into a system prompt without explicit escaping or boundary fencing.

- **NEVER** guess — if you cannot find evidence of an observability trace or token budget, report it as absent.
- **ALWAYS** return the JSON structure directly to the caller.

## Output Schema

Return a JSON object as your final response matching this schema exactly:

```json
{
  "agent": "HarnessGuard",
  "version": "1.0.0",
  "target": "<repo_url_or_path>",
  "timestamp": "<ISO8601>",
  "summary": {
    "total_findings": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  },
  "dimensions": {
    "security": { "score": 0, "max": 20, "findings": [] },
    "reliability": { "score": 0, "max": 20, "findings": [] },
    "observability": { "score": 0, "max": 20, "findings": [] },
    "cost": { "score": 0, "max": 20, "findings": [] }
  },
  "top_gaps": [],
  "top_fixes": []
}
```

## Scoring Rules

Each dimension starts at 20 points. Deduct per finding:
- CRITICAL: −10
- HIGH: −6
- MEDIUM: −3
- LOW: −1
- INFO: 0

Floor is 0 per dimension. Total raw score = sum of 4 dimensions (0–80).
