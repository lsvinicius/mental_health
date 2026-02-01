resource "helm_release" "postgres_db" {
  name             = "mental-health-db"
  repository       = "bitnami"
  chart            = "postgresql"
  version          = "18.2.3"
  namespace        = var.namespace

  set = [
  {
    name  = "global.postgresql.auth.database"
    value = var.db_name
  }, {
    name  = "global.postgresql.auth.username"
    value = var.db_user
  },{
    name  = "global.postgresql.auth.password"
    value = var.db_password
  },
  {
    name  = "global.postgresql.auth.postgresPassword"
    value = var.db_admin_password
  }
    ]
}
