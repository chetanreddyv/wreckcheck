from deepagents import create_deep_agent

try:
    with open("skills/architecture-reviewer/SKILL.md", "r") as f:
        system_prompt = f.read()
except FileNotFoundError:
    system_prompt = "Review /workspace/repo_contents.txt for architecture quality and return a structured JSON report."

arch_reviewer = create_deep_agent(
    name="ArchitectReview",
    model="claude-sonnet-4-6",
    system_prompt=system_prompt,
    tools=["read_file"]
)
