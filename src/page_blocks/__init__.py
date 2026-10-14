"""Scanova's page block rules and schemas, from qcg-backend's page block schema bundle.

The bundle (qcg-backend docs/page-block-schemas.md) is the one source of every
page block's JSON Schema and builder rules — label, how many a page holds,
which QR categories and page types it belongs to, whether it can be removed,
its default data — plus the page-type, form and theme schemas. Each Scanova
environment serves the bundle it validates against at
``GET <API>/qr/page-blocks/schema/``; this module reads it from the API this
server talks to (``API_BASE_URL``), so the rules follow the environment.

- Fetched on first use and re-checked every ``PAGE_BLOCKS_TTL_S`` seconds
  (default 600) with ``If-None-Match``, so an unchanged bundle costs a 304.
- If the API can't be reached (or doesn't serve the bundle yet), the last
  bundle fetched is kept; before any fetch succeeds, ``bundle.json`` here —
  a copy refreshed by ``scripts/sync_page_blocks.py`` — is used.
- ``PAGE_BLOCKS_BUNDLE_URL`` overrides the URL; ``off`` never fetches (tests).
"""

import json
import logging
import os
import threading
import time
from pathlib import Path

import requests

from config import SCANOVA_BASE_URL

log = logging.getLogger(__name__)

FALLBACK = Path(__file__).resolve().parent / "bundle.json"
TIMEOUT_S = 5
FORMAT = 1


def bundle_url() -> str | None:
    url = os.getenv("PAGE_BLOCKS_BUNDLE_URL", "").strip()
    if url.lower() == "off":
        return None
    return url or f"{SCANOVA_BASE_URL.rstrip('/')}/qr/page-blocks/schema/"


def ttl_s() -> float:
    return float(os.getenv("PAGE_BLOCKS_TTL_S", "600"))


def is_bundle(value) -> bool:
    return (
        isinstance(value, dict)
        and value.get("format") == FORMAT
        and isinstance(value.get("blocks"), dict)
        and isinstance(value.get("files"), dict)
        and isinstance(value.get("hash"), str)
    )


_lock = threading.Lock()
_state: dict = {"bundle": None, "etag": None, "live": False, "checked": None}


def _fallback() -> dict:
    return json.loads(FALLBACK.read_text())


def _fetch(url: str, etag: str | None):
    """The bundle, "not-modified", or None when the API didn't give a usable one."""
    try:
        resp = requests.get(
            url,
            headers={"Accept": "application/json", **({"If-None-Match": etag} if etag else {})},
            timeout=TIMEOUT_S,
        )
    except requests.RequestException as e:
        log.warning("page blocks bundle: %s unreachable (%s)", url, e)
        return None
    if resp.status_code == 304:
        return "not-modified"
    if resp.status_code != 200:
        log.warning("page blocks bundle: %s answered %s", url, resp.status_code)
        return None
    try:
        body = resp.json()
    except ValueError:
        body = None
    if not is_bundle(body):
        log.warning("page blocks bundle: %s didn't return a format-%s bundle", url, FORMAT)
        return None
    return body, resp.headers.get("ETag")


def bundle() -> dict:
    """The current bundle: live from the API when it can be had, else the last one, else the bundled copy."""
    now = time.monotonic()
    with _lock:
        if _state["bundle"] is not None and _state["checked"] is not None and now - _state["checked"] < ttl_s():
            return _state["bundle"]
        _state["checked"] = now
        url = bundle_url()
        got = _fetch(url, _state["etag"] if _state["live"] else None) if url else None
        if isinstance(got, tuple):
            _state.update(bundle=got[0], etag=got[1], live=True)
        elif _state["bundle"] is None:
            _state.update(bundle=_fallback(), etag=None, live=False)
        return _state["bundle"]


def source() -> str:
    """Where the current bundle came from: "live" (the API) or "bundled" (bundle.json)."""
    return "live" if _state["live"] else "bundled"


def reset() -> None:
    """Forget the cached bundle (tests)."""
    with _lock:
        _state.update(bundle=None, etag=None, live=False, checked=None)
