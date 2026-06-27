# Prompt Injection Checks

Check for:
1. User input directly concatenated or interpolated into a system prompt.
2. Missing `<user_input>` XML tag fences around external data.
3. Tool outputs being fed back into system context without boundary markers.
