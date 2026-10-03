"""Zoo 1.56.0: a street tree's crown carries the wind's handle -- a sway
weight by height and a phase per leaf cluster in a second UV set -- for
Level Factory 0.130.0's import to move it. Nothing in Zoo moves.

Recorded as `zoo_wind/manifest.json` (each file's SHA-256 at 1.55.0 and at
1.56.0) and `zoo_wind/files/` (the after-state); the patch refuses to write
unless every target is byte-for-byte its recorded before-state or already
its after-state.

    python patch_zoo_wind.py            # apply
    python patch_zoo_wind.py --check    # say what it would do
    ZOO_ROOT=<copy> python patch_zoo_wind.py
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
NEW = HERE / "zoo_wind"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def main(check=False):
    manifest = json.loads((NEW / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["from_version"] == "1.55.0" and manifest["to_version"] == "1.56.0", manifest
    todo, done, wrong = [], [], []
    for row in manifest["files"]:
        rel, before, after = row["path"], row["before"], row["after"]
        src = NEW / "files" / rel
        assert src.exists(), f"zoo_wind/files/{rel} is missing"
        new = src.read_bytes()
        assert _sha(new) == after, f"zoo_wind/files/{rel} is not the file the manifest recorded"
        target = ZOO / rel
        have = _sha(target.read_bytes()) if target.exists() else None
        if have == after:
            done.append(rel)
        elif have == before:
            todo.append((target, new, rel))
        else:
            wrong.append((rel, have))
    if wrong:
        for rel, have in wrong:
            print(f"REFUSED {rel}: neither its 1.55.0 bytes nor its 1.56.0 bytes ({have})")
        raise SystemExit(1)
    print(f"{len(done)} already applied, {len(todo)} to write")
    if check:
        return
    for target, new, rel in todo:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(new)
        print("wrote", rel)


if __name__ == "__main__":
    main(check="--check" in sys.argv[1:])
