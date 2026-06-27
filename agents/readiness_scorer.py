from deepagents import create_deep_agent

try:
    with open("skills/readiness-scorer/SKILL.md", "r") as f:
        system_prompt = f.read()
except FileNotFoundError:
    system_prompt = "Read the JSON reports provided from CodeSentinel, ArchitectReview, and HarnessGuard to produce a final report."

readiness_scorer = create_deep_agent(
    name="ReadinessScorer",
    model="claude-haiku-4-5",
    system_prompt=system_prompt,
    tools=["read_file", "search_files"]
)
