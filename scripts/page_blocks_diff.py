"""Summarise how src/page_blocks/bundle.json changed after sync_page_blocks.py ran.

Prints Markdown: which block types were added, removed or changed (and which
of their rules), then which schema files changed. Compares the working tree
with HEAD. Used by .github/workflows/page-blocks-drift.yml for the job summary
and the PR body.

Usage: python scripts/page_blocks_diff.py
"""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = "src/page_blocks/bundle.json"


def summarize(old: dict, new: dict) -> list[str]:
    """One Markdown bullet per added, removed or changed block type."""
    lines = []
    for t in sorted(new.keys() - old.keys()):
        lines.append(f"- `{t}`: new block")
    for t in sorted(old.keys() - new.keys()):
        lines.append(f"- `{t}`: no longer offered")
    for t in sorted(old.keys() & new.keys()):
        o, n = old[t], new[t]
        if o != n:
            lines.append(f"- `{t}`: " + ", ".join(k for k in sorted(o.keys() | n.keys()) if o.get(k) != n.get(k)))
    return lines


def changed_files(old: dict, new: dict) -> list[str]:
    out = [f"- A `{k}`" for k in sorted(new.keys() - old.keys())]
    out += [f"- D `{k}`" for k in sorted(old.keys() - new.keys())]
    out += [f"- M `{k}`" for k in sorted(old.keys() & new.keys()) if old[k] != new[k]]
    return out


def _head() -> dict:
    run = subprocess.run(["git", "show", f"HEAD:{BUNDLE}"], cwd=ROOT, capture_output=True, text=True)
    return json.loads(run.stdout) if run.returncode == 0 else {}


def main() -> None:
    old, new = _head(), json.loads((ROOT / BUNDLE).read_text())
    blocks = summarize(old.get("blocks") or {}, new.get("blocks") or {})
    files = changed_files(old.get("files") or {}, new.get("files") or {})
    source = new.get("source") or {}
    out = [f"Bundle `{str(new.get('hash'))[:12]}` (from {source.get('environment') or '?'}, qcg-backend `{str(source.get('commit') or '?')[:7]}`)", ""]
    out += ["### Blocks", *(blocks or ["- no change"]), "", "### Schemas", *(files or ["- no change"])]
    print("\n".join(out))


if __name__ == "__main__":
    main()
