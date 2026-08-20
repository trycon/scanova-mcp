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
    assert result["result"]["contents"][0]["mimeType"] == "text/html;profile=mcp-app"
    assert "<html" in result["result"]["contents"][0]["text"].lower()


def test_resources_read_declares_csp_meta():
    body = {"id": 6, "params": {"uri": "ui://scanova/qr-design.html"}}
    result = protocol.handle_tool_method("resources/read", body, api_key=None)
    csp = result["result"]["contents"][0]["_meta"]["ui"]["csp"]
    assert csp["connectDomains"] == []
    assert csp["resourceDomains"] == []


def test_resources_list_declares_csp_meta():
    result = protocol.handle_tool_method("resources/list", {"id": 2}, api_key=None)
    for r in result["result"]["resources"]:
        assert "csp" in r["_meta"]["ui"]


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


def test_tools_call_includes_structured_content_for_ui_hydration(monkeypatch):
    """window.openai.toolOutput (and callTool's resolved value) hydrate from
    structuredContent, not content[0].text — a UI widget gets no data without it."""
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    envelope = {"ok": True, "data": {"count": 1, "results": [{"id": "qr-1"}]}, "pagination": {"count": 1, "next": None, "previous": None}}
    monkeypatch.setattr(protocol, "execute_tool", lambda name, args, key: envelope)
    monkeypatch.setattr(protocol, "normalize", lambda raw, tool_name: raw)
    body = {"id": 9, "params": {"name": "list_qr_codes", "arguments": {}}}
    result = protocol.handle_tool_method("tools/call", body, api_key="k")
    assert result["result"]["structuredContent"] == envelope


def test_tools_list_declares_meta_for_ui_enabled_tool():
    result = protocol.handle_tool_method("tools/list", {"id": 7}, api_key="k")
    tools = {t["name"]: t for t in result["result"]["tools"]}
    assert tools["list_qr_codes"]["_meta"]["openai/outputTemplate"] == "ui://scanova/qr-codes-list.html"
    assert tools["list_qr_codes"]["_meta"]["ui"]["resourceUri"] == "ui://scanova/qr-codes-list.html"


def test_tools_list_omits_meta_for_non_ui_tool():
    result = protocol.handle_tool_method("tools/list", {"id": 8}, api_key="k")
    tools = {t["name"]: t for t in result["result"]["tools"]}
    assert "_meta" not in tools["query_docs"]


def test_tools_call_attaches_meta_for_ui_enabled_tool(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    monkeypatch.setattr(protocol, "execute_tool", lambda name, args, key: {"id": "qr-1", "pattern_info": "{}"})
    body = {"id": 6, "params": {"name": "set_qr_design", "arguments": {"qrid": "qr-1"}}}
    result = protocol.handle_tool_method("tools/call", body, api_key="k")
    assert result["result"]["_meta"]["openai/outputTemplate"] == "ui://scanova/qr-design.html"
    # the text content block itself is still present and untouched in shape
    assert result["result"]["content"][0]["type"] == "text"
