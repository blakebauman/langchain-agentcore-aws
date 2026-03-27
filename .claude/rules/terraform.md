---
paths:
  - "infra/**/*.tf"
---

# Terraform Conventions

- All resources go in reusable modules under `infra/modules/`. Environments (`infra/envs/dev/`) compose modules.
- Use `var.project_name` and `var.environment` prefixes for resource naming: `"${var.project_name}-${var.environment}-*"`.
- Tag all resources with `Project` and `Environment` tags.
- Never hardcode AWS account IDs, regions, or ARNs in module code — pass them as variables.
- Bedrock action group API schemas are inline OpenAPI 3.0 JSON in the agent module.
- Run `terraform fmt -recursive` before committing Terraform changes.
- State backend is commented out in `versions.tf` — it's configured per-environment.
- New optional modules (like `agentcore`) should be commented out by default in env compositions, matching the pattern used for `lambda-action-group`.
- Use `dynamic` blocks and conditional `count` for optional resources gated by feature flags (e.g., `var.enable_memory`).
