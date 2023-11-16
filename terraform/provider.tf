provider "google" {
  credentials = file("flights-de-tf-credentials.json")

  project = var.project
  region  = var.region
  zone    = var.zone
}
