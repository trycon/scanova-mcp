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
    assert "ui://scanova/analytics-dashboard.html" in uris
    assert "ui://scanova/analytics-export.html" in uris


def test_get_resource_by_uri_hit():
    resource = get_resource_by_uri("ui://scanova/qr-design.html")
    assert resource is not None
    assert resource.mime_type == "text/html"
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


def test_download_tools_share_one_resource():
    a = get_resource_for_tool("download_qr_code")
    b = get_resource_for_tool("download_qr_printable")
    assert a is not None and b is not None
    assert a.uri == b.uri == "ui://scanova/download-qr.html"


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


def test_analytics_tools_share_one_resource():
    for tool in ("get_account_stats", "get_qr_analytics"):
        assert get_resource_for_tool(tool).uri == "ui://scanova/analytics-dashboard.html"


def test_analytics_export_tools_share_one_resource():
    for tool in ("export_analytics", "export_raw_scans"):
        assert get_resource_for_tool(tool).uri == "ui://scanova/analytics-export.html"


def test_read_resource_contents_returns_html():
    contents = read_resource_contents("ui://scanova/qr-design.html")
    assert contents is not None
    assert "<html" in contents.lower()


def test_read_resource_contents_unknown_uri_is_none():
    assert read_resource_contents("ui://scanova/nope.html") is None
