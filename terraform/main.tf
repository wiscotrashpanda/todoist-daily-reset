terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Local state for now
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "aws" {
  region = "us-east-1" # Defaulting to us-east-1, change if needed
}

variable "todoist_api_token" {
  type      = string
  sensitive = true
  default   = "changeme_in_console_or_env_var" 
}
