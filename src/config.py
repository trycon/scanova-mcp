import os
from pathlib import Path

# Base URL for Scanova API
SCANOVA_BASE_URL = "https://management.scanova.io/"

# Optional: Access token for MCP server authentication (if needed)
MCP_ACCESS_TOKEN = os.getenv("MCP_ACCESS_TOKEN")

# OAuth server URL for discovery endpoint
OAUTH_SERVER_URL = os.getenv("OAUTH_SERVER_URL", "https://qcg-api.scanova.io")

# Resource URL for lazy authentication 401 header
MCP_RESOURCE_URL = os.getenv("MCP_RESOURCE_URL", "https://mcp.scanova.io")

OPENAI_APPS_CHALLENGE = os.getenv("OPENAI_APPS_CHALLENGE")