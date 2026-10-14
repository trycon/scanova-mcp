"""Refresh src/page_blocks/bundle.json from qcg-backend's page block schema bundle.

The page tools read the bundle live from the API of the environment the
server talks to (src/page_blocks/__init__.py); bundle.json is the copy they
fall back on until a fetch succeeds. This keeps that copy current. It is
written only when the bundle's content (its `hash`) changed, so a refresh
that finds nothing new leaves the file untouched.

Usage:
    python scripts/sync_page_blocks.py                     from the production API
    python scripts/sync_page_blocks.py --from <url|file>   from that URL or file
    python scripts/sync_page_blocks.py <qcg-backend> [<qcg-frontend-next>]
        built from a qcg-backend checkout (`python -m qr_manager.page_block_bundle`)
        when it has the bundle module and its schemas, else from the production
        API. The frontend checkout isn't needed any more; it's accepted (and
        ignored) so existing callers such as the drift workflow keep working.

If no source answers, the copy is left as it is (exit 0, with a warning).
Standard library only: the drift workflow runs it with `uv run --no-project`.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src" / "page_blocks" / "bundle.json"
DEFAULT_URL = os.getenv("PAGE_BLOCKS_BUNDLE_URL") or "https://api.scanova.io/qr/page-blocks/schema/"
NEEDED = ("qr_manager/page_block_bundle.py", "qr_manager/json_schema", "forms/json_schema", "theme_manager/json_schema")


def is_bundle(value) -> bool:
    return isinstance(value, dict) and value.get("format") == 1 and isinstance(value.get("blocks"), dict) \
        and isinstance(value.get("files"), dict) and isinstance(value.get("hash"), str)


def from_backend(checkout: Path):
    src = checkout / "src"
    if not all((src / p).exists() for p in NEEDED):
        return None
    run = subprocess.run([sys.executable, "-m", "qr_manager.page_block_bundle"], cwd=src, capture_output=True, text=True)
    if run.returncode:
        print(f"::warning::building the bundle in {checkout} failed: {run.stderr.strip()[-300:]}")
        return None
    return json.loads(run.stdout)


def load(source: str):
    if source.startswith(("http://", "https://")):
        request = urllib.request.Request(source, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, ValueError) as e:
            print(f"::warning::{source}: {e}")
            return None
    return json.loads(Path(source).read_text())


def write(bundle: dict) -> bool:
    """Write the bundle; False when the copy already has this content."""
    if OUT.exists() and json.loads(OUT.read_text()).get("hash") == bundle["hash"]:
        return False
    OUT.write_text(json.dumps(bundle, indent=1, ensure_ascii=False) + "\n")
    return True


def main(argv: list[str]) -> int:
    if argv[:1] == ["--from"] and len(argv) > 1:
        bundle = load(argv[1])
    else:
        bundle = from_backend(Path(argv[0])) if argv else None
        bundle = bundle or load(DEFAULT_URL)
    if bundle is None:
        print("::warning::no page block bundle to sync from; src/page_blocks/bundle.json left as it is")
        return 0
    if not is_bundle(bundle):
        print("::error::that isn't a format-1 page block schema bundle")
        return 1
    changed = write(bundle)
    print(f"{len(bundle['blocks'])} blocks, hash {bundle['hash'][:12]}: {'updated' if changed else 'no change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
