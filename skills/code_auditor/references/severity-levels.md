# Severity Levels

Use these definitions consistently across all findings.
When in doubt between two levels, choose the higher one.

---

## 🔴 CRITICAL — Score deduction: −10

Conditions that expose the project to immediate, high-probability exploitation or
data loss. A single CRITICAL finding can block enterprise adoption entirely.

**Examples:**
- Hardcoded API key, password, or secret in committed code or `.env`
- `.env` file tracked in git (even if currently empty — it has been in history)
- Remote code execution in install or setup scripts (`curl | sh`)
- GitHub Actions workflow allows code injection via `${{ github.event.* }}` in `run:` block
- Private key file committed to repository
- Dependency with known critical CVE (CVSS ≥ 9.0) with no mitigation

**Action required:** Block merge / flag as DO NOT DEPLOY until resolved.

---

## 🟠 HIGH — Score deduction: −6

Conditions that create significant security or quality risk, likely exploitable
under normal operation. Must be resolved before enterprise deployment.

**Examples:**
- No license file in a public/distributed project
- All dependencies unpinned with no lockfile
- Typosquatting candidate in dependency list
- No CI workflow at all
- GitHub Actions using floating tags (`@v4`) not SHA-pinned
- Sensitive data in git history (even if removed from HEAD)
- No `permissions:` declaration in any CI workflow
- `.env` in git history (even if now gitignored)
- No error handling — exceptions silently swallowed throughout codebase
- No tests and no eval harness in an AI agent project

**Action required:** Must fix before enterprise pilot.

---

## 🟡 MEDIUM — Score deduction: −3

Conditions that reduce quality, increase operational risk, or signal
immaturity in enterprise processes. Should be resolved in next sprint.

**Examples:**
- Unpinned dependencies (e.g., `requests>=2.0`) without lockfile
- No structured logging (bare `print()` for errors/debug)
- No token/cost tracking in an LLM agent
- Tests exist but not wired into CI
- `SECURITY.md` absent
- No eval harness defined for AI agent (eval cases missing, not just runner)
- Sub-agent outputs not verified before next step
- Floating action version tag used (e.g., `actions/checkout@v4` not SHA)

**Action required:** Fix within 1–2 sprints. Will reduce enterprise readiness score.

---

## 🔵 LOW — Score deduction: −1

Quality/hygiene issues that are best-practice violations but low operational
risk. Fix opportunistically.

**Examples:**
- No `CODEOWNERS` file
- `dependabot.yml` absent (but deps are pinned)
- No coverage tooling configured
- README missing setup instructions
- Eval runner exists but not documented in README
- No lockfile but deps are pinned with `==`
- `print()` used for non-error output in agent code

**Action required:** Fix in next cleanup sprint or alongside related work.

---

## ⚪ INFO — Score deduction: 0

Informational observations that are not problems but may be relevant context
for the ReadinessScorer or human reviewer.

**Examples:**
- Repository is private (no license issue, but noted)
- Language or framework choice noted for context
- Dependency count noted (no risk, but context for SBOM generation)
- File structure observation

**Action required:** None. Include in report for context only.

---

## Severity Decision Tree

```
Is it exploitable right now with no additional steps?
  YES → CRITICAL

Would it enable exploitation under realistic conditions?
  YES → HIGH

Does it violate an enterprise requirement or best practice with real risk?
  YES → MEDIUM

Is it a hygiene issue with minimal operational risk?
  YES → LOW

Is it purely informational context?
  YES → INFO
```
