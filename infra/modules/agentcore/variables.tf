variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "enable_memory" {
  description = "Enable AgentCore Memory resources"
  type        = bool
  default     = true
}

variable "enable_gateway" {
  description = "Enable AgentCore Gateway resources"
  type        = bool
  default     = false
}

variable "agent_runtime_image_uri" {
  description = "ECR image URI for the agent runtime container"
  type        = string
  default     = ""
}

variable "foundation_model" {
  description = "Bedrock foundation model identifier"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-20250514-v1:0"
}
