from deepagents import create_deep_agent

try:
    with open("readiness-scorer/SKILL.md", "r") as f:
        system_prompt = f.read()
except FileNotFoundError:
    system_prompt = "Read /workspace/code_audit.json and /workspace/arch_review.json. Produce final report at /workspace/report.md"

readiness_scorer = create_deep_agent(
    name="ReadinessScorer",
    model="claude-haiku-3-5",   # or local
    system_prompt=system_prompt,
    tools=["read_file", "write_file"]
)
