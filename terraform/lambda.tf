# ECR Repository for Lambda container images
resource "aws_ecr_repository" "todoist_daily_reset" {
  name                 = "todoist-daily-reset"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle_policy {
    policy = jsonencode({
      rules = [
        {
          rulePriority = 1
          description  = "Keep last 5 images"
          selection = {
            tagStatus     = "tagged"
            tagPrefixList = ["v"]
            countType     = "imageCountMoreThan"
            countNumber   = 5
          }
          action = {
            type = "expire"
          }
        },
        {
          rulePriority = 2
          description  = "Delete untagged images"
          selection = {
            tagStatus   = "untagged"
            countType   = "sinceImagePushed"
            countUnit   = "days"
            countNumber = 1
          }
          action = {
            type = "expire"
          }
        }
      ]
    })
  }
}

# IAM role for Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "todoist-daily-reset-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda execution
resource "aws_iam_role_policy" "lambda_policy" {
  name = "todoist-daily-reset-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/todoist-daily-reset"
  retention_in_days = 14
}

# Lambda function
resource "aws_lambda_function" "todoist_daily_reset" {
  function_name = "todoist-daily-reset"
  role          = aws_iam_role.lambda_role.arn

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.todoist_daily_reset.repository_url}:latest"

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      TODOIST_API_TOKEN = var.todoist_api_token
      TIMEZONE          = var.timezone
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.lambda_logs
  ]

  # Prevent Terraform from updating the function if only the image URI changes
  # This allows GitHub Actions to deploy new images without Terraform conflicts
  lifecycle {
    ignore_changes = [image_uri]
  }
}

# EventBridge (CloudWatch Events) rule for daily execution
resource "aws_cloudwatch_event_rule" "daily_schedule" {
  name                = "todoist-daily-reset-schedule"
  description         = "Trigger Todoist daily reset Lambda function"
  schedule_expression = var.schedule_expression
}

# EventBridge target for Lambda function
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_schedule.name
  target_id = "TodoistDailyResetTarget"
  arn       = aws_lambda_function.todoist_daily_reset.arn
}

# Permission for EventBridge to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.todoist_daily_reset.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_schedule.arn
}
