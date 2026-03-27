---
name: aws
description: Look up AWS service docs, CLI commands, SDK patterns, IAM policies, and IaC guidance
user-invocable: true
allowed-tools: WebSearch, WebFetch(domain:docs.aws.amazon.com), WebFetch(domain:aws.amazon.com), WebFetch(domain:registry.terraform.io), WebFetch(domain:pypi.org), Read, Grep, Glob
---

# AWS Guidance

Look up AWS documentation and provide actionable guidance on services, CLI commands, boto3 SDK patterns, IAM policies, and infrastructure-as-code.

## Arguments

Topic or question: $ARGUMENTS

## Behavior

1. Search AWS documentation for the topic using WebSearch and WebFetch
2. If the question relates to this project's AWS usage, read relevant source files:
   - `src/agentic_ai/config.py` for current AWS settings
   - `infra/` for Terraform resources
   - `src/agentic_ai/tools/` for boto3 patterns already in use
3. For IAM questions, provide least-privilege policy JSON with the specific actions needed
4. For CLI commands, show the complete `aws` command with required flags
5. For boto3/SDK questions, follow this project's conventions: use `settings.aws_region`, never hardcode regions
6. For Terraform, show the resource block and note any required IAM permissions
7. Cite the specific documentation URL for every recommendation
