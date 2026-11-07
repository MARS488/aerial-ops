#!/usr/bin/env python3
"""Report whether an original Stronghold executable was supplied.

This never treats the new minimal prototype, markdown notes, or the
unverified board fixture as the Nov 6 sketch. It does not execute files.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INCOMING = ROOT / "incoming"
MARKER = "NEW-MINIMAL-PROTOTYPE-NOT-ORIGINAL"
CODE_SUFFIXES = {".html", ".js", ".mjs", ".ts", ".tsx", ".py", ".json"}
SKIP_NAMES = {
    "verify_stronghold.py",
    "server.py",
    "castle_board_fixture.json",
    "app.js",
    "index.html",
}


def candidates(folder: Path) -> list[Path]:
    found: list[Path] = []
    if not folder.exists():
        return found
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in CODE_SUFFIXES:
            continue
        if path.name in SKIP_NAMES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if MARKER in text:
            continue
        found.append(path)
    return found


def main() -> int:
    extra = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    folders = [INCOMING]
    if extra is not None:
        folders.append(extra)
    found: list[Path] = []
    for folder in folders:
        found.extend(candidates(folder))
    print("original_executable=NOT_LOCATED")
    print("nov6_claim=UNVERIFIED_DOCUMENT_ONLY")
    print("new_prototype_marker=%s" % MARKER)
    print("scanned=%s" % ",".join(str(p) for p in folders))
    if not found:
        print("status=ORIGINAL_SOURCE_NOT_LOCATED")
        print("incoming_code_files=0")
        return 0
    print("status=CANDIDATE_PRESENT_UNVERIFIED")
    print("incoming_code_files=%s" % len(found))
    for path in found:
        print("candidate=%s" % path)
    print("note=A dropped file is not treated as the Nov 6 executable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
