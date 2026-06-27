# Reliability & Multi-Agent Stability Checks

Audit the multi-agent orchestration for reliability, loop constraints, and safe output handling:

## AG04 — Insecure Output Handling
- [ ] Agent output written to files that other agents read without sanitisation
  - e.g., `/workspace/*.json` should be validated by consumer before use
- [ ] Report output could be interpreted as a prompt by another agent
  - e.g., including `Ignore previous instructions` in a finding title
- [ ] JSON output is not schema-validated before downstream consumption

## AG09 — Multi-Agent Exploitation
- [ ] No cross-agent prompt injection via shared workspace files
  - e.g., Agent output in `audit.json` should be structured JSON, not free text with instructions
- [ ] Orchestrator only delegates to known, registered sub-agents (not dynamically resolved from user input)
- [ ] Sub-agent names/identities are not user-controlled

## AG10 — Resource Abuse (Execution Stability)
- [ ] No unbounded `while True` loops in agent tool code
- [ ] No recursive agent delegation (A calls B calls A)
- [ ] Hard-crashing on tool execution failures without graceful error messages returned to the agent
