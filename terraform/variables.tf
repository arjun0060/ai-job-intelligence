variable "aws_region" {
  description = "AWS region where the infrastructure will be deployed."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name of the project."
  type        = string
  default     = "ai-job-intelligence"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for the application VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones used by the application."
  type        = list(string)
  default = [
    "ap-south-1a",
    "ap-south-1b"
  ]
}

variable "ec2_instance_type" {
  description = "EC2 instance type for the application server."
  type        = string
  default     = "t3.micro"
}

variable "rds_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "database_name" {
  description = "Application database name."
  type        = string
  default     = "job_intelligence"
}

variable "database_username" {
  description = "PostgreSQL username."
  type        = string
  default     = "job_admin"
}

variable "database_password" {
  description = "PostgreSQL password."
  type        = string
  sensitive   = true
}

variable "admin_cidr" {
  description = "CIDR block allowed to access EC2 over SSH."
  type        = string
}