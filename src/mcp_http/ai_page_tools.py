"""AI pages: the whole-page HTML landing pages of Scanova's AI Studio (app.scanova.io/qr/new/ai).

An AI page is a QR code of the ``ai`` category whose ``info`` is ``{"full_html_page": "<html…>"}``, with an AI
Studio session (qcg-backend ``ai_assistance``) holding its versions. Scova — Trycon's assistant in the app — makes
these pages with its own pipeline (design, build, check in a browser, review) and saves them here, so they open in AI
Studio like any other: the version history is there to refine from, and Scanova compiles the page's Tailwind.

- ``get_ai_page_quota``: the plan's AI page credits (``AI_QR_TOKENS``) — used this month, top-ups, what's left.
- ``get_ai_page``: one AI page's current HTML (its draft if there is one), to change it.
- ``save_ai_page``: a finished page as a new AI Studio version (``ai-assistance/qr-sessions/external/``: Tailwind
  compiled, one credit used), then the QR code's draft — a new AI QR code, or the given one's draft. Nothing goes
  live: publishing is done in AI Studio.
"""

import json

from mcp_http.more_tools import _SEGMENT, MoreTool, _input, _missing, _object
from scanova_api import NO_KEY, scanova

STUDIO_URL = "https://app.scanova.io/qr/{qrid}/ai"
AI_CATEGORY = "ai"
QUOTA = "AI_QR_TOKENS"
MAX_HTML_CHARS = 1_000_000
MAX_PROMPT_CHARS = 4000
DEFAULT_NAME = "AI landing page"


def _failed(result) -> bool:
    return not isinstance(result, dict) or "error" in result


