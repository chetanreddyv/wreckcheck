from deepagents import create_deep_agent

try:
    with open("code-auditor/SKILL.md", "r") as f:
        system_prompt = f.read()
except FileNotFoundError:
    system_prompt = "Audit /workspace/repo_contents.txt for enterprise readiness issues. Write findings to /workspace/code_audit.json"

code_sentinel = create_deep_agent(
    name="CodeSentinel",
    model="claude-haiku-3-5",   # cheapest frontier, or swap for local
    system_prompt=system_prompt,
    tools=["read_file", "search_files"]
)
