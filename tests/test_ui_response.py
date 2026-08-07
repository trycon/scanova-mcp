import mcp_http.ui_response as ui_response


def test_disabled_tool_gets_no_meta():
    envelope = {"ok": True, "data": {"id": "abc"}}
    result = ui_response.attach_ui_metadata("query_docs", envelope)
    assert result["meta"] is None
    assert result["envelope"] is envelope


def test_enabled_tool_gets_dual_meta(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    envelope = {"ok": True, "data": {"id": "abc"}}
    result = ui_response.attach_ui_metadata("set_qr_design", envelope)
    assert result["envelope"] is envelope  # untouched, same object
    assert result["meta"]["openai/outputTemplate"] == "ui://scanova/qr-design.html"
    assert result["meta"]["ui"]["resourceUri"] == "ui://scanova/qr-design.html"


def test_creation_tools_get_dual_meta(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name, expected_uri in (
        ("create_qr_code", "ui://scanova/create-qr-code.html"),
        ("create_folder", "ui://scanova/create-folder.html"),
    ):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"]["openai/outputTemplate"] == expected_uri
        assert result["meta"]["ui"]["resourceUri"] == expected_uri


def test_download_tools_get_dual_meta(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name in ("download_qr_code", "download_qr_printable"):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"]["openai/outputTemplate"] == "ui://scanova/download-qr.html"


def test_phase5_tools_get_dual_meta(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name in ("list_qr_codes", "list_folders", "list_forms", "list_lead_lists", "list_users"):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"] is not None, tool_name


def test_global_flag_off_suppresses_meta(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", False, raising=False)
    envelope = {"ok": True, "data": {"id": "abc"}}
    result = ui_response.attach_ui_metadata("set_qr_design", envelope)
    assert result["meta"] is None
    assert result["envelope"] is envelope


def test_envelope_keys_never_mutated(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    envelope = {"ok": True, "data": {"id": "abc"}, "error": None}
    before_keys = set(envelope.keys())
    ui_response.attach_ui_metadata("set_qr_design", envelope)
    assert set(envelope.keys()) == before_keys
