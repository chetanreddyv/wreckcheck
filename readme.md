# WreckCheck — AI Startup Enterprise Readiness Scorer

> A multi-agent system that tells AI founders exactly how enterprise-ready 
> their project is — and what to fix next.

## What it does
Paste in a GitHub repo URL. Get back a 0–100 enterprise readiness score,
sub-scores across 5 dimensions, top-3 gaps, and top-3 actionable fixes.

## Agents
- Scout (Orchestrator) 
- CodeSentinel (Code Audit) 
- ArchitectReview 
- ReadinessScorer 

## Skills
- `code-auditor/` — agentskills.io conformant
- `architecture-reviewer/` — agentskills.io conformant
- `readiness-scorer/` — agentskills.io conformant

## Model Selection Rationale
[your rationale here]

## Setup
pip install deepagents skills-ref
export ANTHROPIC_API_KEY=...
python main.py --repo https://github.com/your/repo

## Eval
cd evals && python run_evals.py
# With skill: 3/3 PASS | Without skill: 0/3 PASS

## License
MIT