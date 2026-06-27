# Prompt Injection & Security Checks

Audit the agent's system prompts, tools, and execution environment for the following OWASP Agentic Top 10 risks:

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

## AG03 — Excessive Agency
- [ ] File access tools can read/write outside defined workspace (`../`, `~/.ssh`, `/etc/`)
- [ ] Agent tools include `sudo` or privilege escalation
- [ ] Background process spawning (`nohup`, `&`, daemon patterns)
- [ ] Agent can modify its own skill files or other agents' configs
- [ ] Tool scope covers systems beyond stated purpose

## AG05 — Data Exfiltration
- [ ] Agent code makes outbound HTTP requests to domains not in its stated purpose
- [ ] Environment variables harvested and included in output/logs (`os.environ`)
- [ ] Repo contents written to external service (not just `/workspace/`)
- [ ] Sensitive file paths read and contents included in output unnecessarily

## AG08 — Memory Poisoning
- [ ] Agent does NOT write to `MEMORY.md`, `AGENTS.md`, `SOUL.md`, or system context files
- [ ] Agent does NOT modify other agents' SKILL.md files
- [ ] Shared workspace (`/workspace/`) is scoped — agents only write their own output files
- [ ] No persistent context injection across runs (stateless between invocations)
