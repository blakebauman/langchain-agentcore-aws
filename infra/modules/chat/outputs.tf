output "cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.chat.arn
}

output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.chat.name
}

output "task_role_arn" {
  description = "ARN of the task IAM role"
  value       = aws_iam_role.chat_task.arn
}

output "security_group_id" {
  description = "ID of the chat service security group"
  value       = aws_security_group.chat.id
}

output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.chat.name
}

output "alb_dns_name" {
  description = "DNS name of the ALB (empty when ALB is disabled)"
  value       = var.enable_alb ? aws_lb.chat[0].dns_name : ""
}

output "alb_arn" {
  description = "ARN of the ALB (empty when ALB is disabled)"
  value       = var.enable_alb ? aws_lb.chat[0].arn : ""
}
