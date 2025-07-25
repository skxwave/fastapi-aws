variable "aws_region" {
  description = "AWS region to deploy to"
  default     = "us-east-1"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  default     = "ami-0c02fb55956c7d316" # Amazon Linux 2 AMI (HVM), SSD Volume Type for us-east-1
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}
