# ADLC Worksheet — WreckCheck

> Agent Development Lifecycle worksheet covering all 7 phases.
> Each phase includes what was done, key decisions, and evidence.

---

## Phase 1: Scope

**Problem Statement**: AI startups shipping agent-based products cannot quickly self-assess enterprise readiness. Manual audits are slow, expensive, and inconsistent. There is no automated multi-agent system that scans a repo and produces a structured, scored readiness report.

**Target User**: AI founders and engineering leads preparing for enterprise sales or SOC-2 readiness.

**Success Criteria**:
- Given any public GitHub repo URL, produce a 0–100 enterprise readiness score in under 5 minutes
- Surface top-3 gaps and top-3 actionable fixes
- Sub-scores across security, architecture, and agent safety dimensions

**Scope Boundaries**:
- IN: Public GitHub repos, Python/JS/TS codebases, agent skill validation
- OUT: Private repos requiring auth, binary analysis, runtime testing

---

## Phase 2: Design

**Architecture Decision**: Orchestrator → Parallel Specialists → Scorer pipeline.

```
Scout (Orchestrator, Claude Haiku 4.5)
  ├── [ASYNC] CodeSentinel    ← code-auditor skill
  ├── [ASYNC] ArchitectReview ← architecture-reviewer skill
  ├── [ASYNC] HarnessGuard    ← harness-guard skill
  └── [SYNC]  ReadinessScorer ← readiness-scorer skill (runs after all 3 complete)
```

**Key Design Decisions**:
1. **Parallel fan-out** for CodeSentinel / ArchitectReview / HarnessGuard — independent audits with no data dependency on each other, so parallelism cuts wall-clock time by ~3x.
2. **Sync delegation** for ReadinessScorer — must wait for all 3 JSON reports before scoring. Enforced by `wait_for_async_tasks` tool.
3. **Shared workspace** (`./workspace/`) for inter-agent data passing — JSON files written by async workers, read by scorer.
4. **Skill-as-system-prompt** pattern — each agent loads its `SKILL.md` as its system prompt, giving it domain expertise + output schema + scoring rules.

**Agent Boundaries** (non-overlapping):
| Agent | Responsibility | Does NOT do |
|-------|---------------|-------------|
| Scout | Fetch repo, dispatch, collect | Any auditing or scoring |
| CodeSentinel | Code hygiene (secrets, deps, tests, CI) | Architecture or agent safety |
| ArchitectReview | Spec compliance, structure, delegation | Code scanning or scoring |
| HarnessGuard | Agent safety (injection, loops, cost) | Code hygiene or spec validation |
| ReadinessScorer | Weighted aggregation + report | Any auditing |

---

## Phase 3: Build

**Implementation Log**:

| Component | What was built | Files |
|-----------|---------------|-------|
| Orchestrator | Scout agent with async fan-out + sync scorer delegation | `main.py` |
| Agent framework | LangChain-based DeepAgent with async task support | `deepagents.py` |
| Tools | `fetch_repo_files`, `read_file`, `write_file`, `search_files` | `tools.py` |
| Code Auditor Skill | 5-dimension audit (secrets, deps, observability, testing, CI) | `skills/code-auditor/` |
| Architecture Reviewer Skill | 4-dimension review (frontmatter, structure, disclosure, architecture) | `skills/architecture-reviewer/` |
| Harness Guard Skill | 4-dimension safety audit (security, reliability, observability, cost) | `skills/harness-guard/` |
| Readiness Scorer Skill | Weighted aggregation formula + Markdown report template | `skills/readiness-scorer/` |
| Agent wiring | Individual agent configs loading skills as system prompts | `agents/*.py` |
| UI | Streamlit app with live orchestration visualization | `app.py` |

**Skills Conformance**:
- All 4 skills have valid YAML frontmatter with `name`, `description`, `license`
- All use `references/` for conditional loading (progressive disclosure)
- `name` field matches directory name in all cases
- Bodies are under 500 lines / 5000 tokens

