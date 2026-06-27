from deepagents import create_deep_agent
from tools import fetch_repo_files, read_file, write_file

# --- Define sub-agents first (import from their own files) ---
from agents.code_sentinel import code_sentinel
from agents.arch_reviewer import arch_reviewer
from agents.readiness_scorer import readiness_scorer

SCOUT_SYSTEM_PROMPT = """
You are Scout, the orchestrating agent of the ReadyCheck enterprise readiness system.

YOUR ONLY JOB:
1. Receive a GitHub repo URL and product description.
2. Fetch these files from the repo (use read_url or clone tools):
   - README.md
   - Any SKILL.md files found
   - Main entry point (main.py, app.py, index.js, etc.)
   - Any .env.example or requirements.txt / package.json
   - Any ADLC worksheet or docs/ folder contents
3. Write all fetched content to /workspace/repo_contents.txt
4. Delegate to CodeSentinel: "Audit /workspace/repo_contents.txt for enterprise readiness issues and return the structured JSON report."
5. Delegate to ArchitectReview: "Review /workspace/repo_contents.txt for architecture quality and return the structured JSON report."
6. Delegate to HarnessGuard: "Audit the codebase for agent safety, prompt injection, cost, observability, and loop controls, and return the structured JSON report."
7. Wait for CodeSentinel, ArchitectReview, and HarnessGuard to return their JSON reports.
8. Delegate to ReadinessScorer: "Analyze the following JSON reports from CodeSentinel, ArchitectReview, and HarnessGuard to produce a final enterprise readiness report." (Pass the returned JSON objects as input).
9. Return ReadinessScorer's final report as your final output.

RULES:
- Do NOT perform any auditing or scoring yourself.
- Do NOT skip delegation — always route to the correct sub-agent.
- Do NOT proceed to ReadinessScorer until CodeSentinel, ArchitectReview, and HarnessGuard have returned their JSON responses.
- If a file cannot be fetched from the repo, write "NOT FOUND" for that file in repo_contents.txt and continue.
"""

harness_guard = {
    "name": "harness-guard",
    "description": "Audits agent code for security, observability, reliability, and cost controls.",
    "system_prompt": open("skills/harness-guard/SKILL.md").read(),
    "skills": ["./skills/harness-guard/"],
    "tools": [read_file, write_file],
    "model_settings": {
        "model": "anthropic:claude-3-5-haiku-20241022",
        "temperature": 0,
        "max_tokens": 4000,
    },
}

# --- Scout (Orchestrator) ---
scout = create_deep_agent(
    name="Scout",
    model="claude-sonnet-4-5",
    sub_agents=[code_sentinel, arch_reviewer, harness_guard, readiness_scorer],
    tools=[fetch_repo_files, read_file, write_file],
    system_prompt=SCOUT_SYSTEM_PROMPT,
    workspace_dir="./workspace",
)

# --- Entry point ---
def run(repo_url: str, description: str) -> str:
    result = scout.run(
        f"Assess enterprise readiness for: {repo_url}\nProduct description: {description}"
    )
    return result

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/your/repo"
    desc = sys.argv[2] if len(sys.argv) > 2 else "Multi-agent AI system"
    print(run(url, desc))