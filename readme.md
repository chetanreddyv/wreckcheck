# WreckCheck — Multi-Agent Enterprise Readiness Scorer

> Paste a GitHub repo URL. Get a 0–100 enterprise readiness score, dimensional sub-scores, top-3 gaps, and actionable fix commands. Powered by 4 cooperating AI agents with custom skills.

**Lane 3 Submission** · [ADLC Worksheet](ADLC.md) · [Model Selection Rationale](MODEL_SELECTION.md) · [Evals](evals/evals.json) · [MIT License](LICENSE)

---

## What It Does

WreckCheck is a multi-agent system that autonomously audits any public GitHub repository for enterprise readiness across three dimensions:

| Dimension | Agent | Skill | What It Checks |
|-----------|-------|-------|----------------|
| **Security & Code Hygiene** | CodeSentinel | `code-auditor` | Secrets, dependencies, observability, testing, CI/CD |
| **Architecture & Spec Compliance** | ArchitectReview | `architecture-reviewer` | YAML frontmatter, directory structure, progressive disclosure, delegation patterns |
| **Agent Safety** | HarnessGuard | `harness-guard` | Prompt injection, unbounded loops, cost controls, observability gaps |
| **Scoring & Synthesis** | ReadinessScorer | `readiness-scorer` | Weighted 40/30/30 aggregation → 0–100 score + Markdown report |

---

## Architecture — Multi-Agent Delegation

```
Scout (Orchestrator) ─── Claude Haiku 4.5
  │
  ├──[ASYNC]── CodeSentinel      ← loads skills/code-auditor/SKILL.md
  │              writes → workspace/code_sentinel.json
  │
  ├──[ASYNC]── ArchitectReview   ← loads skills/architecture-reviewer/SKILL.md
  │              writes → workspace/architect_review.json
  │
  ├──[ASYNC]── HarnessGuard      ← loads skills/harness-guard/SKILL.md
  │              writes → workspace/harness_guard.json
  │
  │  ⏳ wait_for_async_tasks (blocks until all 3 complete)
  │
  └──[SYNC]── ReadinessScorer    ← loads skills/readiness-scorer/SKILL.md
                reads all 3 JSONs → produces final Markdown report
```

**Delegation mechanism**: Scout uses `start_async_task_*` tools to fan out 3 parallel audits via `ThreadPoolExecutor`. Results auto-save to `./workspace/`. Scout blocks on `wait_for_async_tasks` until all complete, then synchronously delegates to ReadinessScorer. All handoffs are explicit, logged, and tool-mediated — not implicit.

**Shared workspace**: `./workspace/` directory serves as the inter-agent communication channel. Async agents write JSON reports; ReadinessScorer reads them.

---

## Custom Skills (4 skills, agentskills.io conformant)

Each skill is a valid `SKILL.md` directory with YAML frontmatter + `references/` for progressive disclosure:

| Skill | Directory | Lines | References | What It Provides |
|-------|-----------|-------|------------|-----------------|
| `code-auditor` | `skills/code-auditor/` | 107 | `hygiene-checklist.md`, `severity-levels.md`, `output-template.md` | 5-dimension audit workflow + JSON output schema + scoring rules |
| `architecture-reviewer` | `skills/architecture-reviewer/` | 176 | `spec-compliance.md`, `delegation-patterns.md` | 6-step review workflow + frontmatter validation rules + ADLC evidence checks |
| `harness-guard` | `skills/harness-guard/` | 76 | `prompt-injection-checks.md`, `reliability-checks.md`, `observability-checklist.md`, `cost-controls.md` | 4-dimension safety audit + conditional reference loading per step |
| `readiness-scorer` | `skills/readiness-scorer/` | 119 | `scoring-formula.md`, `override-policy.md` | Weighted scoring formula + override rules + report template |

**Spec conformance**:
- ✅ `name` field matches directory name (lowercase + hyphens)
- ✅ `description` covers what + when with trigger keywords
- ✅ Bodies under 500 lines; references load conditionally
- ✅ `references/` used correctly — no scripts in references, no docs in scripts

---

## Setup & Run