---

## Phase 4: Evaluate

**Evaluation Method**: With-skill vs. without-skill comparison on 3 test repos.

| Test Case | With Skill | Without Skill | Delta |
|-----------|-----------|---------------|-------|
| Repo with .env committed + no tests | Correctly flagged CRITICAL secret + missing test harness, scored 15/100 | Generic "looks risky" — no structured findings, no score | Structured JSON with actionable fixes vs. vague prose |
| Clean repo with CI + pinned deps | Correctly scored 82/100, noted minor observability gaps | "Seems fine" — no dimensional breakdown | Granular sub-scores vs. binary good/bad |
| Agent repo with prompt injection | HarnessGuard caught unescaped user input interpolation as CRITICAL | Completely missed prompt injection vector | Safety-specific expertise the base model lacks |

**Key Finding**: Without skills, the base model produces qualitative opinions. With skills, it produces structured JSON with severity-calibrated findings, dimensional scores, and specific fix recommendations.

See `evals/evals.json` for raw test case definitions.

---

## Phase 5: Deploy

**Deployment Configuration**:
- **Runtime**: Python 3.11+, LangChain + Anthropic SDK
- **Model**: Claude Haiku 4.5 for all agents (cost-optimized, see `MODEL_SELECTION.md`)
- **Entry points**:
  - CLI: `python main.py <repo_url> [description]`
  - UI: `streamlit run app.py`
- **Environment**: Single `.env` file with `ANTHROPIC_API_KEY`
- **Dependencies**: Pinned in `requirements.txt`

**Deployment Checklist**:
- [x] Public GitHub repo with README
- [x] MIT LICENSE file in repo root
- [x] `.env.example` provided (no real keys committed)
- [x] `.gitignore` excludes `.env` and workspace outputs
- [x] `requirements.txt` present

---

## Phase 6: Observe

**Observations from Live Runs**:

1. **Timeout handling**: Initial runs had agents hang on large repos. Added 600s timeout per agent and 300s max_execution_time on AgentExecutor. Agents now return graceful error JSON on timeout.
2. **Output format drift**: Without explicit output schemas in SKILL.md, agents would sometimes return prose instead of JSON. Adding strict output schema + "ALWAYS return JSON directly" rules in Critical Rules section fixed this.
3. **Parallel reliability**: ThreadPoolExecutor with 10 workers handles 3 concurrent agents without issues. Task ID tracking in `_async_tasks` dict allows correct result routing.
4. **Token efficiency**: Haiku 4.5 handles all agent tasks within 4096 max_tokens. No truncation observed on repos up to 15 files.

---

## Phase 7: Iterate

**Iteration Log** (changes driven by evaluate/observe feedback):

| Iteration | Trigger | Change Made |
|-----------|---------|-------------|
| 1 | Observe: agents returning prose instead of JSON | Added explicit output schemas and "ALWAYS return JSON" rules to all SKILL.md files |
| 2 | Observe: agent hangs on large repos | Added 600s timeout + graceful error JSON fallback in `deepagents.py` |
| 3 | Evaluate: base model misses prompt injection | Created `harness-guard` skill with specific prompt injection detection patterns |
| 4 | Observe: ReadinessScorer running before inputs ready | Enforced `wait_for_async_tasks` tool — Scout must wait for all 3 async results |
| 5 | Evaluate: no dimensional scoring in baseline | Added per-dimension 0–20 scoring with severity-based deduction tables to all audit skills |

**Evaluate → Observe Loop Evidence**:
- **Loop 1**: Evaluated without skills → observed vague outputs → iterated by adding structured output schemas → re-evaluated → confirmed structured JSON output
- **Loop 2**: Evaluated on agent repo → observed missed safety issues → iterated by creating HarnessGuard skill → re-evaluated → confirmed prompt injection detection

---

*Last updated: 2026-06-27*
