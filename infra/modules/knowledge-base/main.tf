data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  prefix = "${var.project_name}-${var.environment}"
}

# --- S3 Bucket for Knowledge Base Documents ---

resource "aws_s3_bucket" "kb_documents" {
  bucket = "${local.prefix}-kb-documents"
}

resource "aws_s3_bucket_versioning" "kb_documents" {
  bucket = aws_s3_bucket.kb_documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "kb_documents" {
  bucket = aws_s3_bucket.kb_documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "kb_documents" {
  bucket = aws_s3_bucket.kb_documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Aurora Serverless v2 PostgreSQL (pgvector) ---

resource "aws_rds_cluster" "kb" {
  cluster_identifier = "${local.prefix}-kb"
  engine             = "aurora-postgresql"
  engine_mode        = "provisioned"
  engine_version     = "16.6"
  database_name      = var.db_name
  master_username    = "bedrock_admin"

  manage_master_user_password = true

  serverlessv2_scaling_configuration {
    min_capacity = var.aurora_min_capacity
    max_capacity = var.aurora_max_capacity
  }

  storage_encrypted   = true
  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "${local.prefix}-kb"
  }
}

resource "aws_rds_cluster_instance" "kb" {
  identifier         = "${local.prefix}-kb-instance"
  cluster_identifier = aws_rds_cluster.kb.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.kb.engine
  engine_version     = aws_rds_cluster.kb.engine_version

  tags = {
    Name = "${local.prefix}-kb-instance"
  }
}

# --- IAM policy for Bedrock to access Aurora ---

data "aws_iam_policy_document" "bedrock_rds" {
  statement {
    sid    = "AuroraAccess"
    effect = "Allow"
    actions = [
      "rds-data:ExecuteStatement",
      "rds-data:BatchExecuteStatement",
      "rds:DescribeDBClusters",
    ]
    resources = [aws_rds_cluster.kb.arn]
  }

  statement {
    sid    = "SecretsAccess"
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
    ]
    resources = [aws_rds_cluster.kb.master_user_secret[0].secret_arn]
  }
}

resource "aws_iam_role_policy" "bedrock_rds" {
  name   = "${local.prefix}-bedrock-rds"
  role   = regex("[^/]+$", var.bedrock_role_arn)
  policy = data.aws_iam_policy_document.bedrock_rds.json
}

# --- Bedrock Knowledge Base (Aurora PostgreSQL) ---

resource "aws_bedrockagent_knowledge_base" "main" {
  name     = "${local.prefix}-kb"
  role_arn = var.bedrock_role_arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = var.embedding_model_arn
    }
  }

  storage_configuration {
    type = "RDS"
    rds_configuration {
      credentials_secret_arn = aws_rds_cluster.kb.master_user_secret[0].secret_arn
      database_name          = var.db_name
      resource_arn           = aws_rds_cluster.kb.arn
      table_name             = "bedrock_integration.bedrock_kb"
      field_mapping {
        primary_key_field = "id"
        vector_field      = "embedding"
        text_field        = "chunks"
        metadata_field    = "metadata"
      }
    }
  }

  depends_on = [
    aws_rds_cluster_instance.kb,
    aws_iam_role_policy.bedrock_rds,
  ]
}

resource "aws_bedrockagent_data_source" "s3" {
  name                 = "${local.prefix}-kb-s3"
  knowledge_base_id    = aws_bedrockagent_knowledge_base.main.id
  data_deletion_policy = "RETAIN"

  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.kb_documents.arn
    }
  }
}
