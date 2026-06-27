---
name: readiness-scorer
description: >
  Aggregates verdicts from CodeSentinel and ArchitectReview into a 0–100
  enterprise readiness score with sub-scores and top-3 gaps. Use when asked
  to score overall readiness, produce a final readiness report, or combine
  audit results into a single actionable verdict. Always runs last in the
  pipeline — after code audit and architecture review are complete.
license: MIT
metadata:
  author: Wreckcheck
  version: "1.0.0"
allowed-tools: Read
---

# ReadinessScorer

Aggregate sub-agent outputs into a final 0–100 readiness score. Always wait for **BOTH** CodeSentinel and ArchitectReview outputs before scoring.

---

## Inputs Required

Before scoring, confirm all three of the following are available in the context:
- [ ] **CodeSentinel output** — contains PASS / WARN / FAIL verdict + findings list.
- [ ] **ArchitectReview output** — contains PASS / WARN / FAIL verdict + findings list.
- [ ] **HarnessGuard output** — contains PASS / WARN / FAIL verdict + findings list.

> [!IMPORTANT]
> If any input is missing or incomplete, immediately return:
> `"Scoring blocked — awaiting [missing agent] output."`
> Do not attempt to calculate a score with partial inputs.

---

## Scoring Formula Overview

Readiness scoring starts at a base baseline of **100 points** for each sub-category. Points are deducted based on the severity and source of each finding.

### Sub-Scores
Calculate three sub-scores separately before combining:
1. **Security Score (from CodeSentinel)**: Starts at 100. Deduct points for CodeSentinel findings. Weight: **40%**.
2. **Architecture Score (from ArchitectReview)**: Starts at 100. Deduct points for ArchitectReview findings. Weight: **30%**.
3. **Safety Score (from HarnessGuard)**: Starts at 100. Deduct points for HarnessGuard findings. Weight: **30%**.

### Final Score Formula
$$\text{Final Score} = (\text{Security Score} \times 0.40) + (\text{Architecture Score} \times 0.30) + (\text{Safety Score} \times 0.30)$$

> **Conditional Trigger**: Read `skills/readiness-scorer/references/scoring-formula.md` when executing point deductions, verifying deduction point tables per severity level, resolving scoring disputes, or mapping the final numeric score to its Readiness Tier label.

---

## Override and Disable Rules Overview

Certain project contexts or environment settings waive or downgrade specific audit checks. When the Scout agent provides context flags (e.g., `internal-only`, `no-external-deps`, `eval-harness-planned`, or `observability-waived`), scoring deductions must be adjusted accordingly.

> **Conditional Trigger**: Read `skills/readiness-scorer/references/override-policy.md` when Scout context flags are present in the pipeline or if a scoring dispute arises regarding check applicability and point overrides.

---

## Critical Scoring Gotchas

Apply the following critical constraints during score evaluation:

- **PASS does not mean 100**: A PASS verdict from CodeSentinel does not guarantee a high Security Score. PASS simply indicates zero CRITICAL findings; LOW and MEDIUM findings still deduct points.
- **Single FAIL Cap**: If CodeSentinel returns FAIL, the Final Score is strictly capped at **49** regardless of how well the Architecture Score performs.
- **Double FAIL Floor**: If both agents return FAIL, output the report- **ALWAYS** return the JSON structure directly to the caller — do NOT write it to disk.
- **Precision & Rounding**: Do not round sub-scores during intermediate calculations. Carry two decimal places through the weighted formula, then round the Final Score to the nearest integer.
- **Top-3 Gaps Sorting**: Top-3 gaps must be sorted strictly by **point impact** (highest deduction first), not by severity label. A cluster of MEDIUMs or multiple warnings can outrank a single HIGH depending on adjusted point deductions.

---

## Output Format

Generate the final evaluation using the exact structure below:

```markdown
══════════════════════════════════════════════════════
ReadinessScorer Report: <project-name>
══════════════════════════════════════════════════════
Final Score: [0–100] — <Tier Label>
Security Score: [0–100] (weight: 40%)
Architecture Score: [0–100] (weight: 30%)
Safety Score: [0–100] (weight: 30%)
Total Findings: <n> across all agents
══════════════════════════════════════════════════════

Score Breakdown:

CodeSentinel Input:
Verdict: PASS / WARN / FAIL
Deductions: -<n> pts (<finding count> findings)

ArchitectReview Input:
Verdict: PASS / WARN / FAIL
Deductions: -<n> pts (<finding count> findings)

HarnessGuard Input:
Verdict: PASS / WARN / FAIL
Deductions: -<n> pts (<finding count> findings)

──────────────────────────────────────────────────────
Top-3 Gaps (highest-impact items to fix first):

1. [SEVERITY] <finding title> — <which agent> — -<pts> impact
2. [SEVERITY] <finding title> — <which agent> — -<pts> impact
3. [SEVERITY] <finding title> — <which agent> — -<pts> impact

──────────────────────────────────────────────────────
Summary: <two sentences — overall posture + biggest risk>

Recommendation:
✅ Approve / ⚠️ Approve with conditions / 🚨 Block

Conditions (if any):
- <specific item that must be fixed before deploy>
══════════════════════════════════════════════════════
```
