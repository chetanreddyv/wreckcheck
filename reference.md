***

# Resource → Agent Mapping

## Agent 1: Scout (Orchestrator)
**No external repo needed.** This is pure Deep Agents scaffolding — write it yourself using the `create_deep_agent()` boilerplate from above. It's just a system prompt + sub-agent wiring. 10 minutes to write from scratch.

***

## Agent 2: CodeSentinel (Code Audit Agent)

| Resource | What to take from it |
|---|---|
| **`netresearch/enterprise-readiness-skill`**  [github](https://github.com/netresearch/enterprise-readiness-skill) | The entire SKILL.md structure — security checks, quality gates, compliance checklist. This IS your `code-auditor/SKILL.md`. Rename + adapt. |
| **`LLMSecurity/skillguard`**  [github](https://github.com/LLMSecurity/skillguard) | Take `references/audit-checklist.md` — repurpose as your enterprise hygiene checklist (hardcoded secrets, missing license, no eval harness, no observability). Also steal the PASS/FAIL verdict output format. |
| **`agentskill.sh/production-code-audit`**  [agentskill](https://agentskill.sh/@haniakrim21/production-code-audit) | Take the instruction logic for line-by-line scanning and architecture pattern detection. Paste into the Markdown body of your `code-auditor/SKILL.md`. |

**Net result:** Your `code-auditor/SKILL.md` body is assembled from these three sources. Zero writing from scratch.

***

## Agent 3: ArchitectReview (Architecture Review Agent)

| Resource | What to take from it |
|---|---|
| **`mcpmarket.com/agent-skill-validator`**  [mcpmarket](https://mcpmarket.com/tools/skills/agent-skill-validator) | Its entire validation checklist — YAML frontmatter rules, naming rules, progressive disclosure rules, scripts/references/assets usage. This becomes the skill-compliance section of your `architecture-reviewer/SKILL.md`. |
| **`agentskills/agentskills` (official spec repo)**  [github](https://github.com/agentskills/agentskills) | The spec itself — use it to define the rubric for what a valid model-selection rationale looks like, what ADLC worksheet evidence looks like, what multi-agent delegation patterns qualify. |

**Net result:** Your `architecture-reviewer/SKILL.md` rubric is the agentskills.io spec + validator logic reformatted as a review checklist.

***

## Agent 4: ReadinessScorer (Scoring Agent)

| Resource | What to take from it |
|---|---|
| **`mcpservers.org` AgentRC policy framework**  [mcpservers](https://mcpservers.org/agent-skills/author/github) | The readiness scoring logic — how to weight checks, override impact levels, disable irrelevant checks. This becomes your `readiness-scorer/SKILL.md` scoring formula. |
| **`LLMSecurity/skillguard` verdict format**  [github](https://github.com/LLMSecurity/skillguard) | The structured output pattern (SAFE/SUSPICIOUS/MALICIOUS → repurpose as 0–100 score + sub-scores + top-3 gaps). |

**Net result:** Your `readiness-scorer/SKILL.md` scoring rubric + output template is assembled from these two sources.

***

## One-Glance Summary

```
Scout (Orchestrator)         ← write from scratch (Deep Agents boilerplate, ~10 min)
     │
     ├── CodeSentinel        ← netresearch/enterprise-readiness-skill (SKILL.md body)
     │                          + LLMSecurity/skillguard (checklist + verdict format)
     │                          + agentskill.sh/production-code-audit (scan logic)
     │
     ├── ArchitectReview     ← mcpmarket.com/agent-skill-validator (spec compliance rubric)
     │                          + agentskills/agentskills official spec (rationale rubric)
     │
     └── ReadinessScorer     ← mcpservers.org AgentRC policy (scoring formula + weights)
                                + LLMSecurity/skillguard (structured output template)
```

***
