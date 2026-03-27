---
name: test
description: Run tests with optional filter for specific test files, classes, or methods
user-invocable: true
allowed-tools: Bash(make *), Bash(python -m pytest *), Bash(.venv/bin/pytest *), Read, Grep, Glob
---

# Run Tests

Run the project test suite. If arguments are provided, use them as pytest filter expressions.

## Behavior

1. If no arguments given: run `make test` (all unit tests with coverage)
2. If arguments given: run `python -m pytest $ARGUMENTS -v --tb=short`
   - Examples: `/test test_tools` → `python -m pytest tests/ -k test_tools -v --tb=short`
   - Examples: `/test tests/unit/test_agents.py` → `python -m pytest tests/unit/test_agents.py -v --tb=short`
3. If tests fail, read the failing test file and the source file under test to diagnose the issue
4. Report a concise summary: passed/failed counts and any failure details
