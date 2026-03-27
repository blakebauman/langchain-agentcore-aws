---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Python Conventions

- Target Python 3.11+. Use `str | None` union syntax, not `Optional[str]`.
- Use `from __future__ import annotations` in all new Python modules as project standard.
- Use `@tool` decorator from `langchain_core.tools` when defining new tools.
- All tools must have a docstring — LangChain uses it as the tool description for the LLM.
- Configuration values come from `agentic_ai.config.settings` (Pydantic BaseSettings), never hardcoded.
- AWS clients use boto3 with region from `settings.aws_region`. Do not hardcode regions.
- Ruff is the only linter/formatter. Do not add pylint, black, isort, or flake8 config.
- Tests mock AWS via `conftest.py` autouse fixtures. Never make real AWS API calls in unit tests.
- Use lazy imports (inside function body) for optional dependencies like `bedrock-agentcore` and `langgraph-checkpoint-aws` to avoid import-time failures when packages are not installed.
- `chainlit` is an optional dependency (chat extras). Only import it in `chat.py` — never in core agent/tool modules.
- Put type-only imports in `TYPE_CHECKING` blocks when using `from __future__ import annotations`.
