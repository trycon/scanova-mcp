import os
from pathlib import Path

# Base URL for Scanova API
SCANOVA_BASE_URL = os.getenv("API_BASE_URL", "https://management.scanova.io/")

# Optional: Access token for MCP server authentication (if needed)
MCP_ACCESS_TOKEN = os.getenv("MCP_ACCESS_TOKEN")

# OAuth server URL for discovery endpoint
OAUTH_SERVER_URL = os.getenv("OAUTH_SERVER_URL", "https://qcg-api.scanova.io")

# Resource URL for lazy authentication 401 header
MCP_RESOURCE_URL = os.getenv("MCP_RESOURCE_URL", "https://mcp.scanova.io")

OPENAI_APPS_CHALLENGE = os.getenv("OPENAI_APPS_CHALLENGE")

# Global kill switch for MCP UI Elements (resources + _meta attachment).
# Per-tool enablement is separate — see mcp_http/ui_response.py:UI_ENABLED_TOOLS.
UI_ELEMENTS_ENABLED = os.getenv("UI_ELEMENTS_ENABLED", "true").strip().lower() in ("1", "true", "yes")

# CORS allowlist for the /mcp endpoint. Comma-separated origins, e.g.
# "https://chatgpt.com,https://claude.ai". Defaults to "*" (today's
# behavior, preserved for backward compatibility) — set this env var to
# scope it down once the UI-capable client origins are known. See
# docs/mcp-ui-architecture.md Part 15 (CORS scoping).
_allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*").strip()
ALLOWED_ORIGINS = (
    ["*"] if _allowed_origins_raw == "*"
    else [o.strip() for o in _allowed_origins_raw.split(",") if o.strip()]
)