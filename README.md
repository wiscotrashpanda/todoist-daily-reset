# Todoist Daily Reset

An AWS Lambda function that automatically completes recurring Todoist tasks that are due today, effectively "postponing" them to their next scheduled occurrence. This helps maintain a clean daily view while preserving your recurring task schedules.

## Features

- 🔄 Automatically identifies recurring tasks due today
- ✅ Marks them as complete to trigger the next recurrence
- 🕐 Timezone-aware processing
- 📊 Comprehensive logging and error handling
- 🐳 Containerized with Docker
- 🚀 Deployed via Terraform and GitHub Actions
- ☁️ Serverless architecture with AWS Lambda

## How It Works

The Lambda function:
1. Connects to your Todoist account using the API
2. Retrieves all active tasks
3. Filters for recurring tasks that are due today (in your timezone)
4. Marks these tasks as complete
5. Todoist automatically creates the next occurrence based on the recurring pattern

## Architecture

```
GitHub Actions → Docker Build → ECR → Lambda Function → Todoist API
                      ↓
              Terraform → AWS Resources (Lambda, EventBridge, CloudWatch)
```

## Prerequisites

- AWS Account with appropriate permissions
- Todoist account with API access
- GitHub repository for CI/CD
- Terraform installed locally (optional, for manual deployment)

## Setup Instructions

### 1. Get Your Todoist API Token

1. Go to [Todoist Integrations](https://todoist.com/prefs/integrations)
2. Copy your API token
3. Keep this secure - you'll need it for the deployment

### 2. Fork This Repository

Fork this repository to your GitHub account.

### 3. Configure GitHub Secrets and Variables

In your GitHub repository, go to Settings → Secrets and Variables → Actions:

**Required Secrets:**
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `TODOIST_API_TOKEN`: Your Todoist API token

**Optional Variables:**
- `TIMEZONE`: Your timezone (default: UTC). Examples: `America/New_York`, `Europe/London`, `Asia/Tokyo`
- `SCHEDULE_EXPRESSION`: Cron expression for when to run (default: `cron(0 1 * * ? *)` - daily at 1 AM UTC)

### 4. Deploy

Push to the `main` branch or manually trigger the GitHub Actions workflow. This will:
1. Build and test the Lambda function
2. Create a Docker image and push it to ECR
3. Deploy the infrastructure with Terraform
4. Update the Lambda function with the new image

### 5. Verify Deployment

Check the AWS Console:
- **Lambda**: Function should be created and configured
- **ECR**: Repository should contain your Docker image
- **EventBridge**: Rule should be scheduled according to your cron expression
- **CloudWatch**: Log group should be created for monitoring

## Manual Deployment (Alternative)

If you prefer to deploy manually using Terraform:

### 1. Install Dependencies

```bash
# Install Terraform
brew install terraform  # macOS
# or download from https://terraform.io

# Install AWS CLI
brew install awscli  # macOS
# or download from https://aws.amazon.com/cli/
```

### 2. Configure AWS Credentials

```bash
aws configure
```

### 3. Build and Push Docker Image

```bash
# Login to ECR (replace region and account ID)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t todoist-daily-reset .
docker tag todoist-daily-reset:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/todoist-daily-reset:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/todoist-daily-reset:latest
```

### 4. Deploy with Terraform

```bash
cd terraform

# Copy and edit the variables file
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and deploy
terraform init
terraform plan
terraform apply
```

## Configuration

### Environment Variables

The Lambda function uses these environment variables:

- `TODOIST_API_TOKEN`: Your Todoist API token (required)
- `TIMEZONE`: Timezone for task processing (default: UTC)

### Schedule Configuration

The function runs on a schedule defined by the `schedule_expression` variable. Examples:

- `cron(0 1 * * ? *)` - Daily at 1:00 AM UTC
- `cron(0 6 * * ? *)` - Daily at 6:00 AM UTC  
- `cron(0 22 * * ? *)` - Daily at 10:00 PM UTC
- `cron(0 */6 * * ? *)` - Every 6 hours

See [AWS Schedule Expressions](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule.html) for more details.

## Monitoring

### CloudWatch Logs

View Lambda execution logs in CloudWatch:
- Log Group: `/aws/lambda/todoist-daily-reset`
- Each execution logs processed tasks and any errors

### Lambda Metrics

Monitor in AWS Console:
- Invocations, errors, duration
- Custom metrics for tasks processed

### Manual Testing

Test the Lambda function manually:

```bash
aws lambda invoke \
  --function-name todoist-daily-reset \
  --payload '{}' \
  response.json && cat response.json
```

## Troubleshooting

### Common Issues

1. **Lambda Timeout**: Increase timeout in `terraform/variables.tf`
2. **API Rate Limits**: Todoist has rate limits; function includes retry logic
3. **Timezone Issues**: Verify timezone string is valid (e.g., `America/New_York`)
4. **Permissions**: Ensure AWS credentials have necessary permissions

### Debug Locally

Run the Lambda function locally:

```bash
# Set environment variables
export TODOIST_API_TOKEN="your-token"
export TIMEZONE="America/New_York"

# Run the function
python lambda_function.py
```

### Check Logs

```bash
# View recent logs
aws logs tail /aws/lambda/todoist-daily-reset --follow

# View specific time range
aws logs tail /aws/lambda/todoist-daily-reset --since 1h
```

## Security

- API tokens are stored as encrypted GitHub secrets
- Lambda function has minimal IAM permissions
- ECR repository scans images for vulnerabilities
- CloudWatch logs are retained for 14 days

## Cost Estimation

Typical monthly costs (assuming daily execution):
- Lambda: ~$0.20 (128MB, 30s execution)
- ECR: ~$0.10 (storage)
- CloudWatch: ~$0.50 (logs)
- **Total: ~$0.80/month**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Open an issue in this repository
