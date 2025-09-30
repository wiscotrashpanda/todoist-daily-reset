variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "todoist_api_token" {
  description = "Todoist API token for accessing tasks"
  type        = string
  sensitive   = true
}

variable "timezone" {
  description = "Timezone for task processing (e.g., America/New_York, UTC)"
  type        = string
  default     = "UTC"
}

variable "schedule_expression" {
  description = "CloudWatch Events schedule expression for Lambda execution"
  type        = string
  default     = "cron(0 1 * * ? *)" # Run daily at 1 AM UTC
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 128
}
