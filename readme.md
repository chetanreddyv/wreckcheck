# WreckCheck — Multi-Agent Enterprise Readiness Scorer

> Paste a GitHub repo URL. Get a 0–100 enterprise readiness score, dimensional sub-scores, top-3 gaps, and actionable fix commands. Powered by 4 cooperating AI agents with custom skills.

**Lane 3 Submission** · [ADLC Worksheet](ADLC.md) · [Model Selection Rationale](MODEL_SELECTION.md) · [Evals](evals/evals.json) · [MIT License](LICENSE)

---

## 🌟 Executive Summary

**WreckCheck** is an autonomous multi-agent system designed for AI startups to quickly self-assess their enterprise readiness for scenarios like enterprise sales or SOC-2 compliance. 
- **The Process**: WreckCheck fans out three parallel async agents to audit a repository across Security, Architecture, and Agent Safety. A synchronous Scorer agent then aggregates the JSON reports into a final Markdown report.
- **The Brains**: Powered uniformly by **Claude Haiku 4.5**. By injecting domain expertise through custom skills, WreckCheck achieves output quality comparable to larger models (like Sonnet) but at **10x lower cost** (~$0.02–0.04 per run) and low latency (~30-60s).
- **The Advantage**: Without skills, base models produce vague, qualitative prose. With skills, WreckCheck produces structured, severity-calibrated JSON with precise fix recommendations.
- **The Lifecycle**: Built following all 7 phases of the Agent Development Lifecycle (ADLC), including real-world iterations to fix output drift, handle timeouts, and introduce a dedicated agent safety auditor (`HarnessGuard`).

---

## 🚀 What It Does

WreckCheck autonomously audits any public GitHub repository (Python/JS/TS) across core dimensions:

| Dimension | Agent | Skill | What It Checks |
|-----------|-------|-------|----------------|
| **Security & Code Hygiene** | CodeSentinel | `code-auditor` | Secrets, dependencies, observability, testing, CI/CD |
| **Architecture & Spec Compliance** | ArchitectReview | `architecture-reviewer` | YAML frontmatter, directory structure, progressive disclosure, delegation patterns |
| **Agent Safety** | HarnessGuard | `harness-guard` | Prompt injection, unbounded loops, cost controls, observability gaps |
| **Scoring & Synthesis** | ReadinessScorer | `readiness-scorer` | Weighted 40/30/30 aggregation → 0–100 score + Markdown report |

*(Note: Private repos requiring auth, binary analysis, and runtime testing are out of scope.)*

---

## 🏗️ Architecture — Multi-Agent Delegation

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

**Key Design Decisions**:
1. **Parallel Fan-Out**: CodeSentinel, ArchitectReview, and HarnessGuard perform independent audits. Running them in parallel via `ThreadPoolExecutor` cuts wall-clock time by ~3x.
2. **Synchronous Delegation**: The ReadinessScorer must wait for all 3 JSON reports. Scout strictly blocks on `wait_for_async_tasks` before delegating to the scorer.
3. **Shared Workspace**: A local `./workspace/` directory serves as the inter-agent communication channel, passing structured JSON files between async workers and the scorer.
4. **Skill-as-System-Prompt**: Each agent loads its `SKILL.md` as its system prompt, immediately granting it domain expertise, output schemas, and scoring rules.

---

## 🧠 Model Selection & The "Skill Advantage"

All agents use **Claude Haiku 4.5**. This uniform selection is optimized for the cost/latency/quality tradeoffs of WreckCheck:

- **Cost-Efficiency**: A full pipeline run (5 agents analyzing ~15 files) costs **~$0.02–0.04**. Sonnet would cost ~10x more ($0.15–0.25).
- **Speed**: Haiku keeps the full pipeline latency under 60 seconds, whereas local models (e.g., Granite 8B) would take 10-15 minutes.
- **Reliability**: Cheaper models like GPT-4o-mini suffered from poor schema adherence (~20% failure rate) and tool-calling drift. Haiku's tool calling is production-grade.
- **The Skill Advantage**: WreckCheck proves that **skills compensate for model capability**. Haiku paired with a domain-specific `SKILL.md` matches the quality of Sonnet *without* skills, turning vague qualitative analysis into structured checklist-driven validation.

