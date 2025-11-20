resource "aws_ecr_repository" "todoist_repo" {
  name                 = "todoist-daily-rollover"
  image_tag_mutability = "MUTABLE"
  force_delete         = true 
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "todoist_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Basic Execution Policy (Logs)
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "rollover_func" {
  function_name = "todoist-daily-rollover"
  role          = aws_iam_role.lambda_role.arn
  timeout       = 60 # 1 minute should be plenty
  package_type  = "Image"
  
  # Placeholder URI. The GitHub Action will build/push the real image and update this.
  image_uri     = "${aws_ecr_repository.todoist_repo.repository_url}:latest"

  environment {
    variables = {
      TODOIST_API_TOKEN = var.todoist_api_token
    }
  }
}
