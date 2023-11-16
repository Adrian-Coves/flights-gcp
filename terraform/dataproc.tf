resource "google_storage_bucket_object" "dataproc_scripts" {
  name         = "dataproc_scripts/departures_arrivals_csv.py"
  source       = "../dataproc_scripts/departures_arrivals_csv.py"
  content_type = "application/octet-stream"
  bucket       = google_storage_bucket.static.id
}

resource "google_dataproc_cluster" "mycluster" {
  name                          = "spark-cluster-tf"
  region                        = var.region
  graceful_decommission_timeout = "120s"
  cluster_config {
    endpoint_config {
      enable_http_port_access = "true"
    }
    master_config {
      num_instances = 1
      machine_type  = "n2-standard-2"
      disk_config {
        boot_disk_type    = "pd-ssd"
        boot_disk_size_gb = 30
      }
    }
    worker_config {
      num_instances    = 2
      machine_type     = "n2-standard-2"
      min_cpu_platform = "Intel Cascade Lake"
      disk_config {
        boot_disk_size_gb = 30
        num_local_ssds    = 1
      }
    }
    preemptible_worker_config {
      num_instances = 0
    }
    software_config {
      image_version = "2.1.22-debian11"
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }

  }
}
