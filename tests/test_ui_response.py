import mcp_http.ui_response as ui_response
from mcp_http.ui_resources import get_resource_for_tool


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
    expected = get_resource_for_tool("set_qr_design").versioned_uri
    assert result["meta"]["openai/outputTemplate"] == expected
    assert result["meta"]["ui"]["resourceUri"] == expected


def test_create_qr_code_ui_only_shown_on_failure(monkeypatch):
    """create_qr_code is a CONDITIONAL_UI_RULES tool: on success the text
    confirmation already says everything, so no widget should render — the
    form only appears (pre-filled) when the call failed, so the user can
    fix and retry via the UI."""
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)

    success = ui_response.attach_ui_metadata("create_qr_code", {"ok": True, "data": {"qrid": "Qabc"}})
    assert success["meta"] is None

    failure = ui_response.attach_ui_metadata("create_qr_code", {"ok": False, "error": "bad request"})
    assert failure["meta"]["openai/outputTemplate"] == get_resource_for_tool("create_qr_code").versioned_uri


def test_open_qr_code_creation_form_always_shows_ui(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    result = ui_response.attach_ui_metadata("open_qr_code_creation_form", {"ok": True, "data": {"mode": "blank"}})
    assert result["meta"]["openai/outputTemplate"] == get_resource_for_tool("open_qr_code_creation_form").versioned_uri


def test_download_qr_code_gets_dual_meta(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    expected = get_resource_for_tool("download_qr_code").versioned_uri
    result = ui_response.attach_ui_metadata("download_qr_code", {"ok": True, "data": {}})
    assert result["meta"]["openai/outputTemplate"] == expected


def test_phase5_tools_get_dual_meta(monkeypatch):
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name in ("get_account_stats",):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"] is not None, tool_name


def test_all_form_tools_deliberately_have_no_ui(monkeypatch):
    """Tested and confirmed working fine as plain text, 2026-08-24. The
    resource file (forms.html) and its ui_resources.py registry entry are
    kept; only the UI_ENABLED_TOOLS trigger was removed."""
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name in ("list_forms", "retrieve_form", "update_form", "delete_form"):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"] is None, tool_name


def test_all_lead_list_tools_deliberately_have_no_ui(monkeypatch):
    """Tested and confirmed working fine as plain text, 2026-08-24. The
    resource file (lead-lists.html) and its ui_resources.py registry entry
    are kept; only the UI_ENABLED_TOOLS trigger was removed."""
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name in ("list_lead_lists", "retrieve_lead_list", "update_lead_list", "delete_lead_list"):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"] is None, tool_name


def test_all_user_management_tools_deliberately_have_no_ui(monkeypatch):
    """Tested and confirmed working fine as plain text, 2026-08-24. The
    resource file (users.html) and its ui_resources.py registry entry are
    kept; only the UI_ENABLED_TOOLS trigger was removed."""
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name in (
        "list_users", "get_user", "add_user", "remove_user",
        "list_user_roles", "update_user_role",
    ):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"] is None, tool_name


def test_all_folder_tools_deliberately_have_no_ui(monkeypatch):
    """Tested and confirmed working fine as plain text, 2026-08-24. The
    resource files (create-folder.html, folders.html) and their
    ui_resources.py registry entries are kept; only the UI_ENABLED_TOOLS
    trigger was removed."""
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    for tool_name in (
        "create_folder",
        "list_folders",
        "update_folder",
        "delete_folder",
        "move_qr_codes_to_folder",
        "unassign_qr_codes_from_folder",
    ):
        result = ui_response.attach_ui_metadata(tool_name, {"ok": True, "data": {}})
        assert result["meta"] is None, tool_name


def test_list_qr_codes_deliberately_has_no_ui(monkeypatch):
    """Tested and confirmed working fine as plain text — the model can
    decide how to present a QR list, no widget needed. The resource file
    and its ui_resources.py registry entry are kept; only the
    UI_ENABLED_TOOLS trigger was removed, so this stays easy to re-enable."""
    monkeypatch.setattr(ui_response, "UI_ELEMENTS_ENABLED", True, raising=False)
    result = ui_response.attach_ui_metadata("list_qr_codes", {"ok": True, "data": {}})
    assert result["meta"] is None


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
