"""Output schema definitions for all MCP tools (JSON Schema format)."""

# ── Shared building blocks ─────────────────────────────────────────────────── #

_ERROR = {"error": {"type": "string", "description": "Human-readable error message"}}

_QR_OBJECT = {
    "type": "object",
    "description": "A Scanova QR code object",
    "properties": {
        "qrid": {"type": "string", "description": "Unique QR code identifier"},
        "name": {"type": "string", "description": "Display name of the QR code"},
        "category": {"type": "integer", "description": "QR code category ID (1=URL, 11=vCard, etc.)"},
        "qr_type": {"type": "string", "enum": ["dy", "st"], "description": "Dynamic or static"},
        "status": {"type": "string", "enum": ["active", "inactive"], "description": "Activation status"},
        "info": {"type": "object", "description": "Payload data (type + data fields)"},
        "pattern_info": {"type": "string", "description": "JSON string with visual design settings"},
        "created_at": {"type": "string", "description": "ISO 8601 creation timestamp"},
        "updated_at": {"type": "string", "description": "ISO 8601 last-modified timestamp"},
        **_ERROR,
    },
}

_FOLDER_OBJECT = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "folder_type": {"type": "string"},
        "qr_count": {"type": "integer"},
        **_ERROR,
    },
}

_FORM_OBJECT = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "is_active": {"type": "boolean"},
        "fields": {"type": "array", "items": {"type": "object"}},
        **_ERROR,
    },
}

_LEAD_LIST_OBJECT = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "is_active": {"type": "boolean"},
        "webhook_url": {"type": "string"},
        **_ERROR,
    },
}

_USER_OBJECT = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string"},
        "role": {"type": "string"},
        "status": {"type": "string"},
        **_ERROR,
    },
}

# ── Docs MCP Bridge ────────────────────────────────────────────────────────── #

PROBE_DOCS_MCP_OUTPUT = {
    "type": "object",
    "properties": {
        "connected": {"type": "boolean", "description": "True if the docs MCP server responded"},
        "server": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            },
        },
        "available_tools": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of tool names offered by the docs MCP server",
        },
        **_ERROR,
    },
}

QUERY_DOCS_OUTPUT = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean", "description": "True when the docs server returned a result"},
        "result": {"type": "string", "description": "Text content from the documentation"},
        "error": {"type": "string", "description": "Error message when ok is false"},
    },
}

# ── QR Code Design ─────────────────────────────────────────────────────────── #

GET_QR_DESIGN_OPTIONS_OUTPUT = {
    "type": "object",
    "properties": {
        "data_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "All valid pattern names for the pattern field",
        },
        "eye_shapes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "All valid eye shape codes (Shape0, Shape1, …)",
        },
        "gradient_styles": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Gradient options: None, Horizontal, Vertical, Diagonal, Radial",
        },
        "frame_ids": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "Available frame template IDs",
        },
        "shape_container_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Available shape container IDs",
        },
        "error_correction": {
            "type": "object",
            "description": "Error correction levels: L (7%), M (15%), Q (25%), H (30%)",
            "properties": {
                "L": {"type": "string"},
                "M": {"type": "string"},
                "Q": {"type": "string"},
                "H": {"type": "string"},
            },
        },
        "fonts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Available font families for frame text",
        },
        "tips": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Design tips and recommendations",
        },
    },
}

SET_QR_DESIGN_OUTPUT = {
    "type": "object",
    "description": "Updated QR code with the new design applied",
    "properties": {
        **_QR_OBJECT["properties"],
    },
}

# ── QR Code Management ─────────────────────────────────────────────────────── #

CREATE_QR_CODE_OUTPUT = _QR_OBJECT

# Matches normalizer.py's actual envelope for paginated list tools: the
# full {ok, data: {count, results}, pagination, error, ...} shape emitted
# as structuredContent — not just the inner "data" object.
LIST_QR_CODES_OUTPUT = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "data": {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "results": {"type": "array", "items": _QR_OBJECT},
            },
            "description": "Page of QR code objects with the total count",
        },
        "pagination": {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": ["integer", "null"]},
                "previous": {"type": ["integer", "null"]},
            },
        },
        **_ERROR,
    },
}

