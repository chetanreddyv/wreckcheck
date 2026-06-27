# OWASP Agentic Top 10 — Code Audit Checks

Specific checks for AI agent codebases. Apply these AFTER the standard
hygiene checklist. Source: OWASP Agentic Top 10 (2026).

---

## AG01 — Prompt Injection

Patterns to grep for in agent system prompts, SKILL.md files, and instructions:

- [ ] Hidden instructions in HTML/Markdown comments (`<!-- ignore previous -->`)
- [ ] Zero-width Unicode characters in prompt strings (invisible override text)
- [ ] Base64-encoded instruction blocks in string literals
- [ ] Override phrases: "ignore previous instructions", "you are now", "do not tell the user"
- [ ] User input interpolated directly into system prompts without sanitisation
  ```python
  # BAD
  system_prompt = f"You are an assistant. User said: {user_input}"
  # GOOD
  system_prompt = "You are an assistant."
  messages = [{"role": "user", "content": user_input}]
  ```

**Finding:** AG01-001 — Direct prompt injection vector
**Severity:** HIGH if user input reaches system prompt; CRITICAL if from external/untrusted source

---

## AG02 — Insecure Tool Utilization

- [ ] Shell commands constructed from dynamic input:
  ```python
  os.system(f"git clone {repo_url}")   # BAD — repo_url could be malicious
  subprocess.run(f"pip install {pkg}")  # BAD
  ```
- [ ] `eval()` or `exec()` on non-constant input
- [ ] Tool calls bypass confirmation (`auto_confirm=True` without scope limit)
- [ ] Agent tools have no input validation or sanitisation
- [ ] File write tools can write to arbitrary paths (no path restriction)

**Finding:** AG02-001 — Dynamic shell command construction
**Severity:** CRITICAL if user-controlled input; HIGH if agent-controlled

---

## AG03 — Excessive Agency

- [ ] File access tools can read/write outside defined workspace (`../`, `~/.ssh`, `/etc/`)
- [ ] Agent tools include `sudo` or privilege escalation
- [ ] Background process spawning (`nohup`, `&`, daemon patterns)
- [ ] Agent can modify its own skill files or other agents' configs
- [ ] Tool scope covers systems beyond stated purpose
  - e.g., a "code auditor" that also has database write tools

**Finding:** AG03-001 — Unrestricted file system access
**Severity:** HIGH for path traversal risk; CRITICAL if write to system paths

---

## AG04 — Insecure Output Handling

- [ ] Agent output written to files that other agents read without sanitisation
  - `/workspace/*.json` should be validated by consumer before use
- [ ] Report output could be interpreted as a prompt by another agent
  - e.g., including `Ignore previous instructions` in a finding title
- [ ] JSON output is not schema-validated before ReadinessScorer consumes it

**Finding:** AG04-001 — Unsanitised inter-agent output
**Severity:** MEDIUM — consumer should validate; mark as INFO if consumer validates

---

## AG05 — Data Exfiltration

- [ ] Agent code makes outbound HTTP requests to domains not in its stated purpose
- [ ] Environment variables harvested and included in output/logs
  ```python
  os.environ  # logging ALL env vars is a data exfiltration risk
  ```
- [ ] Repo contents written to external service (not just `/workspace/`)
- [ ] Sensitive file paths read and contents included in output unnecessarily

**Finding:** AG05-001 — Undocumented outbound HTTP
**Severity:** HIGH if to unknown domain; MEDIUM if to known service but undocumented

---

## AG06 — Supply Chain (Agent-Specific)

- [ ] Agent framework (`deepagents`, `langchain`, etc.) pinned to exact version
- [ ] No runtime code fetching (`exec(requests.get(...).text)`)
- [ ] SKILL.md files from third-party sources reviewed before `allowed-tools` grants
- [ ] Sub-agent packages are from verified sources

**Finding:** AG06-001 — Unpinned agent framework version
**Severity:** MEDIUM

---

## AG07 — Insufficient Monitoring

- [ ] Every tool call is logged with: tool name, inputs, outputs, timestamp
- [ ] Sub-agent delegation is logged (Scout logs which agent it called and when)
- [ ] Token usage per LLM call is recorded
- [ ] Output file writes are confirmed (agent verifies file exists after write)
- [ ] Failed tool calls are logged with full error context, not swallowed

**Finding:** AG07-001 — No tool call logging
**Severity:** MEDIUM

---

## AG08 — Memory Poisoning

- [ ] Agent does NOT write to `MEMORY.md`, `AGENTS.md`, `SOUL.md`, or system context files
- [ ] Agent does NOT modify other agents' SKILL.md files
- [ ] Shared workspace (`/workspace/`) is scoped — agents only write their own output files
- [ ] No persistent context injection across runs (stateless between invocations)

**Finding:** AG08-001 — Agent writes to shared memory file
**Severity:** HIGH

---

## AG09 — Multi-Agent Exploitation

- [ ] No cross-agent prompt injection via shared workspace files
  - Code Sentinel output in `code_audit.json` should be structured JSON, not free text with instructions
- [ ] Scout only delegates to known, registered sub-agents (not dynamically resolved)
- [ ] Sub-agent names/identities are not user-controlled

**Finding:** AG09-001 — Dynamic sub-agent resolution from user input
**Severity:** HIGH

---

## AG10 — Resource Abuse

- [ ] No unbounded loops in agent tool code
- [ ] File fetch tool has timeout (`timeout=5` on requests calls)
- [ ] No recursive agent delegation (A calls B calls A)
- [ ] Token budget per run is bounded (hard limit on LLM calls per agent)
- [ ] Workspace cleanup after run (temp files removed)

**Finding:** AG10-001 — No timeout on external HTTP calls
**Severity:** MEDIUM
