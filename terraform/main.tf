terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.14.1"
    }
  }

  cloud {
    organization = "emkaytec"

    workspaces {
      name = "todoist-daily-reset"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "todoist-daily-reset"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
