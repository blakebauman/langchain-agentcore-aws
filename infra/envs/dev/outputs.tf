output "bedrock_agent_id" {
  description = "ID of the deployed Bedrock agent"
  value       = module.bedrock_agent.agent_id
}

output "bedrock_agent_alias_id" {
  description = "Alias ID for invoking the agent"
  value       = module.bedrock_agent.agent_alias_id
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "chat_ecr_repository_url" {
  description = "ECR repository URL for the chat image"
  value       = aws_ecr_repository.chat.repository_url
}

output "chat_cluster_arn" {
  description = "ECS cluster ARN for the chat service"
  value       = module.chat.cluster_arn
}

output "chat_service_name" {
  description = "ECS service name for the chat service"
  value       = module.chat.service_name
}

output "chat_log_group" {
  description = "CloudWatch log group for the chat service"
  value       = module.chat.log_group_name
}

output "alb_dns_name" {
  description = "DNS name of the ALB"
  value       = module.chat.alb_dns_name
}

# Uncomment after enabling the Knowledge Base module:
# output "knowledge_base_id" {
#   description = "ID of the Bedrock knowledge base"
#   value       = module.knowledge_base.knowledge_base_id
# }
#
# output "kb_s3_bucket" {
#   description = "S3 bucket for knowledge base documents"
#   value       = module.knowledge_base.s3_bucket_name
# }
#
# output "aurora_cluster_endpoint" {
#   description = "Aurora PostgreSQL cluster endpoint"
#   value       = module.knowledge_base.aurora_cluster_endpoint
# }
