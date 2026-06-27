# WreckCheck Agent Landscape

Here is a breakdown of what each agent in the system currently does, their inputs/outputs, and an analysis of gaps or redundancies to help us plan the next steps.

---

## 1. Scout (Orchestrator)
**Role**: The coordinator of the system.
- **Input**: A GitHub repository URL and a brief product description.
- **Actions**:
  1. Clones/fetches the key files from the repository (`README.md`, `SKILL.md`, `main.py`, etc.) and stores them in memory/workspace.
  2. Spawns `CodeSentinel` and `ArchitectReview` in parallel, handing them the codebase text.
  3. Waits for their JSON reports.
  4. Passes both JSON reports directly to `ReadinessScorer`.
- **Output**: Returns the final enterprise readiness Markdown report back to the user.

## 2. CodeSentinel (Code Auditor)
**Role**: The code-level security and hygiene specialist.
- **Input**: Raw repository files (`repo_contents.txt`).
- **Actions**: Scans the codebase line-by-line across 5 dimensions:
  1. **Secrets**: Uncovered API keys, `.env` files.
  2. **Dependencies**: Floating/unpinned package versions.
  3. **Observability**: Missing logs/metrics.
  4. **Testing**: Missing `pytest`/`evals`.
  5. **CI/CD Hardening**: Unpinned actions, missing branch protection.
- **Output**: A highly structured JSON object scoring these 5 dimensions (0-20 each) with specific CRITICAL/HIGH/MEDIUM findings.

## 3. ArchitectReview (Architecture Reviewer)
**Role**: The system design and spec-compliance specialist.
- **Input**: Raw repository files (`repo_contents.txt`).
- **Actions**: Evaluates the `SKILL.md` and multi-agent setup across 4 dimensions:
  1. **Frontmatter**: YAML spec compliance, naming rules.
  2. **Structure**: Folder organization (`scripts/`, `assets/`, `references/`).
  3. **Disclosure**: Ensuring references are loaded conditionally (Progressive Disclosure).
  4. **Architecture**: Preventing agent circular delegation, checking model rationale, and ADLC evidence.
- **Output**: A structured JSON object scoring these 4 dimensions (0-20 each) with specific findings.

## 4. HarnessGuard (Agent Safety Guard)
**Role**: The AI-specific security and production readiness validator.
- **Input**: Raw repository files (`repo_contents.txt`).
- **Actions**: Evaluates the codebase and agent setup across 4 dimensions:
  1. **Security**: Prompt injection exposure, unsafe tool boundaries.
  2. **Reliability**: Unbounded loops, missing max_steps, recursive delegation.
  3. **Observability**: Missing traces, no token accounting, lack of eval hooks.
  4. **Cost**: Oversized tool outputs, missing token budgets, expensive default models.
- **Output**: A structured JSON object scoring these 4 dimensions (0-20 each) with specific findings natively returned to the orchestrator.

## 5. ReadinessScorer (Scorer)
**Role**: The synthesizer and report generator.
- **Input**: Three JSON objects (from CodeSentinel, ArchitectReview, and HarnessGuard).
- **Actions**: *Intended* to aggregate the scores, apply global policies or weightings, and format the final executive summary. 
- **Output**: A final Markdown report containing the overall Enterprise Readiness score and top prioritized gaps.

---

## Gap Analysis: Missing, Redundant, and Recommended Additions

> [!WARNING]
> **CRITICAL GAP:** `skills/readiness-scorer/SKILL.md` is currently completely empty! 
> The Python agent is wired up, but the actual prompt and instructions for how to parse the JSON and calculate the final score are missing.

### 1. What's Missing?
- **ReadinessScorer SKILL.md**: We need to write the instructions on how it aggregates the 100-point score from CodeSentinel, the 80-point score from ArchitectReview, and the 80-point score from HarnessGuard. How are they weighted? What does the final Markdown template look like?
- **File Fetching Logic Limitation**: Scout currently only looks for hardcoded files (`main.py`, `app.py`, `SKILL.md`). If a repo uses `agent.py` or `src/index.ts`, Scout will miss it. We should eventually give Scout a dynamic directory-listing tool instead of a static list.

### 2. Redundancies?
- Currently, there is very little redundancy. CodeSentinel strictly handles code-level grep checks, while ArchitectReview strictly handles YAML, folder structure, and delegation logic. 

### 3. What to add next?
1. **Flesh out `ReadinessScorer`**: Create its `SKILL.md`, define the final scoring formula, and give it a Markdown template (`assets/report-template.md`).
2. **Reference Files**: We reference files like `hygiene-checklist.md` in `code-auditor`, but we need to ensure those markdown files actually exist and contain the detailed rules (we just added the ones for `harness-guard`).
