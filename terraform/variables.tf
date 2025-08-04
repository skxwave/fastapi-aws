variable "db_name" {
  default = "fastapidb"
}

variable "db_user" {
  default = "fastapi"
}

variable "db_password" {
  sensitive = true
}
