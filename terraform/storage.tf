resource "google_storage_bucket" "static" {
  name                        = var.bucket_name
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
}
