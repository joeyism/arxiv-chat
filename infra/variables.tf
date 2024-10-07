variable "region" {
  description = "AWS region"
  default     = "ca-central-1"
}

variable "availability_zones" {
  description = "Availability Zone"
  type        = list(string)
  default     = ["ca-central-1a", "ca-central-1b"]
}

variable "subnet_cidrs" {
  description = "List of CIDR blocks for subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]  # Ensure these do not overlap
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  default     = "10.0.0.0/16"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend"
  default     = "paperchat.thedataloft.com"
}

variable "aws_profile" {
  type    = string
  default = ""
}

variable "postgres_password" {
  description = "Postgres password"
}

variable "key_pair_name" {
  description = "Name of the existing EC2 key pair"
  default     = "aws-thedataloft-canarie-joey"
}

