import os
import dotenv
dotenv.load_dotenv()
if "anthropic_api_key" in os.environ and "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = os.environ["anthropic_api_key"]
from deepagents import create_deep_agent, AsyncSubAgent
from tools import fetch_repo_files

# --- Only import ReadinessScorer eagerly (sync delegation target) ---
# CodeSentinel, ArchitectReview, HarnessGuard are resolved dynamically via importlib in deepagents.py
from agents.readiness_scorer import readiness_scorer

SCOUT_SYSTEM_PROMPT = """
You are Scout, the orchestrating agent of the ReadyCheck enterprise readiness system.

YOUR ONLY JOB:
1. Receive a GitHub repo URL and product description.
2. Fetch these files from the repo (use the fetch_repo_files tool). This tool automatically writes the fetched content to ./workspace/repo_contents.txt
3. Start an async task for CodeSentinel (use start_async_task_CodeSentinel tool): "Audit ./workspace/repo_contents.txt for enterprise readiness issues and return the structured JSON report."
4. Start an async task for ArchitectReview (use start_async_task_ArchitectReview tool): "Review ./workspace/repo_contents.txt for architecture quality and return the structured JSON report."
5. Start an async task for HarnessGuard (use start_async_task_HarnessGuard tool): "Audit the codebase for agent safety, prompt injection, cost, observability, and loop controls, and return the structured JSON report."
6. WAIT for all three async tasks to complete by using the wait_for_async_tasks tool with the three task IDs returned in steps 3-5.
7. Once you have the results (which are automatically saved to the workspace by the wait_for_async_tasks tool), immediately proceed to step 8.
8. Delegate to ReadinessScorer (use delegate_to_ReadinessScorer tool) with this EXACT instruction:
   "Read the following JSON reports and produce a final enterprise readiness report:
   - workspace/code_sentinel.json (CodeSentinel audit)
   - workspace/architect_review.json (ArchitectReview audit)  
   - workspace/harness_guard.json (HarnessGuard audit)"
9. Return ReadinessScorer's final report as your final output.

RULES:
- Do NOT perform any auditing or scoring yourself.
- Do NOT skip delegation — always route to the correct sub-agent.
- Do NOT proceed to ReadinessScorer until CodeSentinel, ArchitectReview, and HarnessGuard have returned their JSON responses via wait_for_async_tasks.
- If a file cannot be fetched from the repo, write "NOT FOUND" for that file in repo_contents.txt and continue.
- Do NOT use write_file tool to save the results, it is done automatically.
"""

# --- Scout (Orchestrator) ---
scout = create_deep_agent(
    name="Scout",
    model="claude-haiku-4-5",
    sub_agents=[
        AsyncSubAgent(name="CodeSentinel"), 
        AsyncSubAgent(name="ArchitectReview"), 
        AsyncSubAgent(name="HarnessGuard"), 
        readiness_scorer
    ],
    tools=[fetch_repo_files],  # write_file removed — auto-save handles persistence
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
