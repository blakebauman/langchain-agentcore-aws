variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "chat_image_uri" {
  description = "ECR image URI for the chat container"
  type        = string
}

variable "chat_port" {
  description = "Port the chat service listens on"
  type        = number
  default     = 8000
}

variable "cpu" {
  description = "Fargate task CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
}

variable "memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Number of chat service tasks to run"
  type        = number
  default     = 1
}

variable "vpc_id" {
  description = "VPC ID for the chat service"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the chat service"
  type        = list(string)
}

variable "bedrock_model_id" {
  description = "Bedrock model ID for the chat agent"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-20250514-v1:0"
}

variable "chat_auth_secret" {
  description = "Secret for JWT signing (enables authentication)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "chat_persistence" {
  description = "Chat persistence mode (memory, sqlite)"
  type        = string
  default     = "sqlite"
}
