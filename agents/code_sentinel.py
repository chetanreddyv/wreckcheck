from deepagents import create_deep_agent

try:
    with open("skills/code-auditor/SKILL.md", "r") as f:
        system_prompt = f.read()
except FileNotFoundError:
    system_prompt = "Audit /workspace/repo_contents.txt for enterprise readiness issues and return a structured JSON report."

code_sentinel = create_deep_agent(
    name="CodeSentinel",
    model="claude-haiku-3-5",   # cheapest frontier, or swap for local
    system_prompt=system_prompt,
    tools=["read_file", "search_files"]
)