UPDATE_QR_CODE_OUTPUT = _QR_OBJECT
RETRIEVE_QR_CODE_OUTPUT = _QR_OBJECT
ACTIVATE_QR_CODE_OUTPUT = _QR_OBJECT
DEACTIVATE_QR_CODE_OUTPUT = _QR_OBJECT

DOWNLOAD_QR_CODE_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        "content_type": {
            "type": "string",
            "description": "MIME type, e.g. image/png, image/svg+xml, application/pdf",
        },
        **_ERROR,
    },
}

DELETE_QR_CODE_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string", "example": "QR code deleted"},
        **_ERROR,
    },
}

GET_QR_CATEGORIES_OUTPUT = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "slug": {"type": "string"},
                },
            },
        },
        **_ERROR,
    },
}

DOWNLOAD_QR_PRINTABLE_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "content_type": {"type": "string", "example": "application/pdf"},
        "content_length": {"type": "integer", "description": "File size in bytes"},
        "size": {"type": "integer", "description": "Requested pixel size"},
        "name": {"type": "string"},
        **_ERROR,
    },
}

ATTACH_DETACH_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        **_ERROR,
    },
}

# ── Analytics ─────────────────────────────────────────────────────────────── #

GET_ACCOUNT_STATS_OUTPUT = {
    "type": "object",
    "description": "Account-level usage counters",
    "properties": {
        "total_qr_codes": {"type": "integer"},
        "total_scans": {"type": "integer"},
        "total_users": {"type": "integer"},
        "active_qr_codes": {"type": "integer"},
        **_ERROR,
    },
}

GET_QR_ANALYTICS_OUTPUT = {
    "type": "object",
    "description": "QR code scan metrics broken down by the requested dimension",
    "properties": {
        "data": {"type": "array", "items": {"type": "object"}},
        "total": {"type": "integer"},
        **_ERROR,
    },
}

EXPORT_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "content_type": {"type": "string"},
        "content_length": {"type": "integer"},
        "download_url": {"type": "string"},
        **_ERROR,
    },
}

# ── Folder Management ─────────────────────────────────────────────────────── #

CREATE_FOLDER_OUTPUT = _FOLDER_OBJECT
UPDATE_FOLDER_OUTPUT = _FOLDER_OBJECT

LIST_FOLDERS_OUTPUT = {
    "type": "object",
    "properties": {
        "data": {"type": "array", "items": _FOLDER_OBJECT},
        **_ERROR,
    },
}

DELETE_FOLDER_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        **_ERROR,
    },
}

MOVE_QR_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "moved": {"type": "integer", "description": "Number of QR codes moved"},
        **_ERROR,
    },
}

# ── Forms ─────────────────────────────────────────────────────────────────── #

LIST_FORMS_OUTPUT = {
    "type": "object",
    "properties": {
        "data": {"type": "array", "items": _FORM_OBJECT},
        **_ERROR,
    },
}

RETRIEVE_FORM_OUTPUT = _FORM_OBJECT
UPDATE_FORM_OUTPUT = _FORM_OBJECT

DELETE_FORM_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        **_ERROR,
    },
}

# ── Lead Lists ────────────────────────────────────────────────────────────── #

LIST_LEAD_LISTS_OUTPUT = {
    "type": "object",
    "properties": {
        "data": {"type": "array", "items": _LEAD_LIST_OBJECT},
        **_ERROR,
    },
}

RETRIEVE_LEAD_LIST_OUTPUT = _LEAD_LIST_OBJECT
UPDATE_LEAD_LIST_OUTPUT = _LEAD_LIST_OBJECT

DELETE_LEAD_LIST_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        **_ERROR,
    },
}

# ── User Management ───────────────────────────────────────────────────────── #

