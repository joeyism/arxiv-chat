#resource "aws_elasticache_cluster" "paperchat" {
#  cluster_id      = "paperchat"
#  engine          = "redis"
#  node_type       = "cache.t3.micro"
#  num_cache_nodes = 1
#  port            = 6379 # Default Redis port
#
#  security_group_ids = [aws_security_group.redis_sg.id]
#}
#
#resource "aws_security_group" "redis_sg" {
#  name        = "redis_security_group"
#  description = "Allow access to Redis"
#  vpc_id      = aws_vpc.main.id # Replace with your VPC ID
#
#  ingress {
#    from_port       = 6379 # Redis default port
#    to_port         = 6379
#    protocol        = "tcp"
#    security_groups = [aws_security_group.allow_http.id]
#  }
#
#  egress {
#    from_port   = 0
#    to_port     = 0
#    protocol    = "-1"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#}
