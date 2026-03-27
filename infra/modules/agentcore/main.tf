data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  prefix = "${var.project_name}-${var.environment}"
}

# --- IAM Role for AgentCore ---

data "aws_iam_policy_document" "agentcore_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_iam_role" "agentcore" {
  name               = "${local.prefix}-agentcore"
  assume_role_policy = data.aws_iam_policy_document.agentcore_trust.json
}

data "aws_iam_policy_document" "agentcore_permissions" {
  statement {
    sid    = "BedrockInvoke"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = ["*"]
  }

  dynamic "statement" {
    for_each = var.enable_memory ? [1] : []
    content {
      sid    = "AgentCoreMemory"
      effect = "Allow"
      actions = [
        "bedrock:CreateMemory",
        "bedrock:GetMemory",
        "bedrock:UpdateMemory",
        "bedrock:DeleteMemory",
        "bedrock:SearchMemory",
      ]
      resources = [
        "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:memory/*"
      ]
    }
  }
}

resource "aws_iam_role_policy" "agentcore" {
  name   = "${local.prefix}-agentcore-policy"
  role   = aws_iam_role.agentcore.id
  policy = data.aws_iam_policy_document.agentcore_permissions.json
}

# --- AgentCore Memory ---
# Note: AgentCore Memory resources are managed via the AgentCore SDK/Console.
# The Terraform resources below provision the IAM and supporting infrastructure.
# The actual memory_id is created via the SDK and referenced in application config.

# --- AgentCore Runtime ---
# AgentCore Runtime is a managed service — agents are deployed via the
# bedrock-agentcore CLI toolkit or SDK. No Terraform resource needed for
# the runtime itself, only the container image and IAM role.

# ECR repository for the agent runtime container
resource "aws_ecr_repository" "agent_runtime" {
  count = var.agent_runtime_image_uri == "" ? 1 : 0

  name                 = "${local.prefix}-agent-runtime"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# CloudWatch log group for runtime logs
resource "aws_cloudwatch_log_group" "agentcore" {
  name              = "/agentcore/${local.prefix}"
  retention_in_days = 14
}
