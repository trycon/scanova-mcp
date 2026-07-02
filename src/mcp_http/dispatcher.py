"""Route MCP tool calls to Scanova API functions."""

import json

import docs_client
from design import DESIGN_OPTIONS, apply_design, build_pattern_info, extract_design_args
from analytics import export_analytics, export_raw_scans, get_account_stats, get_qr_analytics
from folders import (
    create_folder,
    delete_folder,
    list_folders,
    move_qr_codes_to_folder,
    unassign_qr_codes_from_folder,
    update_folder,
)
from forms import delete_form, list_forms, retrieve_form, update_form
from leads import delete_lead_list, list_lead_lists, retrieve_lead_list, update_lead_list
from qrcode import (
    activate_qr_code,
    attach_form_to_qr,
    attach_lead_list_to_qr,
    create_qr_code,
    deactivate_qr_code,
    delete_qr_code,
    detach_form_from_qr,
    detach_lead_list_from_qr,
    download_qr_code,
    download_qr_printable,
    get_qr_categories,
    list_qr_codes,
    retrieve_qr_code,
    update_qr_code,
)
from users import add_user, get_user, list_user_roles, list_users, remove_user, update_user_role


def _set_qr_design_handler(arguments: dict, api_key: str) -> dict:
    """
    Build pattern_info from friendly params then PATCH the QR code.
    Fetches the existing design first so only the specified fields are changed —
    all other design settings (eye shape, pattern, colors, frame, etc.) are preserved.
    """
    qrid = arguments.get("qrid")
    if not qrid:
        return {"error": "qrid is required"}

    # Fetch existing QR to extract current design as base defaults
    existing_design_args: dict = {}
    existing_qr = retrieve_qr_code(qrid, api_key=api_key)
    if isinstance(existing_qr, dict):
        pi_str = existing_qr.get("pattern_info")
        if pi_str:
            try:
                existing_design_args = extract_design_args(json.loads(pi_str))
            except (json.JSONDecodeError, TypeError):
                pass

    # Collect only the design args the caller explicitly provided
    design_keys = {
        "pattern", "start_color", "end_color", "gradient_style", "dot_scale",
        "background_color", "eye_shape", "eye_inner_color", "eye_outer_color",
        "frame_id", "frame_primary_color", "frame_secondary_color",
        "frame_text_color", "frame_bg_color", "frame_category",
        "frame_text", "frame_text_placement", "frame_text_font",
        "shape_id", "shape_stroke_color", "shape_bg_color", "shape_pattern_color",
        "shape_stroke_width", "shape_margin", "error_correction", "logo_url", "padding",
    }
    user_args = {k: v for k, v in arguments.items() if k in design_keys and v is not None}

    # Merge: existing design as base, user overrides on top
    merged_args = {**existing_design_args, **user_args}
    pattern_info = build_pattern_info(**merged_args)
    return apply_design(qrid, pattern_info, api_key)


def _list_qr_params(arguments: dict) -> dict | None:
    qr_params = {}
    if arguments.get("page"):
        qr_params["page"] = arguments["page"]
    if arguments.get("limit"):
        qr_params["limit"] = arguments["limit"]
    if arguments.get("search"):
        qr_params["search"] = arguments["search"]
    if arguments.get("is_page") is not None:
        qr_params["is_page"] = arguments["is_page"]
    return qr_params or None


