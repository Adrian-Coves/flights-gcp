resource "google_storage_bucket_object" "url_to_bucket" {
  name       = "cloud_functions/url_to_bucket.zip"
  bucket     = google_storage_bucket.static.name
  source     = "/tmp/url_to_bucket.zip"
  depends_on = [data.archive_file.url_to_bucket]
}

data "archive_file" "url_to_bucket" {
  type        = "zip"
  output_path = "/tmp/url_to_bucket.zip"
  source_dir  = "../cloud_functions/url_to_bucket"
}

resource "google_cloudfunctions2_function" "url_to_bucket" {
  name        = "url_to_bucket"
  location    = var.region
  description = "Store file from URL to bucket"
  depends_on  = [google_storage_bucket_object.url_to_bucket]
  build_config {
    runtime     = var.python_version
    entry_point = "url_to_bucket"
    source {
      storage_source {
        bucket = google_storage_bucket.static.name
        object = "cloud_functions/url_to_bucket.zip"
      }
    }
  }
  service_config {
    max_instance_count    = 100
    available_memory      = "2Gi"
    timeout_seconds       = 600
    service_account_email = var.service_account

  }
}

resource "google_storage_bucket_object" "openskynet_pos" {
  name       = "cloud_functions/openskynet_pos.zip"
  bucket     = google_storage_bucket.static.name
  source     = "/tmp/openskynet_pos.zip"
  depends_on = [data.archive_file.openskynet_pos]
}

data "archive_file" "openskynet_pos" {
  type        = "zip"
  output_path = "/tmp/openskynet_pos.zip"
  source_dir  = "../cloud_functions/openskynet_pos"
}

resource "google_cloudfunctions2_function" "openskynet_pos" {
  name        = "openskynet_pos"
  location    = var.region
  description = "Call openskynet API"
  depends_on  = [google_storage_bucket_object.openskynet_pos]
  build_config {
    runtime     = var.python_version
    entry_point = "call_api"
    source {
      storage_source {
        bucket = google_storage_bucket.static.name
        object = "cloud_functions/openskynet_pos.zip"
      }
    }
  }
  service_config {
    max_instance_count    = 100
    available_memory      = "2Gi"
    timeout_seconds       = 600
    service_account_email = var.service_account

  }
}

