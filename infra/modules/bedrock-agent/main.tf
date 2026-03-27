locals {
  prefix = "${var.project_name}-${var.environment}"
}

resource "aws_bedrockagent_agent" "main" {
  agent_name              = "${local.prefix}-${var.agent_name}"
  agent_resource_role_arn = var.role_arn
  foundation_model        = var.foundation_model
  instruction             = var.instruction
  idle_session_ttl_in_seconds = var.idle_session_ttl
}

# Action group — connects Lambda tools to the agent
resource "aws_bedrockagent_agent_action_group" "main" {
  count = var.lambda_action_group_arn != "" ? 1 : 0

  agent_id          = aws_bedrockagent_agent.main.agent_id
  agent_version     = "DRAFT"
  action_group_name = "${local.prefix}-actions"

  action_group_executor {
    lambda = var.lambda_action_group_arn
  }

  api_schema {
    payload = jsonencode({
      openapi = "3.0.0"
      info = {
        title   = "${local.prefix} Action Group API"
        version = "1.0.0"
      }
      paths = {
        "/calculate" = {
          get = {
            summary     = "Evaluate a mathematical expression"
            operationId = "calculate"
            parameters = [
              {
                name        = "expression"
                in          = "query"
                description = "Mathematical expression to evaluate (e.g., '42 * 17')"
                required    = true
                schema      = { type = "string" }
              }
            ]
            responses = {
              "200" = {
                description = "Calculation result"
                content = {
                  "application/json" = {
                    schema = {
                      type = "object"
                      properties = {
                        result = { type = "string" }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        "/health" = {
          get = {
            summary     = "Health check"
            operationId = "healthCheck"
            responses = {
              "200" = {
                description = "Service is healthy"
              }
            }
          }
        }
      }
    })
  }
}

# Knowledge base association
resource "aws_bedrockagent_agent_knowledge_base_association" "main" {
  count = var.enable_knowledge_base ? 1 : 0

  agent_id             = aws_bedrockagent_agent.main.agent_id
  knowledge_base_id    = var.knowledge_base_id
  description          = "Knowledge base for ${local.prefix}"
  knowledge_base_state = "ENABLED"
}

# Agent alias for deployment
resource "aws_bedrockagent_agent_alias" "main" {
  agent_id         = aws_bedrockagent_agent.main.agent_id
  agent_alias_name = var.environment
}