def _parsed(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return None
    return value if isinstance(value, dict) else None


def _category_slug(qr: dict) -> str:
    cat = qr.get("category")
    return (cat.get("slug") if isinstance(cat, dict) else None) or ""


def _html_of(info) -> str:
    env = _parsed(info)
    return env.get("full_html_page") if isinstance(env, dict) and isinstance(env.get("full_html_page"), str) else ""


def _preview_url(qrid: str, api_key: str):
    token = scanova("POST", f"qr/{qrid}/preview-token/", api_key, body={})
    if not _failed(token) and token.get("token") and token.get("complete_url"):
        sep = "&" if "?" in token["complete_url"] else "?"
        return f"{token['complete_url']}{sep}preview_token={token['token']}"
    return None


def get_ai_page_quota(a: dict, api_key: str):
    """What's left of the plan's AI page credits this month: the plan's number, top-ups, and what's been used."""
    if not api_key:
        return NO_KEY
    plan = scanova("GET", "plans/current/", api_key)
    if _failed(plan):
        return plan if isinstance(plan, dict) else {"error": "Couldn't read the current plan."}
    quotas = ((plan.get("plan") or {}).get("quotas") or []) if isinstance(plan.get("plan"), dict) else []
    limit = next((q.get("value") for q in quotas if isinstance(q, dict) and q.get("codename") == QUOTA), None)
    if limit is None or limit == 0:
        return {"limit": 0, "unlimited": False, "used": 0, "topups_remaining": 0, "remaining": 0, "note": "This plan doesn't include AI pages."}
    if limit == -1:
        return {"limit": -1, "unlimited": True, "used": None, "topups_remaining": None, "remaining": None}
    usage = scanova("GET", "ai-assistance/token-usage/", api_key)
    if _failed(usage):
        return usage if isinstance(usage, dict) else {"error": "Couldn't read this month's AI page usage."}
    used = int(usage.get("token_used") or 0)
    topups = scanova("GET", "plans/quota-topups/", api_key)
    rows = topups.get("results") if isinstance(topups, dict) and isinstance(topups.get("results"), list) else topups if isinstance(topups, list) else []
    extra = sum(int(t.get("remaining") or 0) for t in rows if isinstance(t, dict) and t.get("quota_codename") == QUOTA)
    # The same rule Scanova applies before a generation (ExhaustCheck): used < plan + active top-ups.
    return {"limit": int(limit), "unlimited": False, "used": used, "topups_remaining": extra, "remaining": max(int(limit) + extra - used, 0)}


def get_ai_page(a: dict, api_key: str):
    """One QR code's AI page: its HTML (the draft if there is one), and whether it is an AI Studio page at all."""
    if not api_key:
        return NO_KEY
    if err := _missing(a, "qrid"):
        return err
    qrid = str(a["qrid"]).strip()
    if not _SEGMENT.match(qrid):
        return {"error": "qrid isn't a valid id"}
    qr = scanova("GET", f"qr/{qrid}/", api_key)
    if _failed(qr):
        return {"error": f"There's no QR code {qrid!r} in this account."}
    is_ai = _category_slug(qr) == AI_CATEGORY
    html = (_html_of(qr.get("draft_info")) or _html_of(qr.get("info"))) if is_ai else ""
    return {
        "qrid": qrid,
        "name": qr.get("name"),
        "is_ai_page": is_ai,
        "html": html,
        "has_unpublished_changes": bool(qr.get("draft_info")),
        "published": bool(qr.get("published_at")),
        "studio_url": STUDIO_URL.format(qrid=qrid) if is_ai else None,
    }


def _ai_category_id(api_key: str):
    groups = scanova("GET", "qr/category/", api_key)
    cats = [c for g in groups.values() for c in g] if isinstance(groups, dict) and "error" not in groups else groups if isinstance(groups, list) else []
    for c in cats:
        if isinstance(c, dict) and c.get("slug") == AI_CATEGORY:
            return c.get("id")
    return None


def _generator(g) -> dict | None:
    if not isinstance(g, dict):
        return None
    out = {
        "provider": str(g.get("provider") or "external")[:30],
        "model_id": str(g.get("model_id") or "external")[:100],
    }
    for key in ("input_tokens", "output_tokens"):
        if isinstance(g.get(key), int) and g[key] >= 0:
            out[key] = g[key]
    if isinstance(g.get("total_cost"), (int, float)) and g["total_cost"] >= 0:
        out["total_cost"] = round(float(g["total_cost"]), 6)
    return out


def save_ai_page(a: dict, api_key: str):
    """A finished AI page into AI Studio: a new version (Tailwind compiled by Scanova, one credit used), then the QR
    code's draft — a new AI QR code, or the given one's. Nothing is published."""
    if not api_key:
        return NO_KEY
    if err := _missing(a, "html", "prompt"):
        return err
    html, prompt = str(a["html"]), str(a["prompt"]).strip()[:MAX_PROMPT_CHARS]
    if not html.strip() or len(html) > MAX_HTML_CHARS:
        return {"error": f"html must be a whole page, at most {MAX_HTML_CHARS:,} characters."}
    if not prompt:
        return {"error": "prompt is required"}
    qrid = str(a.get("qrid") or "").strip() or None
    if qrid and not _SEGMENT.match(qrid):
        return {"error": "qrid isn't a valid id"}
    name = (str(a.get("name") or "").strip() or None)
    if qrid:
        qr = scanova("GET", f"qr/{qrid}/", api_key)
        if _failed(qr):
            return {"error": f"There's no QR code {qrid!r} in this account.", "status_code": 400}
        if _category_slug(qr) != AI_CATEGORY:
            return {"error": "That QR code isn't an AI Studio page.", "status_code": 400}
        name = name or qr.get("name")
    body = {"prompt": prompt, "full_html_page": html}
    if qrid:
        body["qrid"] = qrid
    if a.get("summary"):
        body["summary"] = str(a["summary"]).strip()[:500]
    if gen := _generator(a.get("generator")):
        body["generator"] = gen
    version = scanova("POST", "ai-assistance/qr-sessions/external/", api_key, body=body)
    if _failed(version):
        return version if isinstance(version, dict) else {"error": "Scanova didn't save the page."}
    compiled = version.get("full_html_page") or html
    info = json.dumps({"full_html_page": compiled})
    session_id = version.get("session_id")
    if qrid:
        saved = scanova("PATCH", f"qr/{qrid}/", api_key, body={"info": info, "is_draft": True, "ai_session_id": session_id})
        created = False
    else:
        category = _ai_category_id(api_key)
        if category is None:
            return {"error": "Couldn't find the AI page category in this account."}
        name = (name or DEFAULT_NAME)[:100]
        saved = scanova("POST", "qr/", api_key, body={"name": name, "category": category, "qr_type": "dy", "info": info, "is_draft": True, "ai_session_id": session_id})
        created = True
    if _failed(saved):
        return saved if isinstance(saved, dict) else {"error": "Scanova saved the version but not the QR code's draft."}
    qrid = saved.get("qrid") or qrid
    out = {
        "qrid": qrid,
        "name": saved.get("name") or name or DEFAULT_NAME,
        "created": created,
        "session_id": session_id,
        "version_number": version.get("version_number"),
        "token_used": version.get("token_used"),
        "studio_url": STUDIO_URL.format(qrid=qrid),
    }
    if preview := _preview_url(qrid, api_key):
        out["preview_url"] = preview
        out["preview_expires"] = "in 1 hour"
    return out


_QRID = {"type": "string", "description": "The AI page's QR code id (qrid)"}

AI_PAGE_TOOLS: list[MoreTool] = [
    MoreTool(
        "get_ai_page_quota", "Check AI page credits",
        "How many AI pages (AI Studio generations, the plan's AI_QR_TOKENS) the account has left this month: the plan's number, top-ups and what's been used. -1 / unlimited means no limit.",
        "AI pages", "ai-assistance/token-usage/", _input(),
        _object({"limit": {"type": ["integer", "null"]}, "unlimited": {"type": "boolean"}, "used": {"type": ["integer", "null"]}, "topups_remaining": {"type": ["integer", "null"]}, "remaining": {"type": ["integer", "null"]}}),
        get_ai_page_quota,
    ),
    MoreTool(
        "get_ai_page", "Get an AI page",
        "An AI Studio page's current HTML (its draft if it has one), name and links — to change it. is_ai_page is false for QR codes that aren't AI Studio pages.",
        "AI pages", "qr/{qrid}/", _input({"qrid": _QRID}, ("qrid",)),
        _object({"qrid": {"type": "string"}, "is_ai_page": {"type": "boolean"}, "html": {"type": "string"}, "studio_url": {"type": ["string", "null"]}}),
        get_ai_page,
    ),
    MoreTool(
        "save_ai_page", "Save an AI page",
        "Save a finished AI landing page (a whole HTML document styled with Tailwind) into AI Studio as a new version — Scanova compiles its Tailwind and one AI page credit is used — and as the QR code's draft: a new AI QR code, or the draft of the one given. Nothing is published; the customer publishes from AI Studio.",
        "AI pages", "ai-assistance/qr-sessions/external/",
        _input({
            "html": {"type": "string", "description": "The whole page, <!DOCTYPE html>…</html>"},
            "prompt": {"type": "string", "maxLength": MAX_PROMPT_CHARS, "description": "What the customer asked for — kept as the version's request in AI Studio"},
            "qrid": _QRID,
            "name": {"type": "string", "maxLength": 100, "description": "A new page's name"},
            "summary": {"type": "string", "maxLength": 500, "description": "One line on what the page is"},
            "generator": {
                "type": "object",
                "description": "What made it, for Scanova's usage records: provider, model_id, input_tokens, output_tokens, total_cost (USD)",
                "properties": {"provider": {"type": "string"}, "model_id": {"type": "string"}, "input_tokens": {"type": "integer"}, "output_tokens": {"type": "integer"}, "total_cost": {"type": "number"}},
            },
        }, ("html", "prompt")),
        _object({"qrid": {"type": "string"}, "name": {"type": "string"}, "studio_url": {"type": "string"}, "preview_url": {"type": "string"}, "version_number": {"type": ["integer", "null"]}}),
        save_ai_page,
    ),
]

AI_PAGE_TOOL_NAMES = frozenset(t.name for t in AI_PAGE_TOOLS)
