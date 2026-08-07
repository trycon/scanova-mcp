"""
Contract tests: validate protocol.py's hand-rolled JSON-RPC `result` payloads
against the official `mcp` SDK's own Pydantic result models.

protocol.py implements JSON-RPC by hand rather than running the SDK's own
dispatcher (see docs/mcp-ui-architecture.md Part 3/8.3) — these tests are
the safety net the architecture doc calls for: they catch spec drift
(wrong field names, wrong shapes) automatically instead of relying on
manual reading of the MCP spec.
"""

from mcp.types import (
    CallToolResult,
    InitializeResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
)

import mcp_http.protocol as protocol


def test_initialize_result_matches_sdk_model():
    result = protocol.handle_tool_method("initialize", {"id": 1}, api_key="k")
    InitializeResult.model_validate(result["result"])


def test_tools_list_result_matches_sdk_model():
    result = protocol.handle_tool_method("tools/list", {"id": 2}, api_key="k")
    ListToolsResult.model_validate(result["result"])


def test_resources_list_result_matches_sdk_model():
    result = protocol.handle_tool_method("resources/list", {"id": 3}, api_key=None)
    ListResourcesResult.model_validate(result["result"])


def test_resources_read_result_matches_sdk_model():
    body = {"id": 4, "params": {"uri": "ui://scanova/qr-design.html"}}
    result = protocol.handle_tool_method("resources/read", body, api_key=None)
    ReadResourceResult.model_validate(result["result"])


def test_tools_call_result_matches_sdk_model_without_ui_meta(monkeypatch):
    monkeypatch.setattr(protocol, "execute_tool", lambda name, args, key: {"ok": True})
    body = {"id": 5, "params": {"name": "query_docs", "arguments": {}}}
    result = protocol.handle_tool_method("tools/call", body, api_key="k")
    CallToolResult.model_validate(result["result"])


def test_tools_call_result_matches_sdk_model_with_ui_meta(monkeypatch):
    import mcp_http.ui_response as ui_response

    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    monkeypatch.setattr(protocol, "execute_tool", lambda name, args, key: {"id": "qr-1"})
    body = {"id": 6, "params": {"name": "set_qr_design", "arguments": {"qrid": "qr-1"}}}
    result = protocol.handle_tool_method("tools/call", body, api_key="k")
    # The SDK's Result base model accepts arbitrary extra fields via its
    # own `_meta` alias — validating here confirms our _meta attachment
    # (Part 5A) doesn't produce a shape the SDK's own model would reject.
    CallToolResult.model_validate(result["result"])
