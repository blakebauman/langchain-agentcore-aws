variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "bedrock_role_arn" {
  description = "ARN of the Bedrock agent IAM role"
  type        = string
}

variable "embedding_model_arn" {
  description = "ARN of the embedding model for the knowledge base"
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
}

variable "aurora_min_capacity" {
  description = "Minimum ACU capacity for Aurora Serverless v2 (0.5 = lowest)"
  type        = number
  default     = 0.5
}

variable "aurora_max_capacity" {
  description = "Maximum ACU capacity for Aurora Serverless v2"
  type        = number
  default     = 4
}

variable "db_name" {
  description = "Name of the PostgreSQL database for the knowledge base"
  type        = string
  default     = "bedrock_kb"
}
