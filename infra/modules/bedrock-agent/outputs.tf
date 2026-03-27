output "agent_id" {
  description = "ID of the Bedrock agent"
  value       = aws_bedrockagent_agent.main.agent_id
}

output "agent_arn" {
  description = "ARN of the Bedrock agent"
  value       = aws_bedrockagent_agent.main.agent_arn
}

output "agent_alias_id" {
  description = "ID of the agent alias"
  value       = aws_bedrockagent_agent_alias.main.agent_alias_id
}
