---
name: architecture-reviewer
description: >
  Reviews agent skill architecture for spec compliance, structural quality,
  and multi-agent design validity. Use when asked to review a SKILL.md file,
  validate agent architecture, check skill folder structure, audit delegation
  patterns, or verify a skill meets the agentskills.io specification.
license: MIT
metadata:
  author: your-org
  version: "1.0.0"
allowed-tools: Read Glob Bash(grep:*)
---

# Architecture Reviewer

Review agent skills and multi-agent designs against the agentskills.io specification and architecture quality standards. Return a structured JSON report.

## Review Workflow

Execute the following review workflow sequentially when auditing an agent skill or multi-agent design:

- [ ] **Step 1: File Inventory** — Inventory all files and directories in the skill folder.
- [ ] **Step 2: YAML Frontmatter Validation** — Verify frontmatter fields against strict specification rules.
- [ ] **Step 3: Directory and File Organization** — Audit directory structure and file placement.
- [ ] **Step 4: Progressive Disclosure Compliance** — Ensure token efficiency and conditional loading.
- [ ] **Step 5: Architecture Rationale and Delegation Design** — Evaluate agent responsibilities and multi-agent interactions.
- [ ] **Step 6: Output Verdict** — Generate a comprehensive review report using the standard template.

---

## Step 1 — File Inventory

1. List every file and folder present within the skill directory.
2. Flag any files exceeding **500 lines** of text.
3. Identify unexpected file types (e.g., compiled binaries, large archives, or deeply nested directories beyond standard structures).
4. Confirm that `SKILL.md` exists directly at the root of the skill directory.

---

## Step 2 — YAML Frontmatter Validation

Check each frontmatter field against the following requirements:

### `name` (required)
- Present and non-empty.
- 1–64 characters in length.
- Contains only lowercase letters, numbers, hyphens, or underscores (`[a-z0-9_-]+`) — no uppercase letters, no spaces.
- Does not start or end with a hyphen or underscore.
- Contains no consecutive hyphens (`--`).
- **Exactly matches** the parent folder name.

### `description` (required)
- Present and non-empty.
- 1–1024 characters in length.
- Clearly describes **BOTH** what the skill does **AND** when an agent should trigger or use it.
- Contains specific trigger keywords and scenarios that an autonomous agent can match against.
- Must not be vague (e.g., "helps with code" fails; "use when asked to audit Python code for security vulnerabilities" passes).

### Optional Fields
- `license`: Should be present if the skill is intended to be shared, distributed, or published.
- `compatibility`: Only included if the skill has real, specific environment or platform requirements (e.g., OS, tool binaries).
- `metadata`: For production skills, must include at least `author` and `version`.
- `allowed-tools`: List of tools scoped strictly to the minimum required permissions (favoring read-only tools where possible).

---

## Step 3 — Directory and File Organization

Evaluate folder organization and file placement:

- `scripts/`: Must contain only runnable utility scripts or executable helpers — no documentation, raw data, or templates.
- `references/`: Must contain supplementary documentation, detailed specifications, or reference guides — no runnable execution logic.
- `assets/`: Must contain static resources, templates, images, or boilerplate files — no instructions or core logic.
- **Purpose Check**: Verify no file is placed in an incorrect directory (e.g., core instructions buried in `assets/` or scripts in `references/`).
- **Path References**: All file paths referenced in `SKILL.md` must use relative paths from the skill root.
- **Reference Depth**: No deeply nested reference chains (maximum one level deep; e.g., `SKILL.md` may link to `references/doc.md`, but `references/doc.md` must not require loading further sub-references).

> [!WARNING]
> If a file or resource is placed in the wrong directory or violates path reference rules, record a **MEDIUM** finding.

---

## Step 4 — Progressive Disclosure Compliance

Audit the skill for adherence to progressive disclosure principles:

- **Line Limit**: The `SKILL.md` body must remain well under 500 lines.
- **Core Visibility**: Core operational instructions must reside in `SKILL.md`, not hidden inside reference files.
- **Conditional Loading**: Files in `references/` must only be loaded conditionally. `SKILL.md` must explicitly define **WHEN** and under what specific conditions an agent should read each reference file.
- **No Unconditional Loading**: `SKILL.md` must never instruct the agent to unconditionally read all reference files upon skill activation.
- **Trigger Clarity**: Generic instructions such as *"see references/ for details"* without explicit trigger conditions result in a **MEDIUM** finding.

> **Conditional Trigger**: Read `skills/architecture-reviewer/references/spec-compliance.md` if any progressive disclosure violations, frontmatter ambiguities, or structural discrepancies are found and require detailed ruling against the agentskills.io specification.

---

## Step 5 — Architecture Rationale and Delegation Design

### Model or Agent Selection Rationale
Each agent or skill within the architecture must clearly justify its design:
- What is its single, focused responsibility?
- Why is it designed as a separate entity rather than merged with another skill or agent?
- What specific class of task is it optimized for (e.g., orchestration, auditing, scoring, extraction, validation)?
- If a specialized or higher-capacity model is specified, what complexity justifies it?

> [!WARNING]
> Record a **HIGH** finding if architecture rationale is missing, unstated, or vague.

### Multi-Agent Delegation Validity
When evaluating multi-agent systems or complex workflows, verify delegation validity:
- **Valid Orchestration**: A single orchestrator assigns tasks; specialists execute strictly within their domain; structured results return upward.
- **Non-Overlapping Boundaries**: Each agent maintains a distinct, non-overlapping responsibility.
- **Directional Flow**: Task execution flows directionally without circular dependencies.
- **No Duplication**: No two agents perform identical or competing functions.

> **Conditional Trigger**: Read `skills/architecture-reviewer/references/delegation-patterns.md` when evaluating multi-agent architectures, auditing complex multi-agent workflows, or diagnosing suspected circular or duplicate delegation patterns.

> [!CAUTION]
> Record a **CRITICAL** finding if:
> - Two agents claim the same responsibility.
> - Delegation patterns are circular (e.g., Agent A → Agent B → Agent A).
> - An agent receives no clear input specification or produces no defined output.

### ADLC Evidence Check
A production-grade skill must demonstrate Agent Development Lifecycle (ADLC) rigor:
- Clear problem statement and scope definition.
- Explicit agent input and output contracts.
- Anticipated failure modes and error-handling strategies.
- Defined evaluation criteria or success metrics.

> [!WARNING]
> Record a **MEDIUM** finding if ADLC design evidence is absent in a production-level skill.

---

## Step 6 — JSON Output

When concluding the architecture — **ALWAYS** return the JSON structure directly to the caller — do NOT write it to disk.

```json
{
  "agent": "ArchitectReview",
  "version": "1.0.0",
  "target": "<skill-name>",
  "timestamp": "<ISO8601>",
  "summary": {
    "total_findings": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  },
  "dimensions": {
    "frontmatter": { "score": 0, "max": 20, "findings": [] },
    "structure": { "score": 0, "max": 20, "findings": [] },
    "disclosure": { "score": 0, "max": 20, "findings": [] },
    "architecture": { "score": 0, "max": 20, "findings": [] }
  },
  "top_gaps": [],
  "top_fixes": [],
  "recommendation": "<approve | revise and resubmit | block>"
}
```

### Scoring Rules
Each dimension starts at 20 points. Deduct per finding:
- CRITICAL: −10
- HIGH: −6
- MEDIUM: −3
- LOW: −1
- INFO: 0

Floor is 0 per dimension. Total raw score = sum of 4 dimensions (0–80).
