# Cost Controls

Check for:
1. Tool outputs being silently truncated or capped (e.g., limiting a `cat` or `grep` to 100 lines).
2. Hardcoded token limits on the agent (`max_tokens`).
3. Fallback to cheaper models for simple tasks (e.g., routing to Haiku for formatting, Opus for reasoning).
