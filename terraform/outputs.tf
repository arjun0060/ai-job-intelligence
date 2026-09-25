output "vpc_id" {
  description = "ID of the application VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets."
  value       = aws_subnet.private[*].id
}

output "ec2_instance_id" {
  description = "ID of the application EC2 instance."
  value       = aws_instance.app.id
}

output "ec2_public_ip" {
  description = "Public IP address of the application EC2 instance."
  value       = aws_instance.app.public_ip
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint."
  value       = aws_db_instance.postgres.address
}

output "s3_bucket_name" {
  description = "S3 bucket used by the application."
  value       = aws_s3_bucket.app.bucket
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}