"""Summarise how src/page_blocks/ changed after sync_page_blocks.py ran.

Prints Markdown: which block types were added, removed or changed (and which
fields, by id), then which schema files changed. Compares the working tree with
HEAD. Used by .github/workflows/page-blocks-drift.yml for the job summary and
the PR body.

Usage: python scripts/page_blocks_diff.py
"""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCKS = "src/page_blocks/blocks.json"
SCHEMAS = "src/page_blocks/schemas"


def _fields(block: dict) -> dict:
    return {f.get("id") or f.get("path"): f for f in block.get("fields") or []}


def summarize(old: dict, new: dict) -> list[str]:
    """One Markdown bullet per added, removed or changed block type."""
    lines = []
    for t in sorted(new.keys() - old.keys()):
        lines.append(f"- `{t}`: new block")
    for t in sorted(old.keys() - new.keys()):
        lines.append(f"- `{t}`: no longer offered")
    for t in sorted(old.keys() & new.keys()):
        o, n = old[t], new[t]
        if o == n:
            continue
        parts = [k for k in sorted(o.keys() | n.keys()) if k != "fields" and o.get(k) != n.get(k)]
        of, nf = _fields(o), _fields(n)
        parts += [f"field `{f}` added" for f in sorted(nf.keys() - of.keys(), key=str)]
        parts += [f"field `{f}` removed" for f in sorted(of.keys() - nf.keys(), key=str)]
        parts += [f"field `{f}` changed" for f in sorted(of.keys() & nf.keys(), key=str) if of[f] != nf[f]]
        if not parts and o.get("fields") != n.get("fields"):
            parts.append("field order")
        lines.append(f"- `{t}`: " + ", ".join(parts))
    return lines


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def main() -> None:
    old = json.loads(_git("show", f"HEAD:{BLOCKS}"))
    new = json.loads((ROOT / BLOCKS).read_text())
    blocks = summarize(old, new)
    # Porcelain status also lists new (untracked) schema files: "XY path".
    schemas = [s for s in _git("status", "--porcelain", "-uall", "--", SCHEMAS).split("\n") if s]
    out = ["### Blocks", *(blocks or ["- no change"]), "", "### Schemas"]
    out += [f"- {s[:2].strip()} `{s[3:].removeprefix(SCHEMAS + '/')}`" for s in schemas] or ["- no change"]
    print("\n".join(out))


if __name__ == "__main__":
    main()
