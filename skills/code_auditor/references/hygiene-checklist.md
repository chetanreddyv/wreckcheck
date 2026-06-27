# Code Hygiene Checklist

Full per-dimension checklist for CodeSentinel audits.
Work through every section in order. Every unchecked item is a potential finding.

---

## Dimension 1 — Secrets (max 20pts)

### File-Level
- [ ] `.env` is listed in `.gitignore`
- [ ] `.env` is NOT tracked in git history (check `git log --all -- .env`)
- [ ] No `.env.local`, `.env.production`, `.env.staging` committed
- [ ] `secrets/`, `credentials/`, `keys/` directories are gitignored

### Code-Level (grep for these patterns)
- [ ] No `api_key = "sk-...` literals in source files
- [ ] No `password = "..."` or `passwd = "..."` hardcoded
- [ ] No `token = "..."` or `access_token = "..."` in source
- [ ] No base64-encoded secrets (long base64 strings in string literals)
- [ ] No AWS/GCP/Azure credential patterns (`AKIA`, `AIza`, `eyJ`)
- [ ] No private key PEM blocks (`-----BEGIN RSA PRIVATE KEY-----`)
- [ ] Environment variables loaded via `os.getenv()` or `python-dotenv`, not hardcoded

### Config Files
- [ ] `config.yaml` / `config.json` contain no plaintext credentials
- [ ] Database connection strings use env var substitution, not literals

**Deduction guide:**
- Committed `.env` with values: CRITICAL (−10)
- Hardcoded API key in source: CRITICAL (−10)
- Hardcoded password in source: HIGH (−6)
- `.env` exists but gitignored — check history: HIGH (−6) if in history
- Floating secrets pattern (env var names suggest secrets, no `.env.example`): MEDIUM (−3)

---

## Dimension 2 — Dependencies (max 20pts)

### Pinning
- [ ] `requirements.txt` uses `==` (pinned), not `>=` or no version
- [ ] `package.json` uses exact versions or lockfile committed (`package-lock.json`, `yarn.lock`)
- [ ] `composer.json` has `composer.lock` committed
- [ ] No `latest` tags in Dockerfile base images

### Supply Chain
- [ ] All packages are from official registries (PyPI, npm, Packagist)
- [ ] No packages with Levenshtein distance ≤1 from popular packages (typosquatting)
- [ ] No `curl | sh` or `wget | bash` in install scripts
- [ ] No runtime fetching of remote code (`exec(requests.get(...).text)`)

### Maintenance
- [ ] Dependency file exists at all (CRITICAL if absent for non-trivial project)
- [ ] No obviously abandoned packages (check for packages with 0 recent commits)
- [ ] `dependabot.yml` or Renovate configured for automated updates (INFO if absent)

**Deduction guide:**
- No `requirements.txt` / `package.json` at all: HIGH (−6)
- All deps unpinned (`>=` or no version): MEDIUM (−3)
- Typosquatting candidate detected: HIGH (−6)
- Remote code execution in install: CRITICAL (−10)
- No lockfile committed: LOW (−1)

---

## Dimension 3 — Observability (max 20pts)

### Logging
- [ ] Structured logging configured (not bare `print()` statements for errors)
- [ ] Log levels used appropriately (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- [ ] Agent reasoning/decisions are logged (for AI agent repos)
- [ ] No sensitive data in log output (credentials, PII)

### Error Handling
- [ ] Exceptions are caught and logged, not silently swallowed (`except: pass`)
- [ ] Error messages include context (file, function, input that caused error)
- [ ] API errors surfaced to caller, not hidden

### Tracing / Metrics (AI agent specific)
- [ ] Token usage logged per call (for LLM-based agents)
- [ ] Agent tool calls are logged with inputs/outputs
- [ ] Latency tracked for sub-agent calls
- [ ] Output files written (e.g., `/workspace/*.json`) are confirmed after write

**Deduction guide:**
- No logging at all: HIGH (−6)
- Silent exception swallowing (`except: pass`): MEDIUM (−3) per occurrence
- No token/cost tracking in LLM agent: MEDIUM (−3)
- No error propagation from sub-agents: MEDIUM (−3)
- `print()` only for errors (no structured logging): LOW (−1)

---

## Dimension 4 — Testing & Eval Harness (max 20pts)

### Test Files
- [ ] `tests/` or `test/` directory exists
- [ ] At least one test file present (`test_*.py`, `*_test.py`, `*.test.js`)
- [ ] Tests can be run with a standard command (`pytest`, `npm test`, etc.)
- [ ] Tests are referenced in CI workflow

### Eval Harness (AI agent specific)
- [ ] `evals/` directory exists
- [ ] `evals/evals.json` or equivalent eval cases defined
- [ ] Eval runner script exists (`run_evals.py` or similar)
- [ ] README documents how to run evals
- [ ] Evals cover at least 3 distinct input cases

### Coverage
- [ ] Coverage tooling configured (`pytest-cov`, `coverage.py`, `nyc`)
- [ ] Coverage threshold enforced in CI (warning if absent)
- [ ] README states expected coverage level

**Deduction guide:**
- No tests at all: HIGH (−6)
- No eval harness in AI agent repo: HIGH (−6)
- Tests exist but not in CI: MEDIUM (−3)
- No coverage tooling: LOW (−1)
- Evals defined but no runner: LOW (−1)

---

## Dimension 5 — CI/CD Hardening (max 20pts)

### Workflow Basics
- [ ] CI workflow file exists (`.github/workflows/*.yml`)
- [ ] CI runs on push to main AND on pull requests
- [ ] CI includes linting step
- [ ] CI includes test step

### Security Hardening
- [ ] `permissions:` declared at workflow level (`contents: read` minimum)
- [ ] Third-party GitHub Actions pinned to SHA, not floating tag (`uses: actions/checkout@abc123 # v4`)
- [ ] No `${{ github.event.* }}` interpolated directly in `run:` blocks (injection risk)
- [ ] Secrets accessed via `${{ secrets.NAME }}`, not hardcoded
- [ ] No `pull_request_target` with write permissions + checkout of PR code (high-risk pattern)

### Supply Chain
- [ ] `SECURITY.md` or security policy exists in repo
- [ ] `LICENSE` file exists (CRITICAL if absent for published project)
- [ ] `CODEOWNERS` defined (INFO if absent)

**Deduction guide:**
- No CI at all: HIGH (−6)
- `LICENSE` file absent: HIGH (−6)
- No `permissions:` in any workflow: MEDIUM (−3)
- Floating action versions (e.g., `@v4` not SHA): MEDIUM (−3)
- GitHub event interpolated in `run:`: HIGH (−6)
- No `SECURITY.md`: LOW (−1)
