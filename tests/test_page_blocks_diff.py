"""scripts/page_blocks_diff.py: the drift workflow's summary of changed blocks."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "page_blocks_diff", Path(__file__).resolve().parent.parent / "scripts" / "page_blocks_diff.py"
)
page_blocks_diff = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(page_blocks_diff)
summarize = page_blocks_diff.summarize


def _block(**kw):
    return {"label": "Map", "limit": None, "fields": [{"id": "zoom", "kind": "number"}], **kw}


def test_no_change_is_empty():
    assert summarize({"map": _block()}, {"map": _block()}) == []


def test_added_and_removed_blocks():
    assert summarize({"old": _block()}, {"new": _block()}) == [
        "- `new`: new block",
        "- `old`: no longer offered",
    ]


def test_changed_keys_and_fields():
    old = _block()
    new = _block(label="Location", fields=[{"id": "zoom", "kind": "slider"}, {"id": "pin", "kind": "text"}])
    assert summarize({"map": old}, {"map": new}) == [
        "- `map`: label, field `pin` added, field `zoom` changed"
    ]


def test_field_order_only():
    fields = [{"id": "a"}, {"id": "b"}]
    assert summarize({"x": {"fields": fields}}, {"x": {"fields": fields[::-1]}}) == ["- `x`: field order"]


def test_committed_blocks_json_is_readable():
    import json

    blocks = json.loads((Path(__file__).resolve().parent.parent / "src/page_blocks/blocks.json").read_text())
    assert summarize(blocks, blocks) == []
