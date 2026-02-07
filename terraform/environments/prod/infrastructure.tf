# ─────────────────────────────────────────────────────────
# Infrastructure Modules Composition
# ─────────────────────────────────────────────────────────

# ── VPC ──────────────────────────────────────────────────
module "vpc" {
  source = "../../modules/vpc"

  cluster_name = var.cluster_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  aws_region   = var.aws_region
}

# ── EKS Cluster ─────────────────────────────────────────
module "eks" {
  source = "../../modules/eks"

  cluster_name        = var.cluster_name
  cluster_version     = var.cluster_version
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  node_instance_types = var.node_instance_types
  node_desired_size   = var.node_desired_size
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size
}

# ── IAM Roles (IRSA) ───────────────────────────────────
module "iam" {
  source = "../../modules/iam"

  cluster_name            = var.cluster_name
  environment             = var.environment
  oidc_provider_arn       = module.eks.oidc_provider_arn
  oidc_provider_url       = module.eks.oidc_provider_url
}

# ── RDS PostgreSQL ──────────────────────────────────────
module "rds" {
  source = "../../modules/rds"

  cluster_name       = var.cluster_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  db_instance_class  = var.db_instance_class
  eks_security_group_id = module.eks.node_security_group_id
}

# ─────────────────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────────────────
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "database_endpoint" {
  value     = module.rds.db_endpoint
  sensitive = true
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

# ECR Repository
resource "aws_ecr_repository" "app" {
  name                 = "${var.cluster_name}/api"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 20 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 20
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
