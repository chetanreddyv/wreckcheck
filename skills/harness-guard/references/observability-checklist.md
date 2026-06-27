# Observability Checklist

Ensure the agent system is fully instrumented for auditing and trace analysis:

## AG07 — Insufficient Monitoring
- [ ] Every tool call is logged with: tool name, inputs, outputs, timestamp
- [ ] Sub-agent delegation is logged (Orchestrator logs which agent it called and when)
- [ ] Token usage per LLM call is recorded
- [ ] Output file writes are confirmed (agent verifies file exists after write)
- [ ] Failed tool calls are logged with full error context, not swallowed
- [ ] Agent trajectories being saved or logged (e.g., LangSmith, local JSON logs)
- [ ] Eval hooks or `agenteval` / `promptfoo` configurations exist in the repository
