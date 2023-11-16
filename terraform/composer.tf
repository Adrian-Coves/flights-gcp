resource "google_composer_environment" "composer" {
  name   = "composer"
  region = var.region
  config {
    node_config {
      service_account = var.service_account

    }
    software_config {
      airflow_config_overrides = {
        core-dags_are_paused_at_creation = "True",
      }

    }

  }
}


resource "null_resource" "upload_directory" {
  triggers = {
    source_files = "../airflow/dags"
  }
  provisioner "local-exec" {
    command = <<-EOT
      gsutil -m cp -r ../airflow/dags/* ${google_composer_environment.composer.config.0.dag_gcs_prefix}
    EOT
  }
}

