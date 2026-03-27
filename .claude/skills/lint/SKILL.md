---
name: lint
description: Lint and auto-fix Python and Terraform code
user-invocable: true
allowed-tools: Bash(make *), Bash(.venv/bin/ruff *), Bash(terraform fmt *), Read, Edit
---

# Lint & Format

Run linters and formatters for the project.

## Behavior

1. Run `make fmt` to auto-fix Python files with ruff
2. Run `terraform fmt -recursive infra/` to format Terraform files
3. Run `make lint` to check for remaining issues
4. If ruff reports errors that can't be auto-fixed, read the flagged files and fix them manually
5. Report what was changed/fixed
