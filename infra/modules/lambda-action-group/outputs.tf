output "function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.action_group.arn
}

output "function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.action_group.function_name
}

output "invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = aws_lambda_function.action_group.invoke_arn
}
