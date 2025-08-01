output "ec2_public_ip" {
  value = aws_instance.fastapi_server.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}
