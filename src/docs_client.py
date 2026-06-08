"""
Bridge client for the Scanova docs MCP server at https://docs.scanova.io/mcp.

Connectivity facts (verified by probing):
- Stateless: no initialize or session management required for tool calls
- Response format: SSE (text/event-stream) with "data: {...}" lines
- No authentication required (public documentation server)
- GET requests return 405 — POST only
- Timeout risk: large file reads can take 10-15s

Available tools on the docs MCP:
  search_scanova_api_documentation(query)
      Full-text semantic search across all Scanova API docs.
  query_docs_filesystem_scanova_api_documentation(command)
      Read-only shell (rg, grep, find, tree, ls, cat, head, tail, jq, etc.)
      against a virtual in-memory filesystem rooted at / containing all
      .mdx doc pages and OpenAPI specs. Stateless — cwd resets to / each call.
"""
import json
import logging

import requests

DOCS_MCP_URL = "https://docs.scanova.io/mcp"
TIMEOUT = 15  # seconds — large file reads can be slow

_SEARCH_TOOL = "search_scanova_api_documentation"
_FS_TOOL = "query_docs_filesystem_scanova_api_documentation"

log = logging.getLogger("mcp.docs_client")


def _parse_sse(raw: str) -> dict:
    """Extract the first JSON payload from an SSE response stream."""
    for line in raw.split("\n"):
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except json.JSONDecodeError:
                pass
    return {"error": {"message": "Could not parse SSE response from docs MCP"}}


def _call(tool_name: str, arguments: dict) -> dict:
    """Make a single stateless tool call to the docs MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    try:
        resp = requests.post(DOCS_MCP_URL, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        parsed = _parse_sse(resp.text)

        if "result" in parsed:
            content = parsed["result"].get("content", [])
            texts = [c["text"] for c in content if c.get("type") == "text"]
            return {"ok": True, "result": "\n".join(texts)}

        err = parsed.get("error", {})
        return {"ok": False, "error": err.get("message", str(err))}

    except requests.Timeout:
        return {
            "ok": False,
            "error": f"Docs MCP did not respond within {TIMEOUT}s — try a more targeted query.",
        }
    except requests.ConnectionError as e:
        return {
            "ok": False,
            "error": f"Cannot reach docs.scanova.io/mcp: {e}",
        }
    except requests.HTTPError as e:
        return {
            "ok": False,
            "error": f"HTTP {e.response.status_code} from docs MCP — note: GET returns 405 (POST only).",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def probe() -> dict:
    """
    Check connectivity and list tools available on the docs MCP server.
    Uses the MCP initialize handshake which returns capabilities in one round-trip.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "scanova-mcp-bridge", "version": "1.0.0"},
        },
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    try:
        resp = requests.post(DOCS_MCP_URL, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = _parse_sse(resp.text)
        result = data.get("result", {})
        tools = list(result.get("capabilities", {}).get("tools", {}).keys())
        return {
            "connected": True,
            "server": result.get("serverInfo", {}),
            "available_tools": tools,
            "note": "Stateless server — no session management needed. POST only.",
        }
    except requests.Timeout:
        return {"connected": False, "error": f"Timed out after {TIMEOUT}s"}
    except requests.ConnectionError as e:
        return {"connected": False, "error": f"Connection failed: {e}"}
    except requests.HTTPError as e:
        return {"connected": False, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"connected": False, "error": str(e)}


def search(query: str) -> dict:
    """
    Semantic search across all Scanova API documentation.
    Returns contextual content with titles and links to matching pages.
    """
    if not query:
        return {"ok": False, "error": "query is required"}
    return _call(_SEARCH_TOOL, {"query": query})


def filesystem(command: str) -> dict:
    """
    Run a read-only shell command on the docs virtual filesystem.

    Supported: rg, grep, find, tree, ls, cat, head, tail, stat, wc,
               sort, uniq, cut, sed, awk, jq, and basic text utilities.
    The filesystem is rooted at / and contains .mdx pages + OpenAPI specs.
    Each call is stateless — cwd resets to / between calls.

    Useful paths:
      /api-reference/references/pattern-info.mdx  — QR design schema
      /api-reference/references/category-list.mdx — QR category IDs
      /api-reference/references/components.mdx    — component reference
      /guides/category-components/                — per-category info formats
      tree / -L 2                                 — full doc structure
    """
    if not command:
        return {"ok": False, "error": "command is required"}
    return _call(_FS_TOOL, {"command": command})
