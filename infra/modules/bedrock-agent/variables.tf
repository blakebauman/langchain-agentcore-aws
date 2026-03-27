variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "agent_name" {
  description = "Name of the Bedrock agent"
  type        = string
  default     = "assistant"
}

variable "foundation_model" {
  description = "Bedrock foundation model identifier"
  type        = string
  default     = "anthropic.claude-sonnet-4-20250514-v1:0"
}

variable "instruction" {
  description = "Instructions for the Bedrock agent"
  type        = string
  default     = "You are a helpful AI assistant. Use your tools to answer questions accurately and thoroughly."
}

variable "role_arn" {
  description = "ARN of the Bedrock agent execution role"
  type        = string
}

variable "lambda_action_group_arn" {
  description = "ARN of the Lambda function for the action group"
  type        = string
  default     = ""
}

variable "enable_knowledge_base" {
  description = "Whether to associate a knowledge base with the agent"
  type        = bool
  default     = false
}

variable "knowledge_base_id" {
  description = "ID of the Bedrock knowledge base to associate"
  type        = string
  default     = ""
}

variable "idle_session_ttl" {
  description = "Idle session TTL in seconds"
  type        = number
  default     = 600
}
