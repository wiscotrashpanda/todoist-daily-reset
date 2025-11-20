# Todoist Daily Recurring Task Rollover

This project automates the management of daily recurring tasks in Todoist. It runs a nightly job (AWS Lambda) that identifies "daily" recurring tasks that were due yesterday but not completed. Instead of letting them become "overdue", the job automatically "closes" them, effectively rolling them over to the current day without marking them as completed in your history.

## Architecture

- **Runtime**: Python 3.11 running on AWS Lambda (packaged via Docker).
- **Infrastructure**: Managed via Terraform.
- **Scheduling**: AWS EventBridge (CloudWatch Events) triggers the Lambda nightly at midnight CST (06:00 UTC).
- **Deployment**: GitHub Actions handles the build and deployment pipeline.

## Prerequisites

- AWS Account
- Todoist API Token
- GitHub Repository with Actions enabled

## Setup

### 1. GitHub Secrets

Configure the following secrets in your GitHub repository:

- `AWS_ROLE_ARN`: The ARN of the IAM role that GitHub Actions will assume to authenticate with AWS (OIDC).

### 2. Environment Variables

The Lambda function requires the following environment variable:

- `TODOIST_API_TOKEN`: Your Todoist API token.

*Note: By default, the Terraform configuration sets a placeholder value. You should update this manually in the AWS Lambda Console after the initial deployment, or configure it to be passed via CI/CD secrets.*

## Deployment

The project is deployed automatically via GitHub Actions on pushes to the `main` branch.

1. **Infrastructure Provisioning**: Terraform creates the ECR repository.
2. **Build**: The Docker image is built and pushed to ECR.
3. **Deploy**: Terraform deploys the Lambda function and configures the EventBridge scheduler.

## Local Development

1. Install dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

2. Run the script locally:
   ```bash
   export TODOIST_API_TOKEN="your_token"
   python src/main.py
   ```

## Directory Structure

- `src/`: Python source code and Dockerfile.
- `terraform/`: Terraform infrastructure definitions.
- `.github/workflows/`: CI/CD configuration.
