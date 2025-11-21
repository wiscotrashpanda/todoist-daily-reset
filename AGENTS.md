# Build/Test Commands
# No test runner configured. Project is simple enough to test manually.
# Install dependencies:
pip install -r src/requirements.txt
# Run locally (requires TODOIST_API_TOKEN env var):
export TODOIST_API_TOKEN="your_token"
python src/main.py
# Build Docker image:
docker build -t todoist-daily-rollover:latest ./src
# Deploy infrastructure:
cd terraform && terraform init && terraform plan

# Code Style & Guidelines
- **Python Version**: 3.11 (matches AWS Lambda runtime in Dockerfile).
- **Formatting**: Follow PEP 8. Use 4 spaces for indentation. Max line length 100-120 chars.
- **Imports**: Group in order: standard library (os, json, datetime), third-party (requests, pytz), then local imports. Separate groups with blank lines.
- **Naming**: snake_case for functions/variables. UPPER_CASE for constants (API_TOKEN, BASE_URL).
- **Error Handling**: Always use try-except for network calls (requests.*). Print errors to stdout/stderr for Lambda CloudWatch logs. Re-raise exceptions after logging.
- **Comments**: Use docstrings for functions. Include inline comments for complex date/time logic or business rules.
- **Configuration**: All secrets via environment variables. Never hardcode tokens.
- **Structure**: 
  - `src/`: Python code (main.py), dependencies (requirements.txt), Dockerfile
  - `terraform/`: Infrastructure as Code (.tf files) - changes here affect AWS resources
  - `.github/workflows/`: CI/CD pipeline (deploy.yml)
- **Lambda Handler**: main.lambda_handler(event, context) is the entry point. Must return dict with statusCode and body.
- **Testing**: Manual testing via local execution. Verify date logic uses CST timezone correctly.
