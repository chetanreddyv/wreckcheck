# Output Template

A complete, well-formed example of `/workspace/code_audit.json`.
Use this as your target format when writing output.

```json
{
  "agent": "CodeSentinel",
  "version": "1.0.0",
  "target": "https://github.com/example/myrepo",
  "timestamp": "2026-06-27T12:00:00Z",
  "summary": {
    "total_findings": 5,
    "critical": 1,
    "high": 2,
    "medium": 1,
    "low": 1,
    "info": 0
  },
  "dimensions": {
    "secrets": {
      "score": 10,
      "max": 20,
      "findings": [
        {
          "id": "SEC-001",
          "severity": "CRITICAL",
          "title": ".env committed to repository",
          "file": ".env",
          "line": null,
          "evidence": "anthropic_api_key = sk-ant-...",
          "description": "The .env file is tracked in git and publicly visible. Any API keys stored here are exposed.",
          "fix": "git rm --cached .env && echo .env >> .gitignore && git commit -m \"fix: remove .env from tracking\""
        }
      ]
    },
    "dependencies": {
      "score": 14,
      "max": 20,
      "findings": [
        {
          "id": "DEP-001",
          "severity": "HIGH",
          "title": "No requirements.txt or dependency file found",
          "file": null,
          "line": null,
          "evidence": "No requirements.txt, setup.py, pyproject.toml, or package.json found in root.",
          "description": "Without a pinned dependency file, reproducible installs are impossible and supply chain risk is uncontrolled.",
          "fix": "Run: pip freeze > requirements.txt and commit it."
        }
      ]
    },
    "observability": {
      "score": 17,
      "max": 20,
      "findings": [
        {
          "id": "OBS-001",
          "severity": "MEDIUM",
          "title": "No structured logging — bare print() used for errors",
          "file": "agents/code_sentinel.py",
          "line": 14,
          "evidence": "print(f\"Error: {e}\")",
          "description": "print() does not support log levels, structured output, or integration with monitoring tools.",
          "fix": "Replace with: import logging; logger = logging.getLogger(__name__); logger.error(f\"Error: {e}\")"
        }
      ]
    },
    "testing": {
      "score": 14,
      "max": 20,
      "findings": [
        {
          "id": "TEST-001",
          "severity": "HIGH",
          "title": "No eval harness defined for AI agent project",
          "file": null,
          "line": null,
          "evidence": "No evals/ directory found. README references evals but no evals/evals.json exists.",
          "description": "AI agent projects without an eval harness cannot demonstrate behavioural correctness under controlled conditions.",
          "fix": "Create evals/evals.json with at least 3 test cases and a run_evals.py runner."
        }
      ]
    },
    "ci_hardening": {
      "score": 19,
      "max": 20,
      "findings": [
        {
          "id": "CI-001",
          "severity": "LOW",
          "title": "SECURITY.md absent",
          "file": null,
          "line": null,
          "evidence": "No SECURITY.md found in repository root or .github/.",
          "description": "Enterprise adopters expect a published vulnerability disclosure policy.",
          "fix": "Create SECURITY.md with contact email and SLA: Critical 7 days, High 30 days."
        }
      ]
    }
  },
  "top_gaps": [
    "Committed .env file with API key (CRITICAL — immediate exposure risk)",
    "No eval harness defined (HIGH — cannot verify agent correctness)",
    "No requirements.txt (HIGH — supply chain uncontrolled)"
  ],
  "top_fixes": [
    "git rm --cached .env && echo .env >> .gitignore",
    "Create evals/evals.json with 3+ test cases and run_evals.py",
    "pip freeze > requirements.txt and commit"
  ]
}
```

## Validation Rules

Before writing the file, verify:
1. All 5 dimension keys are present (`secrets`, `dependencies`, `observability`, `testing`, `ci_hardening`)
2. Each dimension has `score`, `max`, and `findings` keys
3. `summary.total_findings` equals the sum of all findings across all dimensions
4. Every finding has: `id`, `severity`, `title`, `file`, `line`, `evidence`, `description`, `fix`
5. `top_gaps` has 1–5 items (the most critical gaps, in severity order)
6. `top_fixes` has 1–5 items (actionable one-liners or short commands)
7. Output is valid JSON (no trailing commas, no comments inside the JSON block)
