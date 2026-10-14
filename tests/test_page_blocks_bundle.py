"""page_blocks: qcg-backend's page block schema bundle, live from the API with the bundled copy as fallback."""

import copy
import json

import pytest

import page_blocks
from mcp_http import page_tools as P

BUNDLED = json.loads(page_blocks.FALLBACK.read_text())


class _Resp:
    def __init__(self, status=200, body=None, etag=None):
        self.status_code, self._body = status, body
        self.headers = {"ETag": etag} if etag else {}

    def json(self):
        if self._body is None:
            raise ValueError("no body")
        return self._body


@pytest.fixture
def live(monkeypatch):
    """The API, faked: `answers` is what each GET returns, in turn; `calls` what was asked."""
    calls, answers = [], []

    def get(url, headers=None, timeout=None):
        calls.append({"url": url, "headers": headers or {}})
        answer = answers.pop(0) if answers else _Resp(500)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setenv("PAGE_BLOCKS_BUNDLE_URL", "https://api.example/qr/page-blocks/schema/")
    monkeypatch.setattr(page_blocks.requests, "get", get)
    page_blocks.reset()
    yield calls, answers
    page_blocks.reset()


def _changed(**rules):
    b = copy.deepcopy(BUNDLED)
    b["hash"] = "f" * 64
    b["blocks"]["map"].update(rules)
    return b


def test_the_bundled_copy_is_a_bundle():
    assert page_blocks.is_bundle(BUNDLED)
    assert {"page_title", "button", "form_short_answer", "submit_button"} <= set(BUNDLED["blocks"])


def test_default_url_follows_the_api(monkeypatch):
    monkeypatch.delenv("PAGE_BLOCKS_BUNDLE_URL", raising=False)
    assert page_blocks.bundle_url() == page_blocks.SCANOVA_BASE_URL.rstrip("/") + "/qr/page-blocks/schema/"
    monkeypatch.setenv("PAGE_BLOCKS_BUNDLE_URL", "off")
    assert page_blocks.bundle_url() is None


def test_tests_never_fetch():
    page_blocks.reset()
    assert page_blocks.bundle()["hash"] == BUNDLED["hash"] and page_blocks.source() == "bundled"


def test_live_bundle_drives_the_page_tools(live):
    calls, answers = live
    answers.append(_Resp(body=_changed(limit=3, label="Location"), etag='"f"'))
    assert P.blocks()["map"]["limit"] == 3 and P.blocks()["map"]["label"] == "Location"
    assert page_blocks.source() == "live"
    assert calls[0]["url"] == "https://api.example/qr/page-blocks/schema/"


def test_cached_until_the_ttl_then_revalidated(live, monkeypatch):
    calls, answers = live
    answers += [_Resp(body=_changed(limit=3), etag='"f"'), _Resp(304)]
    page_blocks.bundle()
    page_blocks.bundle()
    assert len(calls) == 1  # within the TTL
    monkeypatch.setenv("PAGE_BLOCKS_TTL_S", "0")
    assert page_blocks.bundle()["blocks"]["map"]["limit"] == 3  # 304: kept
    assert calls[1]["headers"]["If-None-Match"] == '"f"'


def test_unreachable_api_falls_back_to_the_bundled_copy(live):
    calls, answers = live
    answers.append(page_blocks.requests.ConnectionError("down"))
    assert page_blocks.bundle()["hash"] == BUNDLED["hash"] and page_blocks.source() == "bundled"


def test_a_failed_refresh_keeps_the_last_live_bundle(live, monkeypatch):
    calls, answers = live
    answers += [_Resp(body=_changed(limit=3), etag='"f"'), _Resp(503)]
    page_blocks.bundle()
    monkeypatch.setenv("PAGE_BLOCKS_TTL_S", "0")
    assert page_blocks.bundle()["blocks"]["map"]["limit"] == 3 and page_blocks.source() == "live"


@pytest.mark.parametrize("body", [{"format": 2, "blocks": {}, "files": {}, "hash": "x"}, {"oops": True}, None])
def test_anything_but_a_bundle_is_ignored(live, body):
    calls, answers = live
    answers.append(_Resp(body=body))
    assert page_blocks.bundle()["hash"] == BUNDLED["hash"]


def test_rules_and_schemas_come_from_the_bundle():
    page_blocks.reset()
    b = BUNDLED["blocks"]
    for block_type, info in P.blocks().items():
        assert info["label"] == b[block_type]["label"] and info["limit"] == b[block_type].get("limit")
        assert info["defaults"] == b[block_type]["default"]
    # Blocks of special page types or hidden from the picker aren't offered.
    assert not {"document_viewer", "image_gallery", "auto_redirect", "cover_page", "main_page"} & set(P.blocks())
    # Form blocks aren't landing blocks.
    assert not any(t.startswith("form_") for t in P.blocks())
    assert P.theme_problems({"_v": 2}) == []
    assert P.theme_problems({"_v": 3})
