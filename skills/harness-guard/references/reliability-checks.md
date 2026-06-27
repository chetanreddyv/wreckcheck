# Reliability Checks

Check for:
1. `while True` loops driving agent actions without a `max_steps` or `max_iterations` counter.
2. Recursive delegation between agents (A -> B -> A).
3. Hard-crashing on tool execution failures without graceful error messages returned to the agent.
