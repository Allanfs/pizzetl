variable "gcp_svc_key" {}

variable "gcp_project" {}

variable "gcp_region" {}

variable "customer" {}

# ------------------------------------------------------------------#

variable "destination_table_consolidador" {
  type        = string
  description = "tabela que serão armazenados os dados consolidados"
}

variable "trigger_bucket" {
  type        = string
  description = "bucket que a function estará ouvindo para iniciar o processamento"
}