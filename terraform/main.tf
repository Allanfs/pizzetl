terraform {
  required_providers {
    archive = {
      source = "hashicorp/archive"
    }

    google = {
      source  = "hashicorp/google"
      version = ">= 6.14.1"
    }
  }
}


# Compactar projeto

resource "archive_file" "init" {
  type        = "zip"
  source_dir  = "${path.module}/.."
  output_path = "${path.module}/project.zip"
}

# ------------------------------------------------------

# Preparar Cloud Function

resource "google_storage_bucket" "bucket" {
  name                        = "${var.gcp_project}-pizzetl-gcf-source" # Every bucket name must be globally unique
  location                    = "US"                                    # southamerica-east1
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "object" {
  name   = "pizzetl-function-source.zip"
  bucket = google_storage_bucket.bucket.name
  source = archive_file.init.output_path
}

resource "google_cloudfunctions2_function" "function" {
  project     = var.gcp_project
  name        = "${var.customer}-consolidador-pedidos"
  location    = var.gcp_region
  description = "Responsável por estruturar pedidos do instadelivery e querodelivery para o Bigquery"

  build_config {
    runtime     = "python39"
    entry_point = "consolidar_plataformas" # Set the entry point 
    environment_variables = {
      DESTINATION_TABLE_CONSOLIDADOR_PLATAFORMAS = var.destination_table_consolidador,
      PROJECT_ID                                 = var.gcp_project
    }

    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "512M"
    timeout_seconds    = 60
  }

  event_trigger {
    trigger_region = var.gcp_region
    event_type     = "google.cloud.storage.object.v1.finalized"
    retry_policy   = "RETRY_POLICY_RETRY"
    event_filters {
      attribute = "bucket"
      value     = var.trigger_bucket
    }
  }
}
