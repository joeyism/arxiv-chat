resource "aws_db_instance" "paperchat" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "16.4"
  instance_class         = "db.t3.micro"
  db_name                = "postgres"
  username               = "postgres"
  password               = var.postgres_password
  db_subnet_group_name   = aws_db_subnet_group.paperchat_subnet_group.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  # Allowing connections from the EC2 instance
  skip_final_snapshot = true

  tags = {
    Name = "Paperchat"
  }
}


resource "aws_db_subnet_group" "paperchat_subnet_group" {
  name       = "paperchat-subnet-group"
  subnet_ids = aws_subnet.main[*].id  # Use all created subnets

  tags = {
    Name = "PaperchatSubnetGroup"
  }
}


resource "aws_security_group" "db_sg" {
  name        = "paperchat_db_security_group"
  description = "Allow access to RDS"
  vpc_id      = aws_vpc.main.id # Replace with your VPC ID

  ingress {
    from_port       = 5432 # PostgreSQL default port
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.allow_http.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
