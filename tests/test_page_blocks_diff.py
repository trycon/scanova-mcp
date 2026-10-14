"""scripts/page_blocks_diff.py: the drift workflow's summary of a bundle refresh."""

import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "page_blocks_diff", Path(__file__).resolve().parent.parent / "scripts" / "page_blocks_diff.py"
)
page_blocks_diff = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(page_blocks_diff)
summarize, changed_files = page_blocks_diff.summarize, page_blocks_diff.changed_files


def _block(**kw):
    return {"label": "Map", "limit": 20, "removable": True, "default": {"zoom": 14}, **kw}


def test_no_change_is_empty():
    assert summarize({"map": _block()}, {"map": _block()}) == []


def test_added_and_removed_blocks():
    assert summarize({"old": _block()}, {"new": _block()}) == [
        "- `new`: new block",
        "- `old`: no longer offered",
    ]


def test_changed_rules_are_named():
    assert summarize({"map": _block()}, {"map": _block(label="Location", limit=5)}) == ["- `map`: label, limit"]


def test_changed_schema_files():
    assert changed_files({"a.json": {}, "b.json": {"x": 1}}, {"b.json": {"x": 2}, "c.json": {}}) == [
        "- A `c.json`", "- D `a.json`", "- M `b.json`",
    ]


def test_committed_bundle_is_readable():
    bundle = json.loads((Path(__file__).resolve().parent.parent / "src/page_blocks/bundle.json").read_text())
    assert summarize(bundle["blocks"], bundle["blocks"]) == []
    assert changed_files(bundle["files"], bundle["files"]) == []