# Dispatch table: tool_name -> callable(arguments, api_key) -> result
_DISPATCH = {
    # ------------------------------------------------------------------ #
    # Docs MCP Bridge (api_key unused — public docs server)
    # ------------------------------------------------------------------ #
    "probe_docs_mcp": lambda a, k: docs_client.probe(),
    "query_docs": lambda a, k: (
        docs_client.search(a["query"]) if a.get("mode") == "search"
        else docs_client.filesystem(a["query"])
    ),
    # ------------------------------------------------------------------ #
    # QR Code Design
    # ------------------------------------------------------------------ #
    "get_qr_design_options": lambda a, k: DESIGN_OPTIONS,
    "set_qr_design": lambda a, k: _set_qr_design_handler(a, k),
    # ------------------------------------------------------------------ #
    # QR Code Management
    # ------------------------------------------------------------------ #
    "create_qr_code": lambda a, k: create_qr_code(a.get("params"), api_key=k),
    "list_qr_codes": lambda a, k: list_qr_codes(_list_qr_params(a), api_key=k),
    "update_qr_code": lambda a, k: update_qr_code(a.get("qrid"), a.get("params"), api_key=k),
    "retrieve_qr_code": lambda a, k: retrieve_qr_code(a.get("qrid"), api_key=k),
    "download_qr_code": lambda a, k: download_qr_code(a.get("qrid"), a.get("params"), api_key=k),
    "activate_qr_code": lambda a, k: activate_qr_code(a.get("qrid"), api_key=k),
    "deactivate_qr_code": lambda a, k: deactivate_qr_code(a.get("qrid"), api_key=k),
    "delete_qr_code": lambda a, k: delete_qr_code(a.get("qrid"), api_key=k),
    "get_qr_categories": lambda a, k: get_qr_categories(
        view_type=a.get("view_type", "all"), api_key=k
    ),
    "download_qr_printable": lambda a, k: download_qr_printable(
        qrid=a.get("qrid"),
        size=a.get("size", 600),
        name=a.get("name"),
        api_key=k,
    ),
    "attach_form_to_qr": lambda a, k: attach_form_to_qr(
        qrid=a.get("qrid"), form_id=a.get("form_id"), api_key=k
    ),
    "detach_form_from_qr": lambda a, k: detach_form_from_qr(a.get("qrid"), api_key=k),
    "attach_lead_list_to_qr": lambda a, k: attach_lead_list_to_qr(
        qrid=a.get("qrid"), lead_list_id=a.get("lead_list_id"), api_key=k
    ),
    "detach_lead_list_from_qr": lambda a, k: detach_lead_list_from_qr(a.get("qrid"), api_key=k),
    # ------------------------------------------------------------------ #
    # Analytics
    # ------------------------------------------------------------------ #
    "get_account_stats": lambda a, k: get_account_stats(
        fields=a.get("fields"), api_key=k
    ),
    "get_qr_analytics": lambda a, k: get_qr_analytics(
        filter_by=a["filter_by"],
        q=a["q"],
        types=a["types"],
        from_date=a["from_date"],
        to_date=a["to_date"],
        exclude_bot_scan=a.get("exclude_bot_scan", False),
        api_key=k,
    ),
    "export_analytics": lambda a, k: export_analytics(
        filter_by=a["filter_by"],
        q=a["q"],
        from_date=a["from_date"],
        to_date=a["to_date"],
        file_format=a.get("file_format", "xlsx"),
        exclude_bot_scan=a.get("exclude_bot_scan", False),
        api_key=k,
    ),
    "export_raw_scans": lambda a, k: export_raw_scans(
        filter_by=a["filter_by"],
        q=a["q"],
        from_date=a["from_date"],
        to_date=a["to_date"],
        file_format=a.get("file_format", "csv"),
        scan_type=a.get("scan_type", "raw"),
        exclude_bot_scan=a.get("exclude_bot_scan", False),
        api_key=k,
    ),
    # ------------------------------------------------------------------ #
    # Folder Management
    # ------------------------------------------------------------------ #
    "create_folder": lambda a, k: create_folder(
        name=a["name"], folder_type=a["folder_type"], api_key=k
    ),
    "list_folders": lambda a, k: list_folders(
        folder_type=a["folder_type"], api_key=k
    ),
    "update_folder": lambda a, k: update_folder(
        folder_id=a["folder_id"], name=a["name"], api_key=k
    ),
    "delete_folder": lambda a, k: delete_folder(
        folder_id=a["folder_id"],
        move_to_uncategorized=a.get("move_to_uncategorized", True),
        delete_permanently=a.get("delete_permanently", False),
        api_key=k,
    ),
    "move_qr_codes_to_folder": lambda a, k: move_qr_codes_to_folder(
        folder_id=a["folder_id"],
        qr_code_ids=a["qr_code_ids"],
        from_folder_id=a.get("from_folder_id"),
        api_key=k,
    ),
    "unassign_qr_codes_from_folder": lambda a, k: unassign_qr_codes_from_folder(
        folder_id=a["folder_id"], qr_code_ids=a["qr_code_ids"], api_key=k
    ),
    # ------------------------------------------------------------------ #
    # Forms
    # ------------------------------------------------------------------ #
    "list_forms": lambda a, k: list_forms(is_active=a.get("is_active"), api_key=k),
    "retrieve_form": lambda a, k: retrieve_form(form_id=a["form_id"], api_key=k),
    "update_form": lambda a, k: update_form(
        form_id=a["form_id"],
        name=a.get("name"),
        is_active=a.get("is_active"),
        api_key=k,
    ),
    "delete_form": lambda a, k: delete_form(form_id=a["form_id"], api_key=k),
    # ------------------------------------------------------------------ #
    # Lead Lists
    # ------------------------------------------------------------------ #
    "list_lead_lists": lambda a, k: list_lead_lists(is_active=a.get("is_active"), api_key=k),
    "retrieve_lead_list": lambda a, k: retrieve_lead_list(
        lead_list_id=a["lead_list_id"], api_key=k
    ),
    "update_lead_list": lambda a, k: update_lead_list(
        lead_list_id=a["lead_list_id"],
        name=a.get("name"),
        is_active=a.get("is_active"),
        api_key=k,
    ),
    "delete_lead_list": lambda a, k: delete_lead_list(
        lead_list_id=a["lead_list_id"], api_key=k
    ),
    # ------------------------------------------------------------------ #
    # User Management
    # ------------------------------------------------------------------ #
    "list_users": lambda a, k: list_users(api_key=k),
    "get_user": lambda a, k: get_user(user_id=a["user_id"], api_key=k),
    "add_user": lambda a, k: add_user(email=a["email"], role=a["role"], api_key=k),
    "remove_user": lambda a, k: remove_user(user_id=a["user_id"], api_key=k),
    "list_user_roles": lambda a, k: list_user_roles(api_key=k),
    "update_user_role": lambda a, k: update_user_role(
        user_id=a["user_id"], role=a["role"], api_key=k
    ),
}


def execute_tool(tool_name: str, arguments: dict, api_key: str):
    """Invoke the Scanova backend for a named MCP tool."""
    handler = _DISPATCH.get(tool_name)
    if handler is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    return handler(arguments, api_key)
