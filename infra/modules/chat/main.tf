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

  # Secrets Manager read access (when secrets_arn is provided)
  dynamic "statement" {
    for_each = var.secrets_arn != "" ? [1] : []
    content {
      sid    = "SecretsManagerRead"
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue",
      ]
      resources = [var.secrets_arn]
    }
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

# --- Security Groups ---

resource "aws_security_group" "chat" {
  name_prefix = "${local.prefix}-chat-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.chat_port
    to_port         = var.chat_port
    protocol        = "tcp"
    cidr_blocks     = var.enable_alb ? [] : ["0.0.0.0/0"]
    security_groups = var.enable_alb ? [aws_security_group.alb[0].id] : []
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

resource "aws_security_group" "alb" {
  count       = var.enable_alb ? 1 : 0
  name_prefix = "${local.prefix}-chat-alb-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
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

# --- Application Load Balancer (optional) ---

resource "aws_lb" "chat" {
  count              = var.enable_alb ? 1 : 0
  name               = "${local.prefix}-chat"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb[0].id]
  subnets            = var.public_subnet_ids

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "chat" {
  count       = var.enable_alb ? 1 : 0
  name        = "${local.prefix}-chat"
  port        = var.chat_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# HTTPS listener (port 443)
resource "aws_lb_listener" "https" {
  count             = var.enable_alb ? 1 : 0
  load_balancer_arn = aws_lb.chat[0].arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.chat[0].arn
  }
}

# HTTP → HTTPS redirect
resource "aws_lb_listener" "http_redirect" {
  count             = var.enable_alb ? 1 : 0
  load_balancer_arn = aws_lb.chat[0].arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
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
      environment = concat(
        [
          { name = "BEDROCK_MODEL_ID", value = var.bedrock_model_id },
          { name = "AWS_REGION", value = data.aws_region.current.name },
          { name = "ENVIRONMENT", value = var.environment },
          { name = "CHAT_PORT", value = tostring(var.chat_port) },
          { name = "CHAT_PERSISTENCE", value = var.chat_persistence },
          { name = "CHAT_AUTH_SECRET", value = var.chat_auth_secret },
          { name = "AGENTCORE_OBSERVABILITY_ENABLED", value = tostring(var.enable_observability) },
          { name = "AGENTCORE_AGENT_NAME", value = var.project_name },
        ],
        var.secrets_arn != "" ? [{ name = "SECRETS_ARN", value = var.secrets_arn }] : [],
      )
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.chat_port}/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
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

  dynamic "load_balancer" {
    for_each = var.enable_alb ? [1] : []
    content {
      target_group_arn = aws_lb_target_group.chat[0].arn
      container_name   = "chat"
      container_port   = var.chat_port
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
