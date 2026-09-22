provider "aws" {
  region  = var.aws_region
  profile = "ai-job-intelligence"

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}