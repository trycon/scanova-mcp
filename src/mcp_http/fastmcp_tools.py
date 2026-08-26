"""FastMCP tool registrations (stdio / streamable-http transport)."""

import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP

from mcp_http.annotations import (
    DESTRUCTIVE_TOOL_ANNOTATIONS,
    READ_ONLY_TOOL_ANNOTATIONS,
    WRITE_TOOL_ANNOTATIONS,
)
from mcp_http.output_schemas import TOOL_OUTPUT_SCHEMAS

log = logging.getLogger("mcp")


def _get_api_key() -> str:
    from config import MCP_ACCESS_TOKEN
    return MCP_ACCESS_TOKEN or ""


def _run(tool_name: str, **kwargs) -> dict:
    """Execute a tool via the dispatcher using MCP_ACCESS_TOKEN."""
    from mcp_http.dispatcher import execute_tool
    api_key = _get_api_key()
    try:
        return execute_tool(tool_name, kwargs, api_key)
    except Exception as exc:
        log.exception("Tool %s failed", tool_name)
        return {"error": str(exc)}


def register_fastmcp_tools(server: FastMCP) -> None:
    """Register all Scanova tools on a FastMCP server instance."""

    # ------------------------------------------------------------------ #
    # Docs MCP Bridge
    # ------------------------------------------------------------------ #

    @server.tool(
        "probe_docs_mcp",
        description="Check connectivity to the Scanova docs MCP server and list its available tools",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def probe_docs_mcp_tool():
        return _run("probe_docs_mcp")

    @server.tool(
        "query_docs",
        description=(
            "Bridge to the live Scanova docs MCP. "
            "mode='search' for semantic search; mode='filesystem' for shell commands on the docs filesystem."
        ),
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def query_docs_tool(mode: str = "search", query: str = None):
        return _run("query_docs", mode=mode, query=query)

    # ------------------------------------------------------------------ #
    # QR Code Design
    # ------------------------------------------------------------------ #

    @server.tool(
        "get_qr_design_options",
        description=(
            "Return all available QR design options: pattern names, eye shape codes, "
            "frame IDs, gradient styles, error correction levels, and tips. "
            "Call this first so users can choose without writing any JSON."
        ),
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def get_qr_design_options_tool():
        return _run("get_qr_design_options")

    @server.tool(
        "set_qr_design",
        description=(
            "Apply a visual design to an existing QR code using human-friendly named parameters. "
            "No JSON required — the server builds pattern_info internally. "
            "Call get_qr_design_options first to show users the available options."
        ),
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def set_qr_design_tool(
        qrid: str = None,
        pattern: str = "Default",
        start_color: str = "#000000",
        end_color: str = None,
        gradient_style: str = "None",
        dot_scale: int = None,
        background_color: str = "#ffffff",
        eye_shape: str = "Shape4",
        eye_inner_color: str = "#000000",
        eye_outer_color: str = "#000000",
        frame_id: int = None,
        frame_primary_color: str = None,
        frame_secondary_color: str = None,
        frame_text_color: str = "#FFFFFF",
        frame_bg_color: str = "#FFFFFF",
        frame_category: str = "url",
        frame_text: str = None,
        frame_text_placement: str = "center",
        frame_text_font: str = "Montserrat",
        shape_id: str = None,
        error_correction: str = "M",
        logo_url: str = None,
    ):
        return _run(
            "set_qr_design",
            qrid=qrid,
            pattern=pattern,
            start_color=start_color,
            end_color=end_color,
            gradient_style=gradient_style,
            dot_scale=dot_scale,
            background_color=background_color,
            eye_shape=eye_shape,
            eye_inner_color=eye_inner_color,
            eye_outer_color=eye_outer_color,
            frame_id=frame_id,
            frame_primary_color=frame_primary_color,
            frame_secondary_color=frame_secondary_color,
            frame_text_color=frame_text_color,
            frame_bg_color=frame_bg_color,
            frame_category=frame_category,
            frame_text=frame_text,
            frame_text_placement=frame_text_placement,
            frame_text_font=frame_text_font,
            shape_id=shape_id,
            error_correction=error_correction,
            logo_url=logo_url,
        )

    # ------------------------------------------------------------------ #
    # QR Code Management
    # ------------------------------------------------------------------ #

    @server.tool()
    def get_scanova_data(query: str) -> str:
        return "This is a test response"

    @server.tool(
        "create_qr_code",
        description="Create a new QR code. Can be called with: create qr, make qr code, generate qr, new qr code, add qr code",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def create_qr_code_tool(params: dict = None):
        return _run("create_qr_code", params=params)

    @server.tool(
        "list_qr_codes",
        description="List QR codes. Can be called with: list qr codes, fetch qr list, get qr codes, show qr codes",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def list_qr_codes_tool(page: int = 1, limit: int = 10, search: str = None):
        return _run("list_qr_codes", page=page, limit=limit, search=search)

    @server.tool(
        "update_qr_code",
        description="Update an existing QR code",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def update_qr_code_tool(qrid: str = None, params: dict = None):
        return _run("update_qr_code", qrid=qrid, params=params)

    @server.tool(
        "retrieve_qr_code",
        description="Get details of a specific QR code",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def retrieve_qr_code_tool(qrid: str = None):
        return _run("retrieve_qr_code", qrid=qrid)

    @server.tool(
        "download_qr_code",
        description="Download QR code image in PNG, JPG, PDF, SVG, or EPS format",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def download_qr_code_tool(qrid: str = None, params: dict = None):
        return _run("download_qr_code", qrid=qrid, params=params)

    @server.tool(
        "activate_qr_code",
        description="Activate a QR code",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def activate_qr_code_tool(qrid: str = None):
        return _run("activate_qr_code", qrid=qrid)

    @server.tool(
        "deactivate_qr_code",
        description="Deactivate a QR code",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def deactivate_qr_code_tool(qrid: str = None):
        return _run("deactivate_qr_code", qrid=qrid)

    @server.tool(
        "delete_qr_code",
        description="Permanently delete a QR code",
        annotations=DESTRUCTIVE_TOOL_ANNOTATIONS,
    )
    def delete_qr_code_tool(qrid: str = None):
        return _run("delete_qr_code", qrid=qrid)

    @server.tool(
        "get_qr_categories",
        description="List available QR code categories (URL, vCard, WiFi, Document, Social Media, etc.)",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def get_qr_categories_tool(view_type: str = "all"):
        return _run("get_qr_categories", view_type=view_type)

    @server.tool(
        "download_qr_printable",
        description="Generate a print-optimised PDF version of a QR code",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def download_qr_printable_tool(qrid: str = None, size: int = 600, name: str = None):
        return _run("download_qr_printable", qrid=qrid, size=size, name=name)

    @server.tool(
        "attach_form_to_qr",
        description="Attach a lead capture form to a QR code",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def attach_form_to_qr_tool(qrid: str = None, form_id: int = None):
        return _run("attach_form_to_qr", qrid=qrid, form_id=form_id)

    @server.tool(
        "detach_form_from_qr",
        description="Remove the lead capture form from a QR code",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def detach_form_from_qr_tool(qrid: str = None):
        return _run("detach_form_from_qr", qrid=qrid)

    @server.tool(
        "attach_lead_list_to_qr",
        description="Attach a lead list to a QR code for lead capture",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def attach_lead_list_to_qr_tool(qrid: str = None, lead_list_id: int = None):
        return _run("attach_lead_list_to_qr", qrid=qrid, lead_list_id=lead_list_id)

    @server.tool(
        "detach_lead_list_from_qr",
        description="Remove the lead list from a QR code",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def detach_lead_list_from_qr_tool(qrid: str = None):
        return _run("detach_lead_list_from_qr", qrid=qrid)

    # ------------------------------------------------------------------ #
    # Analytics
    # ------------------------------------------------------------------ #

    @server.tool(
        "get_account_stats",
        description="Get account-level usage statistics (total QR codes, scans, users, etc.)",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def get_account_stats_tool(fields: list = None):
        return _run("get_account_stats", fields=fields)

    @server.tool(
        "get_qr_analytics",
        description="Get QR code performance metrics broken down by device, geography, date, etc.",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def get_qr_analytics_tool(
        filter_by: str = None,
        q: list = None,
        types: list = None,
        from_date: str = None,
        to_date: str = None,
        exclude_bot_scan: bool = False,
    ):
        return _run(
            "get_qr_analytics",
            filter_by=filter_by,
            q=q,
            types=types,
            from_date=from_date,
            to_date=to_date,
            exclude_bot_scan=exclude_bot_scan,
        )

    # export_analytics / export_raw_scans removed for now (2026-08-24) — not
    # registered as tools, but the underlying analytics.py functions are
    # left in place for an easy re-enable later.

    # ------------------------------------------------------------------ #
    # Folder Management
    # ------------------------------------------------------------------ #

    @server.tool(
        "create_folder",
        description="Create a new folder to organize QR codes or pages",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def create_folder_tool(name: str = None, folder_type: str = None):
        return _run("create_folder", name=name, folder_type=folder_type)

    @server.tool(
        "list_folders",
        description="List all folders of a given type (qr or page)",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def list_folders_tool(folder_type: str = None):
        return _run("list_folders", folder_type=folder_type)

    @server.tool(
        "update_folder",
        description="Rename an existing folder",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def update_folder_tool(folder_id: int = None, name: str = None):
        return _run("update_folder", folder_id=folder_id, name=name)

    @server.tool(
        "delete_folder",
        description="Delete a folder, optionally moving its QR codes to uncategorized",
        annotations=DESTRUCTIVE_TOOL_ANNOTATIONS,
    )
    def delete_folder_tool(
        folder_id: int = None,
        move_to_uncategorized: bool = True,
        delete_permanently: bool = False,
    ):
        return _run(
            "delete_folder",
            folder_id=folder_id,
            move_to_uncategorized=move_to_uncategorized,
            delete_permanently=delete_permanently,
        )

    @server.tool(
        "move_qr_codes_to_folder",
        description="Move multiple QR codes into a folder",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def move_qr_codes_to_folder_tool(
        folder_id: int = None,
        qr_code_ids: list = None,
        from_folder_id: int = None,
    ):
        return _run(
            "move_qr_codes_to_folder",
            folder_id=folder_id,
            qr_code_ids=qr_code_ids,
            from_folder_id=from_folder_id,
        )

    @server.tool(
        "unassign_qr_codes_from_folder",
        description="Remove multiple QR codes from a folder",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def unassign_qr_codes_from_folder_tool(folder_id: int = None, qr_code_ids: list = None):
        return _run("unassign_qr_codes_from_folder", folder_id=folder_id, qr_code_ids=qr_code_ids)

    # ------------------------------------------------------------------ #
    # Forms
    # ------------------------------------------------------------------ #

    @server.tool(
        "list_forms",
        description="List all lead capture forms",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def list_forms_tool(is_active: bool = None):
        return _run("list_forms", is_active=is_active)

    @server.tool(
        "retrieve_form",
        description="Get detailed information about a specific form",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def retrieve_form_tool(form_id: str = None):
        return _run("retrieve_form", form_id=form_id)

    @server.tool(
        "update_form",
        description="Update a form's name or active status",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def update_form_tool(form_id: str = None, name: str = None, is_active: bool = None):
        return _run("update_form", form_id=form_id, name=name, is_active=is_active)

    @server.tool(
        "delete_form",
        description="Permanently delete a form",
        annotations=DESTRUCTIVE_TOOL_ANNOTATIONS,
    )
    def delete_form_tool(form_id: str = None):
        return _run("delete_form", form_id=form_id)

    # ------------------------------------------------------------------ #
    # Lead Lists
    # ------------------------------------------------------------------ #

    @server.tool(
        "list_lead_lists",
        description="List all lead lists",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def list_lead_lists_tool(is_active: bool = None):
        return _run("list_lead_lists", is_active=is_active)

    @server.tool(
        "retrieve_lead_list",
        description="Get detailed information about a specific lead list",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def retrieve_lead_list_tool(lead_list_id: str = None):
        return _run("retrieve_lead_list", lead_list_id=lead_list_id)

    @server.tool(
        "update_lead_list",
        description="Update a lead list's name or active status",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def update_lead_list_tool(lead_list_id: str = None, name: str = None, is_active: bool = None):
        return _run("update_lead_list", lead_list_id=lead_list_id, name=name, is_active=is_active)

    @server.tool(
        "delete_lead_list",
        description="Permanently delete a lead list",
        annotations=DESTRUCTIVE_TOOL_ANNOTATIONS,
    )
    def delete_lead_list_tool(lead_list_id: str = None):
        return _run("delete_lead_list", lead_list_id=lead_list_id)

    # ------------------------------------------------------------------ #
    # User Management
    # ------------------------------------------------------------------ #

    @server.tool(
        "list_users",
        description="List all users in the account",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def list_users_tool():
        return _run("list_users")

    @server.tool(
        "get_user",
        description="Get details of a specific user",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def get_user_tool(user_id: str = None):
        return _run("get_user", user_id=user_id)

    @server.tool(
        "add_user",
        description="Invite a new user to the account by email",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def add_user_tool(email: str = None, role: str = None):
        return _run("add_user", email=email, role=role)

    @server.tool(
        "remove_user",
        description="Remove a user from the account",
        annotations=DESTRUCTIVE_TOOL_ANNOTATIONS,
    )
    def remove_user_tool(user_id: str = None):
        return _run("remove_user", user_id=user_id)

    @server.tool(
        "list_user_roles",
        description="List all available user roles that can be assigned",
        annotations=READ_ONLY_TOOL_ANNOTATIONS,
    )
    def list_user_roles_tool():
        return _run("list_user_roles")

    @server.tool(
        "update_user_role",
        description="Change the role of an existing user",
        annotations=WRITE_TOOL_ANNOTATIONS,
    )
    def update_user_role_tool(user_id: str = None, access_level: str = None):
        return _run("update_user_role", user_id=user_id, access_level=access_level)

    # ------------------------------------------------------------------ #
    # Inject output schemas into registered tool objects.
    # cached_property stores its value in __dict__, so writing there
    # preempts the lazy calculation and surfaces outputSchema in tools/list.
    # ------------------------------------------------------------------ #
    registered = server._tool_manager._tools
    for tool_name, schema in TOOL_OUTPUT_SCHEMAS.items():
        tool_obj = registered.get(tool_name)
        if tool_obj is not None:
            tool_obj.__dict__["output_schema"] = schema
