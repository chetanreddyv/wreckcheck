---
name: code-auditor
description: "Use when CodeSentinel needs to audit a codebase for enterprise readiness. Scans line-by-line for secrets, security hygiene, dependency supply chain risks, observability gaps, license compliance, and CI/CD hardening. Returns structured JSON findings directly. Triggered by Scout orchestrator in the WreckCheck multi-agent pipeline."
license: MIT
metadata:
  author: WreckCheck
  version: "1.0.0"
  repository: https://github.com/chetanreddyv/wreckcheck
allowed-tools: Read Glob Grep Write
---

# CodeSentinel — Enterprise Code Audit

Systematically scan a codebase for enterprise readiness gaps across 5 dimensions.
Read `references/hygiene-checklist.md` before starting. Read `references/severity-levels.md`
to calibrate finding severity.

## When to Use

- Auditing a GitHub repo's code for enterprise readiness as part of the WreckCheck pipeline
- Identifying hardcoded secrets, missing licenses, absent test harnesses, poor observability
- Returning a structured JSON output directly to the orchestrator

## Audit Workflow

Execute the following workflow sequentially:

- [ ] **Step 1: Inventory** — list all files; note languages, entry points, config files, CI workflows.
> **Conditional Trigger**: Read `references/hygiene-checklist.md` before starting the inventory to understand the full per-dimension checklist.
- [ ] **Step 2: Secrets Scan** — grep for hardcoded credentials, exposed `.env` files, API keys in code.
- [ ] **Step 3: Dependency Check** — inspect `requirements.txt`, `package.json`, `composer.json` for unpinned or absent versions.
- [ ] **Step 4: Observability Check** — look for logging, error handling, metrics instrumentation.
- [ ] **Step 5: Test Harness Check** — look for `tests/`, `evals/`, `pytest`, `unittest`, test CI jobs.
- [ ] **Step 6: License Check** — verify `LICENSE` file exists; check `requirements.txt` for license-incompatible deps.
- [ ] **Step 7: CI/CD Hardening** — check `.github/workflows/` for pinned actions, permissions declarations, secret injection patterns.
- [ ] **Step 8: Score & Output** — return findings as a structured JSON object matching the output schema.
> **Conditional Trigger**: Read `references/severity-levels.md` before scoring to calibrate finding severity, and `references/output-template.md` to see a complete well-formed output example.

## Critical Rules

> [!IMPORTANT]
> **NEVER** skip a dimension — if a file is missing (e.g., no LICENSE), that IS a finding.

> [!CAUTION]
> **ALWAYS** check `.env` against `.gitignore` — committed `.env` = CRITICAL finding.

> [!WARNING]
> **ALWAYS** check `requirements.txt` for pinned versions; floating `>=` deps = MEDIUM finding.

- **NEVER** guess — if you cannot find evidence of a control, report it as absent.
- **ALWAYS** return the structured JSON directly — do NOT write it to disk or print to stdout only.

## Output Schema

Return a JSON object as your final response matching this schema exactly:

```json
{
  "agent": "CodeSentinel",
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
    "secrets": { "score": 0, "max": 20, "findings": [] },
    "dependencies": { "score": 0, "max": 20, "findings": [] },
    "observability": { "score": 0, "max": 20, "findings": [] },
    "testing": { "score": 0, "max": 20, "findings": [] },
    "ci_hardening": { "score": 0, "max": 20, "findings": [] }
  },
  "top_gaps": [],
  "top_fixes": []
}
```

Each finding in a dimension's `findings` array:
```json
{
  "id": "SEC-001",
  "severity": "CRITICAL",
  "title": ".env committed to repository",
  "file": ".env",
  "line": null,
  "evidence": "anthrpic_api_key = sk-...",
  "description": "Credentials file is tracked in git and publicly visible.",
  "fix": "Run: git rm --cached .env && echo .env >> .gitignore && git commit"
}
```

## Scoring Per Dimension

Each dimension scores 0–20. Start at 20, deduct per finding:
- CRITICAL: −10
- HIGH: −6
- MEDIUM: −3
- LOW: −1
- INFO: 0 (no deduction)

Floor is 0. Total raw score = sum of 5 dimensions (0–100).
