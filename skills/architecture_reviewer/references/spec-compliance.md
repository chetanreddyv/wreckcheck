# Agentskills.io Specification Compliance Guide

This reference document defines the complete agentskills.io specification rules and ruling guidelines. Reviewers must refer to these rules when scoring structural quality, validating frontmatter syntax, or evaluating progressive disclosure compliance.

---

## 1. Core Principles of the Specification

The agentskills.io specification ensures that agent skills are portable, deterministic, token-efficient, and maintainable across different AI agent runtimes.

### 1.1 Autonomous Agent Customization
Skills are self-contained packages of domain expertise, procedural workflows, and specialized instructions that extend an agent's capabilities without requiring code changes to the underlying agent framework.

### 1.2 Progressive Disclosure
To prevent context window saturation and prompt bloat, skills operate on a **progressive disclosure model**:
1. **Metadata Layer**: Only the skill's `name` and `description` from the YAML frontmatter are loaded into the agent's system prompt during discovery.
2. **Activation Layer**: When triggered, the agent reads the core `SKILL.md` instructions.
3. **Reference Layer**: Detailed documentation, templates, or scripts are loaded **only on demand** when specific conditions defined in `SKILL.md` are met.

### 1.3 Deterministic Triggering
An agent decides whether to activate a skill strictly by semantic matching against its YAML frontmatter `description`. Therefore, descriptions must be precise, actionable, and include explicit trigger keywords.

---

## 2. Directory Structure and Root Rules

### 2.1 Customization Roots
Skills must be placed inside recognized customization roots:
- Workspace scope: `.agents/skills/<skill_name>/` or `skills/<skill_name>/`
- Global scope: `~/.gemini/config/skills/<skill_name>/` or equivalent system agent root.

### 2.2 Standard Subdirectories
A valid skill directory may contain only the following standard subdirectories:
- `scripts/`: Helper scripts, CLI wrappers, or executable utilities. Must not contain static text docs or prompt templates.
- `references/`: Detailed specifications, APIs, rules, or deep documentation loaded conditionally. Must not contain executable code.
- `assets/`: Static templates, boilerplate code, output templates, or diagrams.
- `examples/`: Reference implementations and input/output samples demonstrating skill usage.

---

## 3. YAML Frontmatter Specification

Every `SKILL.md` file must begin with valid YAML frontmatter enclosed by triple dashes (`---`).

### 3.1 `name` Field (Required)
- **Presence**: Mandatory. Must not be blank or missing.
- **Length**: Between 1 and 64 characters.
- **Character Set**: Lowercase letters (`a-z`), numbers (`0-9`), hyphens (`-`), and underscores (`_`). No uppercase characters, no spaces, no special symbols.
- **Hyphen/Underscore Rules**: Must not start or end with `-` or `_`. Must not contain consecutive hyphens (`--`).
- **Directory Consistency**: Must **exactly match** the name of its enclosing parent directory.

### 3.2 `description` Field (Required)
- **Presence**: Mandatory. Must not be blank or missing.
- **Length**: Between 1 and 1024 characters.
- **Dual Requirement**: Must explicitly articulate:
  1. **What it does**: The capabilities and domain functionality provided.
  2. **When to use it**: Trigger keywords, user request patterns, or architectural contexts that signal the agent to activate the skill.
- **Quality Ruling**: Descriptions that lack clear trigger conditions (e.g., *"Useful for git tasks"*) must be ruled as a **WARN**.

### 3.3 Optional Metadata Fields
- `license`: String indicating open-source license (e.g., `MIT`, `Apache-2.0`). Required for public/shared skills.
- `compatibility`: String or object specifying platform requirements (e.g., `macOS`, `Python >= 3.10`, `docker`).
- `metadata`: Key-value pairs containing author identity, version string, or organization tags. Recommended fields: `author`, `version`.
- `allowed-tools`: List of specific tools the skill expects or requires (e.g., `Read`, `Glob`, `Bash(grep:*)`).

---

## 4. Markdown Body & Formatting Standards

### 4.1 Length Constraint
The markdown content of `SKILL.md` (excluding frontmatter) must remain under **500 lines**. If a workflow requires extensive explanations or rules, those sections must be extracted into `references/` files.

### 4.2 Path References
All links to supporting files within `SKILL.md` must use relative formatting from the skill root or standard Markdown file URIs.
- Example: `Read [spec.md](references/spec.md)` or `Read [template](file:///path/to/assets/template.md)`.

### 4.3 Reference Depth Limit
Reference chains must not exceed **one level deep**. A core `SKILL.md` file may instruct an agent to load `references/details.md`, but `references/details.md` must not instruct the agent to load secondary reference files (`references/sub-details.md`). All secondary context must be self-contained or referenced directly from `SKILL.md`.

---

## 5. Ruling Matrix & Severity Classifications

When reviewing a skill against this specification, categorize findings using the following severity rubric:

| Infraction / Gap | Severity | Ruling Justification |
| :--- | :--- | :--- |
| Missing `name` or `description` in frontmatter | 🚨 **FAIL** | Prevents agent discovery and indexing. |
| `name` mismatch with parent directory name | 🚨 **FAIL** | Breaks namespace resolution and path mapping. |
| Uppercase letters, spaces, or invalid chars in `name` | 🚨 **FAIL** | Violates strict URI and slug formatting rules. |
| Circular reference or multi-agent infinite hand-off | 🚨 **FAIL** | Causes runtime deadlock or infinite token consumption. |
| Missing conditional trigger clauses for references | ⚠️ **WARN** | Violates progressive disclosure; increases token bloat. |
| Unconditionally reading all reference files on launch | ⚠️ **WARN** | Defeats token optimization of skill architecture. |
| Vague description lacking trigger keywords | ⚠️ **WARN** | Leads to missed activations or false-positive triggers. |
| Misplaced file types (e.g., code in `references/`) | ⚠️ **WARN** | Degrades structural hygiene and maintainability. |
| `SKILL.md` body exceeding 500 lines | ⚠️ **WARN** | Risk of context dilution and prompt bloat. |
| Minor formatting or typographical inconsistencies | ℹ️ **INFO** | Does not impact agent execution or spec compliance. |
