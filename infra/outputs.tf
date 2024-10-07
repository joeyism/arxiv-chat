output "backend_instance_public_ip" {
  value = aws_instance.backend.public_ip
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend.bucket
}

output "db_endpoint" {
  value = aws_db_instance.paperchat.endpoint
}
