import mcp_http.protocol as protocol
import mcp_http.ui_response as ui_response
from mcp.types import LATEST_PROTOCOL_VERSION


def test_initialize_declares_latest_protocol_version_and_resources_capability():
    result = protocol.handle_tool_method("initialize", {"id": 1}, api_key="k")
    assert result["result"]["protocolVersion"] == LATEST_PROTOCOL_VERSION
    assert "resources" in result["result"]["capabilities"]


def test_resources_list_includes_qr_design():
    result = protocol.handle_tool_method("resources/list", {"id": 2}, api_key=None)
    uris = {r["uri"] for r in result["result"]["resources"]}
    assert "ui://scanova/qr-design.html" in uris


def test_resources_read_known_uri():
    body = {"id": 3, "params": {"uri": "ui://scanova/qr-design.html"}}
    result = protocol.handle_tool_method("resources/read", body, api_key=None)
    assert "result" in result
    assert result["result"]["contents"][0]["mimeType"] == "text/html"
    assert "<html" in result["result"]["contents"][0]["text"].lower()


def test_resources_read_unknown_uri_returns_jsonrpc_error():
    body = {"id": 4, "params": {"uri": "ui://scanova/nope.html"}}
    result = protocol.handle_tool_method("resources/read", body, api_key=None)
    assert "error" in result
    assert result["error"]["code"] == -32002


def test_tools_call_content_block_unchanged_for_non_ui_tool(monkeypatch):
    """Backward-compat guardrail: a non-UI-enabled tool's content[0] text
    block must be byte-identical to what it was before UI Elements existed."""
    monkeypatch.setattr(protocol, "execute_tool", lambda name, args, key: {"ok": True})
    body = {"id": 5, "params": {"name": "query_docs", "arguments": {}}}
    result = protocol.handle_tool_method("tools/call", body, api_key="k")
    assert "_meta" not in result["result"]
    assert result["result"]["content"][0]["type"] == "text"


def test_tools_call_attaches_meta_for_ui_enabled_tool(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    monkeypatch.setattr(protocol, "execute_tool", lambda name, args, key: {"id": "qr-1", "pattern_info": "{}"})
    body = {"id": 6, "params": {"name": "set_qr_design", "arguments": {"qrid": "qr-1"}}}
    result = protocol.handle_tool_method("tools/call", body, api_key="k")
    assert result["result"]["_meta"]["openai/outputTemplate"] == "ui://scanova/qr-design.html"
    # the text content block itself is still present and untouched in shape
    assert result["result"]["content"][0]["type"] == "text"