---

## 🛠️ Custom Skills System

WreckCheck utilizes 4 heavily structured skills, all conformant to **agentskills.io** specifications:

| Skill | Lines | References | What It Provides |
|-------|-------|------------|-----------------|
| `code-auditor` | 107 | `hygiene-checklist.md`, `severity-levels.md`, `output-template.md` | 5-dimension audit workflow + JSON output schema |
| `architecture-reviewer` | 176 | `spec-compliance.md`, `delegation-patterns.md` | 6-step review workflow + frontmatter/ADLC checks |
| `harness-guard` | 76 | `prompt-injection-checks.md`, `reliability-checks.md`, `cost-controls.md` | 4-dimension safety audit with conditional reference loading |
| `readiness-scorer` | 119 | `scoring-formula.md`, `override-policy.md` | Weighted scoring formula + override rules |

**Spec Conformance Check**:
- ✅ `name` matches directory perfectly
- ✅ `description` uses explicit trigger keywords
- ✅ Markdown bodies strictly under 500 lines
- ✅ Employs **progressive disclosure** by selectively loading `references/` (no scripts in references)

---

## 🔄 Agent Development Lifecycle (ADLC)

WreckCheck was built through all 7 phases of the ADLC:

1. **Scope** → Enterprise readiness scoring for AI startups.
2. **Design** → Orchestrator → parallel specialists → scorer pipeline.
3. **Build** → 5 agents, 4 skills, LangChain framework.
4. **Evaluate** → Proved structured JSON outputs beat vague prose via 3 test cases.
5. **Deploy** → CLI + Streamlit UI running on Python 3.11+.
6. **Observe** → Real-world runs exposed timeout hangs on large repos, output formatting drift, and parallel tracking bugs.
7. **Iterate** → Enforced explicit output schemas to fix drift, added rigid 600s timeouts/graceful fallbacks, and introduced the `HarnessGuard` skill after discovering base models missed prompt injection vectors.

---

## 📊 Evaluation Results (Skill vs. No-Skill)

See [`evals/evals.json`](evals/evals.json) for full test cases.

| Test Case | With Skill | Without Skill | Delta |
|-----------|-----------|---------------|-------|
| **Repo w/ committed `.env` + no tests** | Structured JSON: Flagged CRITICAL secret, scored 15/100 | Vague prose: "has some security concerns" | Actionable fixes vs. unhelpful prose |
| **Agent repo w/ prompt injection** | `HarnessGuard` caught unescaped user input interpolation as CRITICAL | Missed the injection vector completely | Safety-specific expertise injected via skills |
| **Clean repo with minor gaps** | Scored 82/100, explicitly noted observability gaps | "Seems mostly ready, B+ grade" | Granular sub-scores vs. binary good/bad |

---

## 💻 Setup & Run

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
*Output saved to `./workspace/readiness_report.md`.*

### Run (Web UI)
```bash
streamlit run app.py
```
*Open `http://localhost:8501`, paste a repo URL, click "Run WreckCheck".*

---

## 📁 Repo Structure

```
wreckcheck/
├── main.py                           # Entry point — Scout orchestrator
├── deepagents.py                     # Agent framework (LangChain + async)
├── tools.py                          # Shared tools (fetch_repo_files, read/write/search)
├── app.py                            # Streamlit web UI
├── agents/
│   ├── code_sentinel.py              # CodeSentinel agent
│   ├── arch_reviewer.py              # ArchitectReview agent
│   ├── harness_guard.py              # HarnessGuard agent
│   └── readiness_scorer.py           # ReadinessScorer agent
├── skills/                           # Custom skills
│   ├── code-auditor/
│   ├── architecture-reviewer/
│   ├── harness-guard/
│   └── readiness-scorer/
├── evals/
│   └── evals.json                    # 3 with-skill vs without-skill test cases
├── workspace/                        # Shared inter-agent workspace
├── ADLC.md                           # Agent Development Lifecycle worksheet
├── MODEL_SELECTION.md                # Model selection rationale
├── LICENSE                           # MIT
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 📜 License

MIT — see [LICENSE](LICENSE)