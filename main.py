import os
import dotenv
dotenv.load_dotenv()
if "anthropic_api_key" in os.environ and "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = os.environ["anthropic_api_key"]
from deepagents import create_deep_agent
from tools import fetch_repo_files, read_file, write_file

# --- Define sub-agents first (import from their own files) ---
from agents.code_sentinel import code_sentinel
from agents.arch_reviewer import arch_reviewer
from agents.readiness_scorer import readiness_scorer
from agents.harness_guard import harness_guard

SCOUT_SYSTEM_PROMPT = """
You are Scout, the orchestrating agent of the ReadyCheck enterprise readiness system.

YOUR ONLY JOB:
1. Receive a GitHub repo URL and product description.
2. Fetch these files from the repo (use the fetch_repo_files tool). This tool automatically writes the fetched content to ./workspace/repo_contents.txt
3. Delegate to CodeSentinel (use delegate_to_CodeSentinel tool): "Audit ./workspace/repo_contents.txt for enterprise readiness issues and return the structured JSON report."
4. Delegate to ArchitectReview (use delegate_to_ArchitectReview tool): "Review ./workspace/repo_contents.txt for architecture quality and return the structured JSON report."
5. Delegate to HarnessGuard (use delegate_to_harness_guard tool): "Audit the codebase for agent safety, prompt injection, cost, observability, and loop controls, and return the structured JSON report."
6. Wait for CodeSentinel, ArchitectReview, and HarnessGuard to return their JSON reports.
7. Delegate to ReadinessScorer (use delegate_to_ReadinessScorer tool). You MUST provide the `input_text` parameter containing the string: "Analyze the following JSON reports..." followed by all three JSON reports concatenated into a single string.
8. Return ReadinessScorer's final report as your final output.

RULES:
- Do NOT perform any auditing or scoring yourself.
- Do NOT skip delegation — always route to the correct sub-agent.
- Do NOT proceed to ReadinessScorer until CodeSentinel, ArchitectReview, and HarnessGuard have returned their JSON responses.
- If a file cannot be fetched from the repo, write "NOT FOUND" for that file in repo_contents.txt and continue.
"""

# --- Scout (Orchestrator) ---
scout = create_deep_agent(
    name="Scout",
    model="claude-haiku-4-5",
    sub_agents=[code_sentinel, arch_reviewer, harness_guard, readiness_scorer],
    tools=[fetch_repo_files],
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