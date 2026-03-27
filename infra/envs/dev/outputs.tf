output "bedrock_agent_id" {
  description = "ID of the deployed Bedrock agent"
  value       = module.bedrock_agent.agent_id
}

output "bedrock_agent_alias_id" {
  description = "Alias ID for invoking the agent"
  value       = module.bedrock_agent.agent_alias_id
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
