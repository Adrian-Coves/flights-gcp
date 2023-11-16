variable "project" {
  type    = string
  default = "flights-de"
}

variable "region" {
  type    = string
  default = "europe-southwest1"
}

variable "zone" {
  type    = string
  default = "europe-southwest1-a"
}

variable "bucket_name" {
  type    = string
  default = "flights-acj"
}

variable "python_version" {
  type    = string
  default = "python311"
}

variable "service_account" {
  type    = string
  default = "flight-tf@flights-de.iam.gserviceaccount.com"

}
