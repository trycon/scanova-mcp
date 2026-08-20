"""
UI resource registry — maps logical MCP resource URIs to the static HTML/JS
payloads served via resources/read.

Owns: resource discovery data (backs resources/list) and resource content
lookup (backs resources/read). Does NOT decide whether a given tool call
should attach _meta — that's ui_response.py's job (see Part 4A/5A of
docs/mcp-ui-architecture.md).

Deliberately simple: no versioning field, no description field, no
per-resource feature flag. See docs/mcp-ui-architecture.md Part 7 for why
each of those was left out.
"""

from dataclasses import dataclass
from pathlib import Path

_UI_DIR = Path(__file__).parent / "ui"

# All UI resources are fully self-contained (inline CSS/JS, no fetch/XHR,
# img-src data: only per each HTML's own CSP meta tag) — so every resource
# declares the same empty allowlist here. Add per-resource overrides if a
# widget ever needs to reach an external domain.
_NO_EXTERNAL_CSP = {"connectDomains": [], "resourceDomains": []}


@dataclass(frozen=True)
class UIResource:
    uri: str              # logical MCP resource URI, e.g. "ui://scanova/qr-design.html"
    file_path: str        # filename relative to src/mcp_http/ui/
    mime_type: str        # "text/html;profile=mcp-app" marks this as a renderable MCP App/widget resource
    tools: tuple          # tool name(s) this resource is attached to

    @property
    def path(self) -> Path:
        return _UI_DIR / self.file_path

    @property
    def meta(self) -> dict:
        """_meta.ui.csp for resources/list and resources/read — tells the
        host which domains this widget's iframe may reach."""
        return {"ui": {"csp": _NO_EXTERNAL_CSP}}


_RESOURCES: dict[str, UIResource] = {
    r.uri: r
    for r in (
        UIResource(
            uri="ui://scanova/qr-design.html",
            file_path="qr-design.html",
            mime_type="text/html;profile=mcp-app",
            tools=("set_qr_design",),
        ),
        UIResource(
            uri="ui://scanova/create-qr-code.html",
            file_path="create_qr_code.html",
            mime_type="text/html;profile=mcp-app",
            tools=("create_qr_code",),
        ),
        UIResource(
            uri="ui://scanova/create-folder.html",
            file_path="create_folder.html",
            mime_type="text/html;profile=mcp-app",
            tools=("create_folder",),
        ),
        UIResource(
            uri="ui://scanova/download-qr.html",
            file_path="download_qr.html",
            mime_type="text/html;profile=mcp-app",
            tools=("download_qr_code", "download_qr_printable"),
        ),
        UIResource(
            uri="ui://scanova/qr-codes-list.html",
            file_path="qr_codes_list.html",
            mime_type="text/html;profile=mcp-app",
            tools=("list_qr_codes",),
        ),
        UIResource(
            uri="ui://scanova/folders.html",
            file_path="folders.html",
            mime_type="text/html;profile=mcp-app",
            tools=(
                "list_folders",
                "update_folder",
                "delete_folder",
                "move_qr_codes_to_folder",
                "unassign_qr_codes_from_folder",
            ),
        ),
        UIResource(
            uri="ui://scanova/forms.html",
            file_path="forms.html",
            mime_type="text/html;profile=mcp-app",
            tools=("list_forms", "retrieve_form", "update_form", "delete_form"),
        ),
        UIResource(
            uri="ui://scanova/lead-lists.html",
            file_path="lead_lists.html",
            mime_type="text/html;profile=mcp-app",
            tools=(
                "list_lead_lists",
                "retrieve_lead_list",
                "update_lead_list",
                "delete_lead_list",
            ),
        ),
        UIResource(
            uri="ui://scanova/users.html",
            file_path="users.html",
            mime_type="text/html;profile=mcp-app",
            tools=(
                "list_users",
                "get_user",
                "add_user",
                "remove_user",
                "list_user_roles",
                "update_user_role",
            ),
        ),
        UIResource(
            uri="ui://scanova/analytics-dashboard.html",
            file_path="analytics_dashboard.html",
            mime_type="text/html;profile=mcp-app",
            tools=("get_account_stats", "get_qr_analytics"),
        ),
        UIResource(
            uri="ui://scanova/analytics-export.html",
            file_path="analytics_export.html",
            mime_type="text/html;profile=mcp-app",
            tools=("export_analytics", "export_raw_scans"),
        ),
    )
}


def list_resources() -> list[UIResource]:
    """All registered UI resources, for resources/list."""
    return list(_RESOURCES.values())


def get_resource_by_uri(uri: str) -> UIResource | None:
    """Look up a resource by its logical URI, for resources/read.

    Falls back to a tool-name lookup when the URI isn't one of our own
    ui://scanova/... URIs — some clients request resources by
    "<connector_label>.<tool_name>" instead of the URI we returned in _meta.
    """
    resource = _RESOURCES.get(uri)
    if resource is not None:
        return resource
    tool_name = uri.rsplit(".", 1)[-1]
    return get_resource_for_tool(tool_name)


def get_resource_for_tool(tool_name: str) -> UIResource | None:
    """Look up the (single) UI resource associated with a tool, if any."""
    for resource in _RESOURCES.values():
        if tool_name in resource.tools:
            return resource
    return None


def read_resource_contents(uri: str) -> str | None:
    """Return the resource's file contents, or None if the URI is unknown or the file is missing."""
    resource = get_resource_by_uri(uri)
    if resource is None or not resource.path.is_file():
        return None
    return resource.path.read_text(encoding="utf-8")
