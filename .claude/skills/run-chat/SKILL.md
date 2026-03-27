---
name: run-chat
description: Start the Chainlit chat UI for interactive agent conversations
user-invocable: true
allowed-tools: Bash(make run-chat *), Bash(source *), Read
---

# Run Chat UI

Start the Chainlit-based web chat interface.

## Behavior

1. Run `make run-chat`
2. The chat UI starts on http://localhost:8000 (configurable via `CHAT_PORT`)
3. If it fails, diagnose the error:
   - Missing `chainlit` package → `pip install -e ".[chat]"`
   - Port already in use → suggest changing `CHAT_PORT` in `.env`
   - AWS credential issues → check `aws configure` and `AWS_PROFILE`
4. To run via Docker instead: `docker compose up chat`