### Prerequisites
- Python 3.11+
- Anthropic API key

### Install

```bash
git clone https://github.com/chetanreddyv/wreckcheck.git
cd wreckcheck
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-...
```

### Run (CLI)

```bash
python main.py https://github.com/some-org/some-repo "Description of the project"
```

Output saved to `./workspace/readiness_report.md`.

### Run (Web UI)

```bash
streamlit run app.py
```

Open `http://localhost:8501`, paste a repo URL, click "Run WreckCheck".

---

## Eval Results — Skill vs. No-Skill

See [`evals/evals.json`](evals/evals.json) for full test cases.

| Test Case | With Skill | Without Skill |
|-----------|-----------|---------------|
| Repo with committed `.env` + no tests | Structured JSON: 12 findings, CRITICAL secret flagged, score 47/100 | Vague prose: "has some security concerns" |
| Agent repo with prompt injection | HarnessGuard: caught unescaped user input as CRITICAL | Base model: "looks functional, consider adding error handling" |
| Clean repo with minor gaps | ReadinessScorer: precise 82/100, weighted formula, tier classification | Base model: "seems mostly ready, B+ grade" |

**Conclusion**: Skills transform vague qualitative assessments into structured, severity-calibrated, actionable reports. Haiku + skill beats Sonnet without skill at 10x lower cost.

---

## Model Selection Summary

All agents: **Claude Haiku 4.5** — ~$0.02–0.04 per full pipeline run.

**Why not cheaper?** GPT-4o-mini fails on JSON schema adherence ~20% of runs. Local Granite 8B too slow (10–15 min).
**Why not stronger?** Skills inject domain expertise, compensating for model capability. Haiku + skill ≈ Sonnet quality at 10x lower cost.

Full analysis: [`MODEL_SELECTION.md`](MODEL_SELECTION.md)

---

## ADLC Summary

All 7 phases completed with 2 evaluate/observe loops evidenced:

1. **Scope** → Enterprise readiness scoring for AI startups
2. **Design** → Orchestrator → parallel specialists → scorer pipeline
3. **Build** → 5 agents, 4 skills, LangChain framework
4. **Evaluate** → 3 with-skill vs without-skill test cases
5. **Deploy** → CLI + Streamlit UI
6. **Observe** → Fixed timeout handling, output format drift, parallel reliability
7. **Iterate** → Added HarnessGuard skill, enforced output schemas, added wait mechanism

Full worksheet: [`ADLC.md`](ADLC.md)

---

## Repo Structure

```
wreckcheck/
├── main.py                           # Entry point — Scout orchestrator
├── deepagents.py                     # Agent framework (LangChain + async)
├── tools.py                          # Shared tools (fetch_repo_files, read/write/search)
├── app.py                            # Streamlit web UI
├── agents/
│   ├── code_sentinel.py              # CodeSentinel agent (loads code-auditor skill)
│   ├── arch_reviewer.py              # ArchitectReview agent
│   ├── harness_guard.py              # HarnessGuard agent
│   └── readiness_scorer.py           # ReadinessScorer agent
├── skills/
│   ├── code-auditor/
│   │   ├── SKILL.md                  # 5-dimension code audit
│   │   └── references/               # hygiene-checklist, severity-levels, output-template
│   ├── architecture-reviewer/
│   │   ├── SKILL.md                  # 6-step architecture review
│   │   └── references/               # spec-compliance, delegation-patterns
│   ├── harness-guard/
│   │   ├── SKILL.md                  # 4-dimension agent safety audit
│   │   └── references/               # prompt-injection, reliability, observability, cost
│   └── readiness-scorer/
│       ├── SKILL.md                  # Weighted scoring + report template
│       └── references/               # scoring-formula, override-policy
├── evals/
│   └── evals.json                    # 3 with-skill vs without-skill test cases
├── workspace/                        # Shared inter-agent workspace (gitignored outputs)
├── ADLC.md                           # Agent Development Lifecycle worksheet (7 phases)
├── MODEL_SELECTION.md                # Model selection rationale with cost/latency/quality
├── LICENSE                           # MIT
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## License

MIT — see [LICENSE](LICENSE)