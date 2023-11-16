# Terraform Resources Overview

This Terraform configuration defines the infrastructure for a Flight Data Engineering project on Google Cloud Platform (GCP). The resources provisioned include storage buckets, Cloud Functions, Dataproc cluster, and Google Cloud Composer environment.

## [Terraform Configuration](./main.tf)

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}
```

## [Provider Configuration](./provider.tf)

- **Provider:** `google`
  - **Credentials:** Loaded from the file "flights-de-tf-credentials.json"
  - **Project:** `var.project`
  - **Region:** `var.region`
  - **Zone:** `var.zone`

## [Storage Bucket and Objects](./storage.tf)

### `google_storage_bucket` - `static`

Despite objects descriptions being here the source code is on the module they're related

- **Purpose:** Storage bucket for project data.
- **Configuration:**
  - Bucket Name: `var.bucket_name`
  - Location: `var.region`
  - Storage Class: STANDARD
  - Uniform Bucket Level Access: Enabled

### `google_storage_bucket_object` - `url_to_bucket`

- **Purpose:** Cloud Function code to download url data to a bucket.
- **Source:** `../cloud_functions/url_to_bucket`

### `google_storage_bucket_object` - `openskynet_pos`

- **Purpose:** Cloud Function code to call an external API.
- **Source:** `../cloud_functions/openskynet_pos`

### `google_storage_bucket_object` - `dataproc_scripts`

- **Purpose:** Dataproc script for processing departure and arrival data.
- **Source:** `../dataproc_scripts/departures_arrivals_csv.py`

## [Cloud Functions](./cloudfunctions.tf)

### `google_cloudfunctions2_function` - `url_to_bucket` and `openskynet_pos`

- **Purpose:** Cloud functions to download url data to a bucket and to call an external API.
- **Configuration:**
  - URL-to-Bucket Function:
    - Runtime: `var.python_version`
    - Entry Point: `url_to_bucket`
  - Openskynet Position Function:
    - Runtime: `var.python_version`
    - Entry Point: `call_api`
  - Common Configuration:
    - Location: `var.region`
    - Max Instance Count: 100
    - Available Memory: 2Gi
    - Timeout: 600 seconds
    - Service Account: `var.service_account`

## [Google Cloud Composer (Airflow)](./composer.tf)

### `google_composer_environment` - `composer`

- **Purpose:** Google Cloud Composer environment for Apache Airflow.
- **Configuration:**
  - Name: `composer`
  - Region: `var.region`
  - Node Configuration:
    - Service Account: `var.service_account`
  - Software Configuration:
    - Airflow Config Overrides:
      - `core-dags_are_paused_at_creation`: True

### `null_resource` - `upload_directory`

- **Purpose:** Upload dags from local project to the dags folder in Composer.
- **Requirements:** gsutil installed in local

## [Dataproc Cluster](./dataproc.tf)

### `google_dataproc_cluster` - `mycluster`

- **Purpose:** Dataproc cluster for PySpark data processing.
- **Configuration:**
  - Name: `spark-cluster-tf`
  - Region: `var.region`
  - Master Configuration:
    - Machine Type: `n2-standard-2`
    - Boot Disk Type: pd-ssd, Boot Disk Size: 30GB
  - Worker Configuration:
    - Machine Type: `n2-standard-2`
    - Boot Disk Size: 30GB, Num Local SSDs: 1
  - Preemptible Worker Configuration: Disabled
  - Software Configuration:
    - Image Version: 2.1.22-debian11
    - Allow Zero Workers Property: True
