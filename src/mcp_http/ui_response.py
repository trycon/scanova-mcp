"""
UI response builder — the seam between a normalized tool result and the
final JSON-RPC serialization done by protocol.py.

Owns: the decision of whether a tool call should carry UI metadata, and the
shape of that metadata. Never touches the normalized envelope itself.
See docs/mcp-ui-architecture.md Part 4A (layer ownership) and Part 5A
(this abstraction, with rationale).

Multi-client support: rather than picking one UI convention, this emits
BOTH the OpenAI Apps SDK convention (_meta["openai/outputTemplate"]) and a
generic MCP-UI-style convention (_meta["ui"]["resourceUri"]) pointing at the
same resource. Per MCP Core, _meta is an arbitrary dict and unknown keys
must be ignored by conformant clients — so a client that only understands
one convention simply ignores the other key. This avoids branching on
client identity server-side (which Part 6 of the architecture doc found
has no reliable signal anyway).
"""

from config import UI_ELEMENTS_ENABLED
from mcp_http.ui_resources import get_resource_for_tool

# Per-tool enablement. Add tool names here as each subsequent phase's UI
# resource ships (see roadmap in docs/mcp-ui-architecture.md Part 16 /
# Part 11 priority column). Phase 1: set_qr_design. Phase 2: creation tools.
# Phase 3: download/media tools. Phase 5: remaining CRUD tools (folders,
# forms, lead lists, users) plus list_qr_codes. Phase 4: analytics
# dashboard (vanilla JS + hand-rolled inline-SVG bar chart, no Preact/Vite —
# a deliberate deviation from docs/mcp-ui-architecture.md's Phase 4
# recommendation to introduce a build pipeline; revisit if/when this
# dashboard's component needs outgrow hand-written JS).
UI_ENABLED_TOOLS = frozenset({
    "set_qr_design",
    "create_qr_code",
    "create_folder",
    "download_qr_code",
    "download_qr_printable",
    "list_qr_codes",
    "list_folders",
    "update_folder",
    "delete_folder",
    "move_qr_codes_to_folder",
    "unassign_qr_codes_from_folder",
    "list_forms",
    "retrieve_form",
    "update_form",
    "delete_form",
    "list_lead_lists",
    "retrieve_lead_list",
    "update_lead_list",
    "delete_lead_list",
    "list_users",
    "get_user",
    "add_user",
    "remove_user",
    "list_user_roles",
    "update_user_role",
    "get_account_stats",
    "get_qr_analytics",
    "export_analytics",
    "export_raw_scans",
})

OPENAI_OUTPUT_TEMPLATE_META_KEY = "openai/outputTemplate"


def _resource_meta(tool_name: str) -> dict | None:
    """Shared {_meta} shape linking a tool to its UI resource, or None if
    UI Elements are disabled, the tool isn't UI-enabled, or it has no
    registered resource."""
    if not UI_ELEMENTS_ENABLED or tool_name not in UI_ENABLED_TOOLS:
        return None
    resource = get_resource_for_tool(tool_name)
    if resource is None:
        return None
    return {
        OPENAI_OUTPUT_TEMPLATE_META_KEY: resource.uri,
        "ui": {"resourceUri": resource.uri},
    }


def attach_ui_metadata(tool_name: str, envelope: dict) -> dict:
    """
    Given a tool name and its already-normalized envelope, return
    {"envelope": envelope, "meta": <_meta dict or None>}.

    Never modifies `envelope` — purely additive. Returns meta=None when UI
    Elements are globally disabled, the tool isn't UI-enabled, or no
    resource is registered for it.
    """
    return {"envelope": envelope, "meta": _resource_meta(tool_name)}


def tool_descriptor_meta(tool_name: str) -> dict | None:
    """
    The `_meta` block a tool's `tools/list` descriptor must carry so a host
    (e.g. ChatGPT) can discover its associated UI resource up front — hosts
    read this at listing time and only call resources/read for tools that
    declare it here; declaring it solely on the tools/call result (as
    attach_ui_metadata does) is not sufficient for discovery.
    """
    return _resource_meta(tool_name)
