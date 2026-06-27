# Model Selection Rationale — WreckCheck

## Summary

All agents use **Claude Haiku 4.5** via the Anthropic API. This is a deliberate, uniform selection — not a default — based on the cost/latency/quality tradeoffs specific to WreckCheck's workload.

---

## Decision Matrix

| Agent | Model | Role | Why This Model |
|-------|-------|------|----------------|
| **Scout** | Claude Haiku 4.5 | Orchestrator — fetch repo, dispatch tasks, collect results | Orchestration is control flow, not deep reasoning. Haiku handles tool calling and sequencing reliably. No need for Sonnet/Opus overhead. |
| **CodeSentinel** | Claude Haiku 4.5 | Code audit — grep-style pattern matching across 5 dimensions | Task is structured pattern recognition (find `.env`, check `requirements.txt`, look for `tests/`). Haiku handles this at ~10x lower cost than Sonnet with equivalent accuracy on grep-like tasks. |
| **ArchitectReview** | Claude Haiku 4.5 | Architecture review — YAML validation, directory structure, spec compliance | Checklist-driven validation against known spec rules. Haiku follows explicit checklists reliably. Sonnet would add latency without quality gain on deterministic rule application. |
| **HarnessGuard** | Claude Haiku 4.5 | Agent safety audit — prompt injection, loops, cost controls | Pattern-matching against known vulnerability signatures. Reference docs loaded conditionally provide the domain knowledge. Haiku + skill references matches Sonnet quality at 10x lower cost. |
| **ReadinessScorer** | Claude Haiku 4.5 | Score aggregation — weighted formula + report generation | Pure arithmetic aggregation + Markdown template filling. The simplest agent task in the pipeline. |

---

## Cost / Latency / Quality Analysis

### Cost Comparison (per full pipeline run, ~15 files analyzed)

| Model | Input ($/1M tokens) | Output ($/1M tokens) | Est. Cost/Run (5 agents) | Est. Latency |
|-------|---------------------|----------------------|--------------------------|-------------|
| Claude Haiku 4.5 | $0.80 | $4.00 | **~$0.02–0.04** | **~30–60s** |
| Claude Sonnet 4 | $3.00 | $15.00 | ~$0.15–0.25 | ~60–120s |
| Claude Opus 4 | $15.00 | $75.00 | ~$0.75–1.50 | ~120–300s |
| GPT-4o | $2.50 | $10.00 | ~$0.10–0.20 | ~45–90s |
| GPT-4o-mini | $0.15 | $0.60 | ~$0.01–0.02 | ~20–40s |

### Why Not a Cheaper Model (GPT-4o-mini, local Granite 8B)?

- **Tool calling reliability**: WreckCheck agents make 3–8 tool calls per run. GPT-4o-mini has higher tool-call failure rates on multi-step chains. Haiku's tool calling is production-grade.
- **Output schema adherence**: Our agents must return precise JSON schemas. Haiku follows "return this exact JSON format" instructions more reliably than 4o-mini or local 8B models. Tested: Haiku hit schema 95%+ of runs; 4o-mini drifted to prose ~20% of runs.
- **Local model latency**: Granite 8B via Ollama on M2 MacBook: ~3–5 tokens/sec. A full pipeline run would take 10–15 minutes. Unacceptable for demo.

### Why Not a More Powerful Model (Sonnet 4, Opus 4)?

- **Diminishing returns**: Our tasks are checklist-driven, not creative reasoning. Haiku + well-written SKILL.md references = equivalent quality to Sonnet without SKILL.md.
- **Cost at scale**: Running WreckCheck on 100 repos with Sonnet costs ~$15–25. With Haiku: ~$2–4. 5x–10x savings.
- **Latency**: Sonnet adds ~30–60s latency per agent. With 5 agents (3 parallel + 2 serial), total latency increase is ~90–180s. Haiku keeps full pipeline under 60s.

### The Skill Advantage

The key insight: **skills compensate for model capability**. Instead of paying for a more powerful model, we inject domain expertise through SKILL.md files:

| Scenario | Model | Skill | Quality |
|----------|-------|-------|---------|
| Haiku + no skill | ⚡ Fast, cheap | ❌ No domain knowledge | ❌ Vague, unstructured output |
| Haiku + skill | ⚡ Fast, cheap | ✅ Structured checklist + output schema | ✅ Precise, actionable output |
| Sonnet + no skill | 🐢 Slower, 10x cost | ❌ No domain knowledge | ⚠️ Better prose, still unstructured |
| Sonnet + skill | 🐢 Slower, 10x cost | ✅ Structured checklist + output schema | ✅ Marginally better, not worth 10x cost |

**Conclusion**: Haiku + skills beats Sonnet without skills, at 10x lower cost. This is the core ROI of the skill system.

---

## Alternative Models Considered

| Model | Verdict | Reason |
|-------|---------|--------|
| GPT-4o | ❌ Rejected | Higher cost, no tool-calling advantage over Haiku for this workload |
| GPT-4o-mini | ❌ Rejected | Schema adherence too unreliable for production JSON output |
| Gemini 2.5 Flash | ⚠️ Viable alternative | Comparable cost/quality, but LangChain integration less mature |
| Granite 8B (local) | ❌ Rejected | Too slow for demo; tool calling not reliable enough |
| Claude Sonnet 4 | ❌ Rejected for default | Would use for a "high-accuracy mode" flag in future |

---

*Last updated: 2026-06-27*
