variable "project_id" {
  default     = "hsu-matthewnemeth-personal"
  description = "the gcp_name_short project where GKE creates the cluster"
}

variable "region" {
  default     = "us-west1"
  description = "the gcp_name_short region where GKE creates the cluster"
}

variable "zone" {
  default     = "us-west1-a"
  description = "the GPU nodes zone"
}

variable "cluster_name" {
  default     = "protein-server"
  description = "the name of the cluster"
}

variable "gpu_type" {
  default     = "nvidia-tesla-t4"
  description = "the GPU accelerator type"
}

variable "esm_inference_pool_name" {
  default     = "esm-inference-pool"
  description = "the name of the pool"
}

variable "frontend_pool_name" {
  default     = "frontend-pool"
  description = "the name of the pool"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_container_cluster" "ml_cluster" {
  name     = var.cluster_name
  location = var.region
  node_locations = [var.zone]
  remove_default_node_pool = true
  initial_node_count = 1

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  } 
}

resource "google_container_node_pool" "gpu_pool" {
  name       = var.esm_inference_pool_name
  location   = var.region
  cluster    = google_container_cluster.ml_cluster.name
  node_count = 1


  autoscaling {
    total_min_node_count = "0"
    total_max_node_count = "5"
  }

  management {
    auto_repair  = "true"
    auto_upgrade = "true"
  }

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/trace.append",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
    ]

    labels = {
      env = var.project_id
    }

    guest_accelerator {
      type  = var.gpu_type
      count = 1
    }

    image_type   = "cos_containerd"
    machine_type = "n1-highmem-8"
    tags         = ["gke-node", "${var.project_id}-gke"]

    disk_size_gb = "100"
    disk_type    = "pd-standard"

    metadata = {
      disable-legacy-endpoints = "true"
    }

    workload_metadata_config {
        mode = "GKE_METADATA"
    }
  }
}



resource "google_container_node_pool" "frontend_pool" {
  name       = var.frontend_pool_name
  location   = var.region
  cluster    = google_container_cluster.ml_cluster.name
  node_count = 1

  autoscaling {
    total_min_node_count = "0"
    total_max_node_count = "3"
  }

  management {
    auto_repair  = "true"
    auto_upgrade = "true"
  }

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/trace.append",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
    ]

    labels = {
      env = var.project_id
    }

    image_type   = "cos_containerd"
    machine_type = "e2-medium"
    tags         = ["gke-node", "${var.project_id}-gke"]

    disk_size_gb = "50"
    disk_type    = "pd-standard"

    metadata = {
      disable-legacy-endpoints = "true"
    }

    workload_metadata_config {
        mode = "GKE_METADATA"
    }
  }
}