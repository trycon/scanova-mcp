import os
from pathlib import Path

# Base URL for Scanova API
SCANOVA_BASE_URL = "https://management.scanova.io/"

# Optional: Access token for MCP server authentication (if needed)
MCP_ACCESS_TOKEN = os.getenv("MCP_ACCESS_TOKEN")
