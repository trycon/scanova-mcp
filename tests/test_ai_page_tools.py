"""AI page tools (mcp_http/ai_page_tools.py), with the Scanova API faked at requests.request."""

import json

import pytest

import scanova_api
from mcp_http.annotations import annotations_for
from mcp_http.dispatcher import execute_tool
from mcp_http.normalizer import normalize
from mcp_http.toolsets import toolset_for

KEY = "key123"


class _Resp:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = {"ok": True} if body is None else body
        self.text = json.dumps(self._body)

    def json(self):
        return self._body


@pytest.fixture
def api(monkeypatch):
    calls, routes = [], {}

    def fake(method, url, headers=None, params=None, json=None, timeout=None):
        path = url.split("/", 3)[-1]
        calls.append({"method": method, "path": path, "body": json, "auth": (headers or {}).get("Authorization")})
        answer = routes.get((method, path))
        if callable(answer):
            answer = answer(json)
        return answer if isinstance(answer, _Resp) else _Resp(body=answer)

    monkeypatch.setattr(scanova_api.requests, "request", fake)
    fake.calls, fake.routes = calls, routes
    return fake


def _plan(value):
    return {"plan": {"name": "Pro", "quotas": [{"codename": "QR_CODES", "value": 50}, {"codename": "AI_QR_TOKENS", "value": value}]}}


PAGE = "<!DOCTYPE html><html><head></head><body><h1 class='text-3xl'>Café Luna</h1></body></html>"
COMPILED = PAGE.replace("<head></head>", "<head><style>.text-3xl{font-size:1.875rem}</style></head>")


def _ai_qr(qrid="Qa1", draft=True):
    info = json.dumps({"full_html_page": "<html>old draft</html>" if draft else "<html>live</html>"})
    return {"qrid": qrid, "name": "Café Luna", "category": {"id": 31, "slug": "ai"}, "draft_info": info if draft else None,
            "info": json.dumps({"full_html_page": "<html>live</html>"}), "published_at": "2026-10-01T00:00:00Z"}


# ── quota ──────────────────────────────────────────────────────────────────── #

def test_quota_counts_plan_topups_and_usage(api):
    api.routes[("GET", "plans/current/")] = _plan(10)
    api.routes[("GET", "ai-assistance/token-usage/")] = {"token_used": 9}
    api.routes[("GET", "plans/quota-topups/")] = [{"quota_codename": "AI_QR_TOKENS", "remaining": 5}, {"quota_codename": "QR_CODES", "remaining": 100}]
    out = execute_tool("get_ai_page_quota", {}, KEY)
    assert out == {"limit": 10, "unlimited": False, "used": 9, "topups_remaining": 5, "remaining": 6}
    assert all(c["auth"] == KEY for c in api.calls)  # the customer's own credential, as given


def test_quota_unlimited_and_none(api):
    api.routes[("GET", "plans/current/")] = _plan(-1)
    assert execute_tool("get_ai_page_quota", {}, KEY)["unlimited"] is True
    assert [c["path"] for c in api.calls] == ["plans/current/"]
    api.routes[("GET", "plans/current/")] = {"plan": {"quotas": []}}
    assert execute_tool("get_ai_page_quota", {}, KEY)["remaining"] == 0


def test_quota_used_up_never_goes_negative(api):
    api.routes[("GET", "plans/current/")] = _plan(3)
    api.routes[("GET", "ai-assistance/token-usage/")] = {"token_used": 7}
    api.routes[("GET", "plans/quota-topups/")] = {"count": 0, "results": []}
    assert execute_tool("get_ai_page_quota", {}, KEY)["remaining"] == 0


def test_quota_usage_unreachable_is_an_error(api):
    api.routes[("GET", "plans/current/")] = _plan(10)
    api.routes[("GET", "ai-assistance/token-usage/")] = _Resp(404, {"detail": "Not found."})
    out = normalize(execute_tool("get_ai_page_quota", {}, KEY), "get_ai_page_quota")
    assert out["ok"] is False and out["status_code"] == 404


# ── reading a page ─────────────────────────────────────────────────────────── #

def test_get_ai_page_reads_the_draft_first(api):
    api.routes[("GET", "qr/Qa1/")] = _ai_qr()
    out = execute_tool("get_ai_page", {"qrid": "Qa1"}, KEY)
    assert out["is_ai_page"] is True and out["html"] == "<html>old draft</html>"
    assert out["studio_url"] == "https://app.scanova.io/qr/Qa1/ai"
    api.routes[("GET", "qr/Qa1/")] = _ai_qr(draft=False)
    assert execute_tool("get_ai_page", {"qrid": "Qa1"}, KEY)["html"] == "<html>live</html>"


def test_get_ai_page_of_another_kind(api):
    api.routes[("GET", "qr/Qb2/")] = {"qrid": "Qb2", "category": {"slug": "dynamicText"}, "info": json.dumps({"pages": []})}
    out = execute_tool("get_ai_page", {"qrid": "Qb2"}, KEY)
    assert out["is_ai_page"] is False and out["html"] == "" and out["studio_url"] is None


def test_get_ai_page_rejects_path_tricks(api):
    assert "error" in execute_tool("get_ai_page", {"qrid": "../plans"}, KEY)
    assert api.calls == []


# ── saving ─────────────────────────────────────────────────────────────────── #

