
data "google_client_config" "this" {}

# data "google_artifact_registry_repository" "extract" {
#   location      = data.google_client_config.this.region
#   repository_id = "extract"
# }

# # Latest extract image as a google cloud run deployment
# resource "google_cloud_run_service" "extract" {
#   name     = "extract"
#   location = data.google_client_config.this.region

#   template {
#     spec {
#       containers {
#         image = data.google_artifact_registry_repository.extract.location
#       }
#     }
#   }
# }

resource "google_bigquery_dataset" "default" {
  dataset_id                  = "base"
  location                    = "EU"
}


resource "google_bigquery_table" "news" {
  dataset_id = google_bigquery_dataset.default.dataset_id
  table_id   = "news"
}
