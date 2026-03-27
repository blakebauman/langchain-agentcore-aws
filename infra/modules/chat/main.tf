data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  prefix = "${var.project_name}-${var.environment}"
}

# --- IAM Role for ECS Task ---

data "aws_iam_policy_document" "task_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "chat_task" {
  name               = "${local.prefix}-chat-task"
  assume_role_policy = data.aws_iam_policy_document.task_trust.json

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

data "aws_iam_policy_document" "chat_permissions" {
  statement {
    sid    = "BedrockInvoke"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "chat_bedrock" {
  name   = "${local.prefix}-chat-bedrock"
  role   = aws_iam_role.chat_task.id
  policy = data.aws_iam_policy_document.chat_permissions.json
}

# ECS task execution role (for pulling images and logging)
resource "aws_iam_role" "chat_execution" {
  name               = "${local.prefix}-chat-execution"
  assume_role_policy = data.aws_iam_policy_document.task_trust.json

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "chat_execution" {
  role       = aws_iam_role.chat_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# --- CloudWatch Logs ---

resource "aws_cloudwatch_log_group" "chat" {
  name              = "/ecs/${local.prefix}-chat"
  retention_in_days = 14

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- ECS Cluster ---

resource "aws_ecs_cluster" "chat" {
  name = "${local.prefix}-chat"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- Security Group ---

resource "aws_security_group" "chat" {
  name_prefix = "${local.prefix}-chat-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = var.chat_port
    to_port     = var.chat_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- ECS Task Definition ---

resource "aws_ecs_task_definition" "chat" {
  family                   = "${local.prefix}-chat"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.chat_execution.arn
  task_role_arn            = aws_iam_role.chat_task.arn

  container_definitions = jsonencode([
    {
      name      = "chat"
      image     = var.chat_image_uri
      essential = true
      portMappings = [
        {
          containerPort = var.chat_port
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "BEDROCK_MODEL_ID", value = var.bedrock_model_id },
        { name = "AWS_REGION", value = data.aws_region.current.name },
        { name = "ENVIRONMENT", value = var.environment },
        { name = "CHAT_PORT", value = tostring(var.chat_port) },
        { name = "CHAT_PERSISTENCE", value = var.chat_persistence },
        { name = "CHAT_AUTH_SECRET", value = var.chat_auth_secret },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.chat.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "chat"
        }
      }
    }
  ])

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- ECS Service ---

resource "aws_ecs_service" "chat" {
  name            = "${local.prefix}-chat"
  cluster         = aws_ecs_cluster.chat.id
  task_definition = aws_ecs_task_definition.chat.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.chat.id]
    assign_public_ip = true
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
