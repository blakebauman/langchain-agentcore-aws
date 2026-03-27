---
paths:
  - "src/agentic_ai/chat.py"
  - ".chainlit/**"
---

# Chat UI Conventions

- Chainlit is an optional dependency (`pip install -e ".[chat]"`). Only import it in `chat.py`, never in core modules.
- Use `cl.user_session` for per-session state (agent, thread_id, agent_type). Never use module-level globals for session state.
- Tool calls render as `cl.Step` with `type="tool"`. Planning steps use `type="run"`.
- Streaming uses `agent.astream_events(..., version="v2")` with `response.stream_token()`.
- Auth is opt-in: requires both `CHAT_AUTH_SECRET` and `CHAT_AUTH_PASSWORD`. The callback registers conditionally at module scope.
- Chat profiles map to agent types via `_profile_to_agent_type()`. Add new profiles there when adding agent factories.
- `CHAT_PERSISTENCE` controls checkpointer: "memory" (default), "sqlite", or "agentcore".
- Chainlit config: `.chainlit/config.toml`. Welcome message: `chainlit.md` at project root.
