# Cost & Supply Chain Controls

Audit the agent for unbounded resource consumption and unpinned dependencies:

## AG06 — Supply Chain (Agent-Specific)
- [ ] Agent framework (`deepagents`, `langchain`, etc.) pinned to exact version in dependencies
- [ ] No runtime code fetching (`exec(requests.get(...).text)`)
- [ ] SKILL.md files from third-party sources reviewed before `allowed-tools` grants
- [ ] Sub-agent packages are from verified sources

## AG10 — Resource Abuse (Cost Limits)
- [ ] File fetch tools have a timeout (`timeout=5` on requests calls)
- [ ] Token budget per run is bounded (hard limit on LLM calls per agent run)
- [ ] Tool outputs are truncated or capped to prevent context window blowups (e.g., limiting `grep` to 100 lines)
- [ ] Workspace cleanup after run (temp files removed)
- [ ] Fallback to cheaper models for simple routing or formatting tasks
