"""Verifies the shared theme/bridge injection (ui_theme.py + ui_resources.py's
read_resource_contents) replaces, rather than duplicates, the tokens every
widget used to carry independently — the actual bug the 2026-08 UI redesign
was meant to fix (drift between per-file copies)."""

import mcp_http.ui_resources as ui_resources
from mcp_http.ui_theme import SHARED_BRIDGE_SCRIPT, SHARED_STYLE


def test_shared_style_and_bridge_are_nonempty():
    assert "--accent: #c0392b" in SHARED_STYLE
    assert "window.__scanovaBridge = function" in SHARED_BRIDGE_SCRIPT


def test_every_resource_gets_shared_theme_exactly_once():
    for resource in ui_resources.list_resources():
        html = ui_resources.read_resource_contents(resource.uri)
        assert html is not None, f"{resource.uri} file missing"
        assert html.count("--accent: #c0392b") == 1, resource.uri
        assert html.count("window.__scanovaBridge = function") == 1, resource.uri


def test_every_widget_calls_the_shared_bridge_factory():
    for resource in ui_resources.list_resources():
        html = ui_resources.read_resource_contents(resource.uri)
        assert "const Bridge = window.__scanovaBridge();" in html, resource.uri
        # No widget should still define its own local Bridge IIFE.
        assert "const Bridge = (function" not in html, resource.uri


def test_no_widget_redeclares_root_tokens_locally():
    # Check the RAW file (pre-injection) — SHARED_STYLE itself legitimately
    # declares :root twice (light + dark-mode override), so post-injection
    # HTML always has 2 regardless of the widget; what matters is that the
    # widget file itself doesn't carry its own copy.
    for resource in ui_resources.list_resources():
        raw = resource.path.read_text(encoding="utf-8")
        assert ":root" not in raw, resource.uri