LIST_USERS_OUTPUT = {
    "type": "object",
    "properties": {
        "data": {"type": "array", "items": _USER_OBJECT},
        **_ERROR,
    },
}

GET_USER_OUTPUT = _USER_OBJECT
ADD_USER_OUTPUT = _USER_OBJECT
UPDATE_USER_ROLE_OUTPUT = _USER_OBJECT

REMOVE_USER_OUTPUT = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        **_ERROR,
    },
}

LIST_USER_ROLES_OUTPUT = {
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
        },
        **_ERROR,
    },
}

# ── Lookup table: tool_name → outputSchema ────────────────────────────────── #

TOOL_OUTPUT_SCHEMAS: dict[str, dict] = {
    # Docs bridge
    "probe_docs_mcp": PROBE_DOCS_MCP_OUTPUT,
    "query_docs": QUERY_DOCS_OUTPUT,
    # Design
    "get_qr_design_options": GET_QR_DESIGN_OPTIONS_OUTPUT,
    "set_qr_design": SET_QR_DESIGN_OUTPUT,
    # QR management
    "create_qr_code": CREATE_QR_CODE_OUTPUT,
    "list_qr_codes": LIST_QR_CODES_OUTPUT,
    "update_qr_code": UPDATE_QR_CODE_OUTPUT,
    "retrieve_qr_code": RETRIEVE_QR_CODE_OUTPUT,
    "download_qr_code": DOWNLOAD_QR_CODE_OUTPUT,
    "activate_qr_code": ACTIVATE_QR_CODE_OUTPUT,
    "deactivate_qr_code": DEACTIVATE_QR_CODE_OUTPUT,
    "delete_qr_code": DELETE_QR_CODE_OUTPUT,
    "get_qr_categories": GET_QR_CATEGORIES_OUTPUT,
    "download_qr_printable": DOWNLOAD_QR_PRINTABLE_OUTPUT,
    "attach_form_to_qr": ATTACH_DETACH_OUTPUT,
    "detach_form_from_qr": ATTACH_DETACH_OUTPUT,
    "attach_lead_list_to_qr": ATTACH_DETACH_OUTPUT,
    "detach_lead_list_from_qr": ATTACH_DETACH_OUTPUT,
    # Analytics
    "get_account_stats": GET_ACCOUNT_STATS_OUTPUT,
    "get_qr_analytics": GET_QR_ANALYTICS_OUTPUT,
    "export_analytics": EXPORT_OUTPUT,
    "export_raw_scans": EXPORT_OUTPUT,
    # Folders
    "create_folder": CREATE_FOLDER_OUTPUT,
    "list_folders": LIST_FOLDERS_OUTPUT,
    "update_folder": UPDATE_FOLDER_OUTPUT,
    "delete_folder": DELETE_FOLDER_OUTPUT,
    "move_qr_codes_to_folder": MOVE_QR_OUTPUT,
    "unassign_qr_codes_from_folder": MOVE_QR_OUTPUT,
    # Forms
    "list_forms": LIST_FORMS_OUTPUT,
    "retrieve_form": RETRIEVE_FORM_OUTPUT,
    "update_form": UPDATE_FORM_OUTPUT,
    "delete_form": DELETE_FORM_OUTPUT,
    # Lead lists
    "list_lead_lists": LIST_LEAD_LISTS_OUTPUT,
    "retrieve_lead_list": RETRIEVE_LEAD_LIST_OUTPUT,
    "update_lead_list": UPDATE_LEAD_LIST_OUTPUT,
    "delete_lead_list": DELETE_LEAD_LIST_OUTPUT,
    # Users
    "list_users": LIST_USERS_OUTPUT,
    "get_user": GET_USER_OUTPUT,
    "add_user": ADD_USER_OUTPUT,
    "remove_user": REMOVE_USER_OUTPUT,
    "list_user_roles": LIST_USER_ROLES_OUTPUT,
    "update_user_role": UPDATE_USER_ROLE_OUTPUT,
}
