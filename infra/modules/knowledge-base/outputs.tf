output "knowledge_base_id" {
  description = "ID of the Bedrock knowledge base"
  value       = aws_bedrockagent_knowledge_base.main.id
}

output "knowledge_base_arn" {
  description = "ARN of the Bedrock knowledge base"
  value       = aws_bedrockagent_knowledge_base.main.arn
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for KB documents"
  value       = aws_s3_bucket.kb_documents.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for KB documents"
  value       = aws_s3_bucket.kb_documents.arn
}

output "aurora_cluster_endpoint" {
  description = "Endpoint of the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.kb.endpoint
}

output "aurora_cluster_arn" {
  description = "ARN of the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.kb.arn
}
