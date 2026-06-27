from deepagents import create_deep_agent

try:
    with open("skills/harness-guard/SKILL.md", "r") as f:
        system_prompt = f.read()
except FileNotFoundError:
    system_prompt = "Audit the codebase for agent safety, prompt injection, cost, observability, and loop controls, and return the structured JSON report."

harness_guard = create_deep_agent(
    name="harness-guard",
    model="claude-haiku-4-5",
    system_prompt=system_prompt,
    skills=["./skills/harness-guard/"],
    tools=["read_file", "search_files"]
)
