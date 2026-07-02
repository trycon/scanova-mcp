"""MCP tools/list definitions for the HTTP JSON-RPC endpoint."""

from mcp_http.annotations import (
    DESTRUCTIVE_TOOL_ANNOTATIONS_JSON,
    READ_ONLY_TOOL_ANNOTATIONS_JSON,
    WRITE_TOOL_ANNOTATIONS_JSON,
)
from mcp_http.output_schemas import TOOL_OUTPUT_SCHEMAS
from mcp_http.schemas import (
    # Docs bridge + Design
    QUERY_DOCS_SCHEMA,
    SET_QR_DESIGN_SCHEMA,
    # QR Code
    ATTACH_FORM_TO_QR_SCHEMA,
    ATTACH_LEAD_LIST_TO_QR_SCHEMA,
    CREATE_QR_PARAMS_SCHEMA,
    DOWNLOAD_QR_PARAMS_SCHEMA,
    DOWNLOAD_QR_PRINTABLE_SCHEMA,
    GET_QR_CATEGORIES_SCHEMA,
    LIST_QR_CODES_INPUT_SCHEMA,
    QRID_SCHEMA,
    UPDATE_QR_PARAMS_SCHEMA,
    # Analytics
    ACCOUNT_STATS_SCHEMA,
    EXPORT_ANALYTICS_SCHEMA,
    EXPORT_RAW_SCANS_SCHEMA,
    GET_QR_ANALYTICS_SCHEMA,
    # Folders
    CREATE_FOLDER_SCHEMA,
    DELETE_FOLDER_SCHEMA,
    FOLDER_ID_SCHEMA,
    LIST_FOLDERS_SCHEMA,
    MOVE_QR_TO_FOLDER_SCHEMA,
    UNASSIGN_QR_FROM_FOLDER_SCHEMA,
    UPDATE_FOLDER_SCHEMA,
    # Forms
    FORM_ID_SCHEMA,
    LIST_FORMS_SCHEMA,
    UPDATE_FORM_SCHEMA,
    # Lead Lists
    LEAD_LIST_ID_SCHEMA,
    LIST_LEAD_LISTS_SCHEMA,
    UPDATE_LEAD_LIST_SCHEMA,
    # Users
    ADD_USER_SCHEMA,
    UPDATE_USER_ROLE_SCHEMA,
    USER_ID_SCHEMA,
)


def _tool(name, title, description, annotations, input_schema):
    descriptor = {
        "name": name,
        "title": title,
        "description": description,
        "annotations": annotations,
        "inputSchema": input_schema,
    }
    output_schema = TOOL_OUTPUT_SCHEMAS.get(name)
    if output_schema:
        descriptor["outputSchema"] = output_schema
    return descriptor


