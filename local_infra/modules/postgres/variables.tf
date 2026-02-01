variable "namespace" {
  type = string
  description = "Namespace to be deployed"
}

variable "db_name" {
  type = string
  description = "db name"
}

variable "db_user" {
  type = string
  description = "custom user"
}

variable "db_password" {
  type = string
  description = "custom user password"
}

variable "db_admin_password" {
  type = string
  description = "admin password"
}
