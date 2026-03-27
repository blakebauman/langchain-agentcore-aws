locals {
  prefix = "${var.project_name}-${var.environment}"
}

resource "aws_lambda_function" "action_group" {
  function_name = "${local.prefix}-${var.function_name}"
  role          = var.role_arn
  handler       = var.handler
  runtime       = var.runtime
  timeout       = var.timeout
  memory_size   = var.memory_size
  filename      = var.source_path

  source_code_hash = filebase64sha256(var.source_path)

  environment {
    variables = merge(
      {
        ENVIRONMENT = var.environment
        LOG_LEVEL   = "INFO"
      },
      var.environment_variables,
    )
  }
}

resource "aws_lambda_permission" "bedrock" {
  statement_id  = "AllowBedrockInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.action_group.function_name
  principal     = "bedrock.amazonaws.com"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.action_group.function_name}"
  retention_in_days = var.log_retention_days
}
