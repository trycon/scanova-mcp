from mcp_http.ui_resources import (
    get_resource_by_uri,
    get_resource_for_tool,
    list_resources,
    read_resource_contents,
)


def test_list_resources_includes_qr_design():
    uris = {r.uri for r in list_resources()}
    assert "ui://scanova/qr-design.html" in uris
    assert "ui://scanova/create-qr-code.html" in uris
    assert "ui://scanova/create-folder.html" in uris
    assert "ui://scanova/download-qr.html" in uris
    assert "ui://scanova/qr-codes-list.html" in uris
    assert "ui://scanova/folders.html" in uris
    assert "ui://scanova/forms.html" in uris
    assert "ui://scanova/lead-lists.html" in uris
    assert "ui://scanova/users.html" in uris
    assert "ui://scanova/account-stats.html" in uris
    assert "ui://scanova/analytics-export.html" in uris
    assert "ui://scanova/design-options.html" in uris


def test_get_resource_for_design_options_tool():
    assert get_resource_for_tool("get_qr_design_options").uri == "ui://scanova/design-options.html"


def test_get_resource_by_uri_hit():
    resource = get_resource_by_uri("ui://scanova/qr-design.html")
    assert resource is not None
    assert resource.mime_type == "text/html;profile=mcp-app"
    assert "set_qr_design" in resource.tools


def test_get_resource_by_uri_miss():
    assert get_resource_by_uri("ui://scanova/does-not-exist.html") is None


def test_get_resource_for_tool_hit():
    resource = get_resource_for_tool("set_qr_design")
    assert resource is not None
    assert resource.uri == "ui://scanova/qr-design.html"


def test_get_resource_for_tool_miss():
    assert get_resource_for_tool("query_docs") is None


def test_get_resource_for_creation_tools():
    assert get_resource_for_tool("create_qr_code").uri == "ui://scanova/create-qr-code.html"
    assert get_resource_for_tool("create_folder").uri == "ui://scanova/create-folder.html"


def test_download_qr_code_resource():
    a = get_resource_for_tool("download_qr_code")
    assert a is not None
    assert a.uri == "ui://scanova/download-qr.html"


def test_download_qr_printable_not_registered():
    """Removed for now (2026-08-21) — not exposed as a tool."""
    assert get_resource_for_tool("download_qr_printable") is None


def test_folders_tools_share_one_resource():
    for tool in (
        "list_folders", "update_folder", "delete_folder",
        "move_qr_codes_to_folder", "unassign_qr_codes_from_folder",
    ):
        assert get_resource_for_tool(tool).uri == "ui://scanova/folders.html"


def test_forms_tools_share_one_resource():
    for tool in ("list_forms", "retrieve_form", "update_form", "delete_form"):
        assert get_resource_for_tool(tool).uri == "ui://scanova/forms.html"


def test_lead_list_tools_share_one_resource():
    for tool in ("list_lead_lists", "retrieve_lead_list", "update_lead_list", "delete_lead_list"):
        assert get_resource_for_tool(tool).uri == "ui://scanova/lead-lists.html"


def test_user_tools_share_one_resource():
    for tool in ("list_users", "get_user", "add_user", "remove_user", "list_user_roles", "update_user_role"):
        assert get_resource_for_tool(tool).uri == "ui://scanova/users.html"


def test_account_stats_resource():
    assert get_resource_for_tool("get_account_stats").uri == "ui://scanova/account-stats.html"


def test_get_qr_analytics_has_no_resource():
    """The dashboard widget was simplified to show account stats only,
    dropping the query-builder UI that used to trigger get_qr_analytics —
    it now returns plain text with no widget."""
    assert get_resource_for_tool("get_qr_analytics") is None


def test_analytics_export_tools_share_one_resource():
    for tool in ("export_analytics", "export_raw_scans"):
        assert get_resource_for_tool(tool).uri == "ui://scanova/analytics-export.html"


def test_read_resource_contents_returns_html():
    contents = read_resource_contents("ui://scanova/qr-design.html")
    assert contents is not None
    assert "<html" in contents.lower()


def test_read_resource_contents_unknown_uri_is_none():
    assert read_resource_contents("ui://scanova/nope.html") is None
