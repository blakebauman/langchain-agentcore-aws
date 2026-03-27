---
name: deploy-infra
description: Plan Terraform infrastructure changes (requires user approval to apply)
user-invocable: true
allowed-tools: Bash(make infra-init), Bash(make infra-plan), Bash(terraform *), Read, Glob
---

# Infrastructure Deployment

Plan infrastructure changes for review. **Never auto-apply.**

## Behavior

1. Run `make infra-init` to initialize Terraform
2. Run `make infra-plan` to generate the execution plan
3. Summarize what resources will be created, modified, or destroyed
4. Ask the user to confirm before applying — do NOT run `make infra-apply` without explicit approval
