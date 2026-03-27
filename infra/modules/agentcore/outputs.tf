output "agentcore_role_arn" {
  description = "ARN of the AgentCore IAM role"
  value       = aws_iam_role.agentcore.arn
}

output "agentcore_role_name" {
  description = "Name of the AgentCore IAM role"
  value       = aws_iam_role.agentcore.name
}

output "ecr_repository_url" {
  description = "ECR repository URL for the agent runtime container"
  value       = length(aws_ecr_repository.agent_runtime) > 0 ? aws_ecr_repository.agent_runtime[0].repository_url : var.agent_runtime_image_uri
}

output "log_group_name" {
  description = "CloudWatch log group for AgentCore"
  value       = aws_cloudwatch_log_group.agentcore.name
}