def list_mcp_tools():
    """Return tool descriptors for MCP ``tools/list`` responses."""
    return [
        # ------------------------------------------------------------------ #
        # Docs MCP Bridge
        # ------------------------------------------------------------------ #
        _tool(
            "probe_docs_mcp",
            "Probe Scanova docs MCP",
            "Check connectivity to the Scanova docs MCP server and list its available tools",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {}},
        ),
        _tool(
            "query_docs",
            "Query Scanova API documentation",
            (
                "Bridge to the live Scanova docs MCP server. "
                "mode='search' runs a semantic search across all docs. "
                "mode='filesystem' runs a read-only shell command (cat, head, rg, tree, jq…) "
                "on the docs virtual filesystem — use this to read specific pages like "
                "/api-reference/references/pattern-info.mdx or /api-reference/references/category-list.mdx"
            ),
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            QUERY_DOCS_SCHEMA,
        ),
        # ------------------------------------------------------------------ #
        # QR Code Design
        # ------------------------------------------------------------------ #
        _tool(
            "get_qr_design_options",
            "Get QR code design options",
            (
                "Return the full catalog of available QR design options: all data pattern names, "
                "gradient styles, eye shape codes, frame IDs, error correction levels, fonts, "
                "and design tips. Use this before calling set_qr_design so users can see and "
                "choose from available options without writing any JSON."
            ),
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {}},
        ),
        _tool(
            "set_qr_design",
            "Set QR code design",
            (
                "Apply a visual design to an existing QR code using human-friendly named parameters. "
                "Only the fields you specify are changed — all other design settings (eye shape, pattern, "
                "colors, frame, etc.) are automatically preserved from the current design. "
                "Internally fetches the existing design and merges your changes on top. "
                "Call get_qr_design_options first to show users available patterns, eye shapes, and frames."
            ),
            WRITE_TOOL_ANNOTATIONS_JSON,
            SET_QR_DESIGN_SCHEMA,
        ),
        # ------------------------------------------------------------------ #
        # QR Code Management
        # ------------------------------------------------------------------ #
        _tool(
            "create_qr_code",
            "Create QR code",
            "Create a new QR code. Can be called with: create qr, make qr code, generate qr",
            WRITE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"params": CREATE_QR_PARAMS_SCHEMA}, "required": ["params"]},
        ),
        _tool(
            "list_qr_codes",
            "List QR codes",
            (
                "List QR codes and/or Pages in the account. By default returns all items (QR codes + Pages combined). "
                "Use is_page=false to list only QR Codes, or is_page=true to list only Pages. "
                "Use the count field from the response for accurate totals — do not infer counts from page size alone."
            ),
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            LIST_QR_CODES_INPUT_SCHEMA,
        ),
        _tool(
            "update_qr_code",
            "Update QR code",
            "Update an existing QR code",
            WRITE_TOOL_ANNOTATIONS_JSON,
            {
                "type": "object",
                "properties": {"qrid": QRID_SCHEMA, "params": UPDATE_QR_PARAMS_SCHEMA},
                "required": ["qrid", "params"],
            },
        ),
        _tool(
            "retrieve_qr_code",
            "Retrieve QR code details",
            "Get details of a specific QR code",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"qrid": QRID_SCHEMA}, "required": ["qrid"]},
        ),
        _tool(
            "download_qr_code",
            "Download QR code image",
            "Download QR code image in PNG, JPG, PDF, SVG, or EPS format",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {
                "type": "object",
                "properties": {"qrid": QRID_SCHEMA, "params": DOWNLOAD_QR_PARAMS_SCHEMA},
                "required": ["qrid"],
            },
        ),
        _tool(
            "activate_qr_code",
            "Activate QR code",
            "Activate a QR code",
            WRITE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"qrid": QRID_SCHEMA}, "required": ["qrid"]},
        ),
        _tool(
            "deactivate_qr_code",
            "Deactivate QR code",
            "Deactivate a QR code",
            WRITE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"qrid": QRID_SCHEMA}, "required": ["qrid"]},
        ),
        _tool(
            "delete_qr_code",
            "Delete QR code",
            "Permanently delete a QR code",
            DESTRUCTIVE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"qrid": QRID_SCHEMA}, "required": ["qrid"]},
        ),
        _tool(
            "get_qr_categories",
            "Get QR code categories",
            "List available QR code categories (URL, vCard, WiFi, Document, Social Media, etc.)",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            GET_QR_CATEGORIES_SCHEMA,
        ),
        _tool(
            "download_qr_printable",
            "Download printable QR code",
            "Generate a print-optimised PDF version of a QR code",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            DOWNLOAD_QR_PRINTABLE_SCHEMA,
        ),
        _tool(
            "attach_form_to_qr",
            "Attach form to QR code",
            "Attach a lead capture form to a QR code",
            WRITE_TOOL_ANNOTATIONS_JSON,
            ATTACH_FORM_TO_QR_SCHEMA,
        ),
        _tool(
            "detach_form_from_qr",
            "Detach form from QR code",
            "Remove the lead capture form from a QR code",
            WRITE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"qrid": QRID_SCHEMA}, "required": ["qrid"]},
        ),
        _tool(
            "attach_lead_list_to_qr",
            "Attach lead list to QR code",
            "Attach a lead list to a QR code for lead capture",
            WRITE_TOOL_ANNOTATIONS_JSON,
            ATTACH_LEAD_LIST_TO_QR_SCHEMA,
        ),
        _tool(
            "detach_lead_list_from_qr",
            "Detach lead list from QR code",
            "Remove the lead list from a QR code",
            WRITE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"qrid": QRID_SCHEMA}, "required": ["qrid"]},
        ),
        # ------------------------------------------------------------------ #
        # Analytics
        # ------------------------------------------------------------------ #
        _tool(
            "get_account_stats",
            "Get account statistics",
            "Retrieve account-level usage counters (total QR codes, scans, users, etc.)",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            ACCOUNT_STATS_SCHEMA,
        ),
        _tool(
            "get_qr_analytics",
            "Get QR code analytics",
            "Retrieve QR code performance metrics broken down by device, geography, date, etc.",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            GET_QR_ANALYTICS_SCHEMA,
        ),
        _tool(
            "export_analytics",
            "Export analytics report",
            "Export QR code analytics as an Excel or PDF report",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            EXPORT_ANALYTICS_SCHEMA,
        ),
        _tool(
            "export_raw_scans",
            "Export raw scan data",
            "Export row-level scan logs as CSV or Excel for custom BI pipelines",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            EXPORT_RAW_SCANS_SCHEMA,
        ),
        # ------------------------------------------------------------------ #
        # Folder Management
        # ------------------------------------------------------------------ #
        _tool(
            "create_folder",
            "Create folder",
            "Create a new folder to organize QR codes or pages",
            WRITE_TOOL_ANNOTATIONS_JSON,
            CREATE_FOLDER_SCHEMA,
        ),
        _tool(
            "list_folders",
            "List folders",
            "List all folders of a given type (qr or page)",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            LIST_FOLDERS_SCHEMA,
        ),
        _tool(
            "update_folder",
            "Rename folder",
            "Rename an existing folder",
            WRITE_TOOL_ANNOTATIONS_JSON,
            UPDATE_FOLDER_SCHEMA,
        ),
        _tool(
            "delete_folder",
            "Delete folder",
            (
                "Delete a folder. IMPORTANT: Before calling this tool, ask the user which action "
                "to take for QR codes inside the folder: (1) move to Uncategorized "
                "(move_to_uncategorized=true, delete_permanently=false) or (2) permanently delete "
                "them along with the folder (delete_permanently=true, move_to_uncategorized=false). "
                "Do not proceed without explicit user confirmation of the desired behavior."
            ),
            DESTRUCTIVE_TOOL_ANNOTATIONS_JSON,
            DELETE_FOLDER_SCHEMA,
        ),
        _tool(
            "move_qr_codes_to_folder",
            "Move QR codes to folder",
            "Move multiple QR codes into a folder",
            WRITE_TOOL_ANNOTATIONS_JSON,
            MOVE_QR_TO_FOLDER_SCHEMA,
        ),
        _tool(
            "unassign_qr_codes_from_folder",
            "Unassign QR codes from folder",
            "Remove multiple QR codes from a folder (moves them to uncategorized)",
            WRITE_TOOL_ANNOTATIONS_JSON,
            UNASSIGN_QR_FROM_FOLDER_SCHEMA,
        ),
        # ------------------------------------------------------------------ #
        # Forms
        # ------------------------------------------------------------------ #
        _tool(
            "list_forms",
            "List forms",
            "List all lead capture forms, optionally filtered by active status",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            LIST_FORMS_SCHEMA,
        ),
        _tool(
            "retrieve_form",
            "Retrieve form details",
            "Get detailed information about a specific form including its configuration",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"form_id": FORM_ID_SCHEMA}, "required": ["form_id"]},
        ),
        _tool(
            "update_form",
            "Update form",
            "Update a form's name or active status",
            WRITE_TOOL_ANNOTATIONS_JSON,
            UPDATE_FORM_SCHEMA,
        ),
        _tool(
            "delete_form",
            "Delete form",
            "Permanently delete a form",
            DESTRUCTIVE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"form_id": FORM_ID_SCHEMA}, "required": ["form_id"]},
        ),
        # ------------------------------------------------------------------ #
        # Lead Lists
        # ------------------------------------------------------------------ #
        _tool(
            "list_lead_lists",
            "List lead lists",
            "List all lead lists, optionally filtered by active status",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            LIST_LEAD_LISTS_SCHEMA,
        ),
        _tool(
            "retrieve_lead_list",
            "Retrieve lead list details",
            "Get detailed information about a specific lead list including webhook config",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {
                "type": "object",
                "properties": {"lead_list_id": LEAD_LIST_ID_SCHEMA},
                "required": ["lead_list_id"],
            },
        ),
        _tool(
            "update_lead_list",
            "Update lead list",
            "Update a lead list's name or active status",
            WRITE_TOOL_ANNOTATIONS_JSON,
            UPDATE_LEAD_LIST_SCHEMA,
        ),
        _tool(
            "delete_lead_list",
            "Delete lead list",
            "Permanently delete a lead list",
            DESTRUCTIVE_TOOL_ANNOTATIONS_JSON,
            {
                "type": "object",
                "properties": {"lead_list_id": LEAD_LIST_ID_SCHEMA},
                "required": ["lead_list_id"],
            },
        ),
        # ------------------------------------------------------------------ #
        # User Management
        # ------------------------------------------------------------------ #
        _tool(
            "list_users",
            "List users",
            "List all users in the account",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {}},
        ),
        _tool(
            "get_user",
            "Get user details",
            "Get details of a specific user",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"user_id": USER_ID_SCHEMA}, "required": ["user_id"]},
        ),
        _tool(
            "add_user",
            "Add user",
            "Invite a new user to the account by email",
            WRITE_TOOL_ANNOTATIONS_JSON,
            ADD_USER_SCHEMA,
        ),
        _tool(
            "remove_user",
            "Remove user",
            "Remove a user from the account",
            DESTRUCTIVE_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {"user_id": USER_ID_SCHEMA}, "required": ["user_id"]},
        ),
        _tool(
            "list_user_roles",
            "List user roles",
            "List all available user roles that can be assigned",
            READ_ONLY_TOOL_ANNOTATIONS_JSON,
            {"type": "object", "properties": {}},
        ),
        _tool(
            "update_user_role",
            "Update user role",
            "Change the role of an existing user",
            WRITE_TOOL_ANNOTATIONS_JSON,
            UPDATE_USER_ROLE_SCHEMA,
        ),
    ]


HTTP_AUTH_STUB_RESPONSE = {
    "error": "Please use the HTTP MCP endpoint for API key authentication",
}