GEN = {"provider": "trycon", "model_id": "bedrock/zai.glm-4.7", "input_tokens": 12000, "output_tokens": 9000, "total_cost": 0.0324567891}


def test_save_new_page_creates_a_version_then_the_qr_code(api):
    api.routes[("POST", "ai-assistance/qr-sessions/external/")] = _Resp(201, {"session_id": "s-1", "version_id": "v-1", "version_number": 1, "full_html_page": COMPILED, "qr_code_uuid": None, "token_used": 4})
    api.routes[("GET", "qr/category/")] = {"Popular": [{"id": 4, "slug": "url"}], "New": [{"id": 31, "slug": "ai"}]}
    api.routes[("POST", "qr/")] = _Resp(201, {"qrid": "Qnew1", "name": "Café Luna"})
    api.routes[("POST", "qr/Qnew1/preview-token/")] = {"token": "t0k", "complete_url": "https://scnv.io/AbC"}
    out = execute_tool("save_ai_page", {"html": PAGE, "prompt": "A page for Café Luna", "name": "Café Luna", "summary": "Café opening", "generator": GEN}, KEY)
    version = next(c for c in api.calls if c["path"] == "ai-assistance/qr-sessions/external/")
    assert version["body"] == {
        "prompt": "A page for Café Luna", "full_html_page": PAGE, "summary": "Café opening",
        "generator": {"provider": "trycon", "model_id": "bedrock/zai.glm-4.7", "input_tokens": 12000, "output_tokens": 9000, "total_cost": 0.032457},
    }
    qr = next(c for c in api.calls if c["path"] == "qr/" and c["method"] == "POST")
    # The compiled page (Tailwind inlined by Scanova) is what the QR code gets, linked to its AI Studio session.
    assert qr["body"] == {"name": "Café Luna", "category": 31, "qr_type": "dy", "info": json.dumps({"full_html_page": COMPILED}), "is_draft": True, "ai_session_id": "s-1"}
    assert out == {
        "qrid": "Qnew1", "name": "Café Luna", "created": True, "session_id": "s-1", "version_number": 1, "token_used": 4,
        "studio_url": "https://app.scanova.io/qr/Qnew1/ai", "preview_url": "https://scnv.io/AbC?preview_token=t0k", "preview_expires": "in 1 hour",
    }


def test_save_into_an_existing_ai_page_updates_its_draft(api):
    api.routes[("GET", "qr/Qa1/")] = _ai_qr()
    api.routes[("POST", "ai-assistance/qr-sessions/external/")] = _Resp(201, {"session_id": "s-9", "version_number": 4, "full_html_page": COMPILED, "qr_code_uuid": "Qa1", "token_used": 5})
    api.routes[("PATCH", "qr/Qa1/")] = {"qrid": "Qa1", "name": "Café Luna"}
    out = execute_tool("save_ai_page", {"html": PAGE, "prompt": "Darker colours", "qrid": "Qa1"}, KEY)
    assert next(c for c in api.calls if c["path"] == "ai-assistance/qr-sessions/external/")["body"]["qrid"] == "Qa1"
    patch = next(c for c in api.calls if c["method"] == "PATCH")
    assert patch["body"] == {"info": json.dumps({"full_html_page": COMPILED}), "is_draft": True, "ai_session_id": "s-9"}
    assert out["created"] is False and out["version_number"] == 4 and not any(c["path"] == "qr/" for c in api.calls)


def test_save_refuses_a_page_that_isnt_an_ai_page(api):
    api.routes[("GET", "qr/Qb2/")] = {"qrid": "Qb2", "category": {"slug": "dynamicText"}}
    out = execute_tool("save_ai_page", {"html": PAGE, "prompt": "x", "qrid": "Qb2"}, KEY)
    assert "isn't an AI Studio page" in out["error"]
    assert not any(c["method"] == "POST" for c in api.calls)


def test_save_out_of_credits_passes_the_403_on(api):
    api.routes[("POST", "ai-assistance/qr-sessions/external/")] = _Resp(403, {"detail": "You have exhausted your limit of 10 AI QR token calls.", "limit": 10})
    env = normalize(execute_tool("save_ai_page", {"html": PAGE, "prompt": "x"}, KEY), "save_ai_page")
    assert env["ok"] is False and env["status_code"] == 403
    assert not any(c["path"] == "qr/" for c in api.calls)


def test_save_needs_html_prompt_and_a_key(api):
    assert "error" in execute_tool("save_ai_page", {"prompt": "x"}, KEY)
    assert "error" in execute_tool("save_ai_page", {"html": PAGE}, KEY)
    assert "error" in execute_tool("save_ai_page", {"html": "x" * 1_000_001, "prompt": "x"}, KEY)
    assert "error" in execute_tool("save_ai_page", {"html": PAGE, "prompt": "x"}, None)
    assert api.calls == []


def test_classified_as_page_tools():
    assert annotations_for("get_ai_page_quota")["readOnlyHint"] is True
    assert annotations_for("get_ai_page")["readOnlyHint"] is True
    save = annotations_for("save_ai_page")
    assert save["readOnlyHint"] is False and save["destructiveHint"] is False  # a draft and a version: only adds
    assert {toolset_for(n) for n in ("get_ai_page_quota", "get_ai_page", "save_ai_page")} == {"pages"}
