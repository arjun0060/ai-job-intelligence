resource "aws_db_subnet_group" "postgres" {
  name = "${var.project_name}-postgres"

  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-postgres"
  }
}

resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-postgres"

  engine         = "postgres"
  engine_version = "16"

  instance_class        = var.rds_instance_class
  allocated_storage     = 20
  max_allocated_storage = 20
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.database_username
  password = var.database_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false

  backup_retention_period = 0
  skip_final_snapshot     = true

  deletion_protection = false

  tags = {
    Name = "${var.project_name}-postgres"
  }
}