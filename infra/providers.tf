provider "google" {
  project = "hoehetis"
  region  = "europe-west1"
}

terraform {
  required_version = ">= 1.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.1.0"
    }
  }

  backend "gcs" {
    bucket = "hoehetis-terraform"
    prefix = "prod/state"
  }
}
