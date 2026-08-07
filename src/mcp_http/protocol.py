"""MCP JSON-RPC handlers for tool-related methods."""

import json
import logging

from mcp.types import LATEST_PROTOCOL_VERSION

from mcp_http.dispatcher import execute_tool
from mcp_http.normalizer import normalize
from mcp_http.registry import list_mcp_tools
from mcp_http.ui_resources import get_resource_by_uri, list_resources, read_resource_contents
from mcp_http.ui_response import attach_ui_metadata

log = logging.getLogger("mcp")

# Resources are static UI assets, not Scanova user data — no API key required to fetch them.
PUBLIC_METHODS = frozenset({
    "initialize",
    "tools/list",
    "resources/list",
    "resources/read",
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
    normalized = normalize(result, tool_name)
    if isinstance(normalized, dict) and normalized.get("status_code") == 401:
        normalized["error"] = (
            "Your Scanova session has expired or the API key is invalid. "
            "Please reconnect your Scanova API key in your MCP client settings."
        )

    built = attach_ui_metadata(tool_name, normalized)
    mcp_result = {"content": [{"type": "text", "text": json.dumps(built["envelope"])}]}
    if built["meta"] is not None:
        mcp_result["_meta"] = built["meta"]

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": mcp_result,
    }


def resources_list_result(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "resources": [
                {"uri": r.uri, "name": r.file_path, "mimeType": r.mime_type}
                for r in list_resources()
            ]
        },
    }


def resources_read_result(request_id, uri: str):
    resource = get_resource_by_uri(uri)
    contents = read_resource_contents(uri) if resource else None
    if resource is None or contents is None:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32002, "message": f"Resource not found: {uri}"},
        }
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "contents": [
                {"uri": resource.uri, "mimeType": resource.mime_type, "text": contents}
            ]
        },
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
            "protocolVersion": LATEST_PROTOCOL_VERSION,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
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

    if method == "resources/list":
        return resources_list_result(request_id)

    if method == "resources/read":
        params = body.get("params", {})
        return resources_read_result(request_id, params.get("uri"))

    if method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            return tools_call_result(request_id, tool_name, arguments, api_key)
        except Exception as e:
            return tools_call_error(request_id, str(e))

    return method_not_found(request_id, method)
