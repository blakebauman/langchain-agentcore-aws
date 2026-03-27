variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "bedrock_model_arns" {
  description = "List of Bedrock model ARNs the agent is allowed to invoke"
  type        = list(string)
  default     = ["*"]
}

variable "s3_kb_bucket_arn" {
  description = "ARN of the S3 bucket used for knowledge base documents"
  type        = string
  default     = ""
}
