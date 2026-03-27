terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }

  # Uncomment after creating the state bucket and DynamoDB table:
  # backend "s3" {
  #   bucket         = "agentic-ai-tfstate-dev"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "agentic-ai-tfstate-lock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# --- IAM Roles ---

module "iam" {
  source = "../../modules/iam"

  project_name = var.project_name
  environment  = var.environment
}

# --- Knowledge Base ---
# Uncomment when ready for RAG (note: OpenSearch Serverless has ~$700/mo idle cost):

# module "knowledge_base" {
#   source = "../../modules/knowledge-base"
#
#   project_name     = var.project_name
#   environment      = var.environment
#   bedrock_role_arn = module.iam.bedrock_agent_role_arn
# }

# --- Lambda Action Group ---
# Uncomment after building the Lambda package (make build-lambda):

# module "action_group_lambda" {
#   source = "../../modules/lambda-action-group"
#
#   project_name  = var.project_name
#   environment   = var.environment
#   function_name = "action-group"
#   role_arn      = module.iam.lambda_role_arn
#   source_path   = var.lambda_source_path
# }

# --- Bedrock Agent ---

module "bedrock_agent" {
  source = "../../modules/bedrock-agent"

  project_name     = var.project_name
  environment      = var.environment
  foundation_model = var.foundation_model
  instruction      = var.agent_instruction
  role_arn         = module.iam.bedrock_agent_role_arn

  # Uncomment after enabling the Knowledge Base module above:
  # enable_knowledge_base = true
  # knowledge_base_id     = module.knowledge_base.knowledge_base_id

  # Uncomment after enabling the Lambda module above:
  # lambda_action_group_arn = module.action_group_lambda.function_arn
}

# --- AgentCore ---
# Uncomment to provision AgentCore infrastructure (IAM, ECR, logging):

# module "agentcore" {
#   source = "../../modules/agentcore"
#
#   project_name     = var.project_name
#   environment      = var.environment
#   foundation_model = var.foundation_model
#   enable_memory    = true
#   enable_gateway   = false
# }

# --- VPC (free) ---

module "vpc" {
  source = "../../modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  availability_zones = ["${var.aws_region}a", "${var.aws_region}b"]
}

# --- ECR Repository for Chat Image ---

resource "aws_ecr_repository" "chat" {
  name                 = "${var.project_name}-${var.environment}-chat"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- Chat Service (ECS Fargate) ---

module "chat" {
  source = "../../modules/chat"

  project_name     = var.project_name
  environment      = var.environment
  chat_image_uri   = "${aws_ecr_repository.chat.repository_url}:latest"
  vpc_id           = module.vpc.vpc_id
  subnet_ids       = module.vpc.public_subnet_ids
  bedrock_model_id = "us.${var.foundation_model}"
  chat_persistence = "sqlite"

  # No ALB for dev — access via ECS task public IP
  enable_alb = false
}
