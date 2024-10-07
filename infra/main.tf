terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70.0" # Adjust the version as needed
    }
  }
}


provider "aws" {
  region  = var.region
  profile = var.aws_profile
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
}

resource "aws_subnet" "main" {
  count      = length(var.availability_zones)
  vpc_id     = aws_vpc.main.id
  cidr_block = element(var.subnet_cidrs, count.index) # Use predefined CIDR blocks

  availability_zone = element(var.availability_zones, count.index)

  tags = {
    Name = "PaperchatSubnet-${count.index}"
  }
}

resource "aws_security_group" "allow_http" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "backend" {
  ami                         = "ami-08add6b727bde335a"
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.main[0].id # Reference a specific subnet
  security_groups             = [aws_security_group.allow_http.id]
  key_name                    = var.key_pair_name
  associate_public_ip_address = true

  tags = {
    Name = "PaperChat"
  }

  user_data = <<-EOF
              #!/bin/bash
              git clone https://github.com/joeyism/arxiv-chat.git
              cd arxiv-chat
              pip install -r requirements.txt
              gunicorn app:app --bind 0.0.0.0:80
              EOF

  lifecycle {
    ignore_changes = [user_data, security_groups]
  }
}

resource "aws_s3_bucket" "frontend" {
  bucket = var.frontend_bucket_name
}

resource "aws_s3_object" "frontend_files" {
  bucket = aws_s3_bucket.frontend.id
  key    = "index.html"                             # Update as necessary
  source = "../arxiv-chat-frontend/dist/index.html" # Path to your frontend build
}


resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.main[0].id  # Associate with your public subnet
  route_table_id = aws_route_table.public.id
}
