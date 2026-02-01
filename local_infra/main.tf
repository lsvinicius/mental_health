provider "helm" {
  kubernetes = {
    config_path = "~/.kube/config"
  }
}
provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}

resource "kubernetes_namespace_v1" "k8s_namespace" {
  metadata {
    name = "local"
  }
}

locals {
  db_user = "mental_health_user"
  db_name = "mental_health_db"
  db_host = "mental-health-db-postgresql"
  db_port = 5432
}

module "postgres" {
  source = "./modules/postgres"
  namespace = kubernetes_namespace_v1.k8s_namespace.metadata[0].name

  db_admin_password = var.admin_password
  db_name           = local.db_name
  db_password       = var.mental_health_user_password
  db_user           = local.db_user
}

resource "helm_release" "mental_health" {
  name       = "mental-health"
  chart      = "../charts/mental_health"
  namespace  = kubernetes_namespace_v1.k8s_namespace.metadata[0].name
  depends_on = [
    module.postgres
  ]
  set_sensitive = [
    {
      name  = "mentalhealth.db_connection_string"
      value = "postgresql+asyncpg://${local.db_user}:${var.mental_health_user_password}@${local.db_host}:${local.db_port}/${local.db_name}"
    },
    {
      name  = "mentalhealth.google_api_key"
      value = var.google_api_key
    }
  ]
}
