# Build/Test Commands
# No test runner configured.
# Install dependencies:
pip install -r src/requirements.txt
# Run locally (requires TODOIST_API_TOKEN env var):
python src/main.py

# Code Style & Guidelines
- **Python**: Follow PEP 8. Use 4 spaces for indentation.
- **Structure**: 
  - `src/`: Python source code and Dockerfile.
  - `terraform/`: Infrastructure as Code.
- **Imports**: Group standard library, third-party (requests, pytz), and local imports.
- **Error Handling**: Use `try-except` blocks for network calls. Log errors to stdout/stderr.
- **Configuration**: Secrets must be passed via environment variables (`TODOIST_API_TOKEN`).
- **Infrastructure**: Managed via Terraform. modifying `.tf` files changes the AWS architecture.
- **Naming**: Snake_case for functions and variables. Upper_case for constants.
