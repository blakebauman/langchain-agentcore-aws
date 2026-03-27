variable "project_name" {
  description = "Project name"
  type        = string
  default     = "agentic-ai"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "foundation_model" {
  description = "Bedrock foundation model for the agent"
  type        = string
  default     = "anthropic.claude-sonnet-4-20250514-v1:0"
}

variable "agent_instruction" {
  description = "Instructions for the Bedrock agent"
  type        = string
  default     = "You are a helpful AI assistant. Use your tools to answer questions accurately and thoroughly."
}

variable "lambda_source_path" {
  description = "Path to the Lambda deployment package"
  type        = string
  default     = "../../../dist/lambda.zip"
}
