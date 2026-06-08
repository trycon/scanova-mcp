"""MCP JSON-RPC handlers for tool-related methods."""

import logging

from mcp_http.dispatcher import execute_tool
from mcp_http.registry import list_mcp_tools

log = logging.getLogger("mcp")

PUBLIC_METHODS = frozenset({
    "initialize",
    "tools/list",
    "notifications/initialized",
    "notifications/cancelled",
})


def tools_list_result(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": list_mcp_tools()},
    }


def tools_call_result(request_id, tool_name: str, arguments: dict, api_key: str):
    result = execute_tool(tool_name, arguments, api_key)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"content": [{"type": "text", "text": str(result)}]},
    }


def tools_call_error(request_id, message: str):
    log.error("Tool execution error: %s", message)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32603, "message": f"Tool execution error: {message}"},
    }


def initialize_result(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "tools": {"listChanged": False},
            },
            "serverInfo": {"name": "scanova-mcp", "version": "1.0.0"},
        },
    }


def method_not_found(request_id, method: str):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def handle_tool_method(method: str, body: dict, api_key: str):
    """
    Handle MCP JSON-RPC methods.

    Returns a JSON-RPC response dict, or None for notification methods
    (notifications have no id and must not receive a response).
    Caller handles auth and HTTP wrapping.
    """
    request_id = body.get("id")

    if method == "initialize":
        return initialize_result(request_id)

    # Notifications — no response body (return None so caller sends 202)
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None

    if method == "tools/list":
        return tools_list_result(request_id)

    if method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            return tools_call_result(request_id, tool_name, arguments, api_key)
        except Exception as e:
            return tools_call_error(request_id, str(e))

    return method_not_found(request_id, method)
