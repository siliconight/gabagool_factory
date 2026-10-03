"""Zoo 1.57.0: the roller grill's heat lamp -- a red-orange element under
the hood on its own lit face, and a `LuxEmit_heat_lamp` attachment below it
for Lux 0.63.0's loader to light. The walker, 2026-10-03: "a dim but warm
warming light to bring a bit more light to the dogs".

Recorded as `zoo_heat_lamp/manifest.json` (each file's SHA-256 at 1.56.0 and
at 1.57.0) and `zoo_heat_lamp/files/` (the after-state); the patch refuses to
write unless every target is byte-for-byte its recorded before-state or
already its after-state.

    python patch_zoo_heat_lamp.py            # apply
    python patch_zoo_heat_lamp.py --check    # say what it would do
    ZOO_ROOT=<copy> python patch_zoo_heat_lamp.py
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
NEW = HERE / "zoo_heat_lamp"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def main(check=False):
    manifest = json.loads((NEW / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["from_version"] == "1.56.0" and manifest["to_version"] == "1.57.0", manifest
    todo, done, wrong = [], [], []
    for row in manifest["files"]:
        rel, before, after = row["path"], row["before"], row["after"]
        src = NEW / "files" / rel
        assert src.exists(), f"zoo_heat_lamp/files/{rel} is missing"
        new = src.read_bytes()
        assert _sha(new) == after, f"zoo_heat_lamp/files/{rel} is not the file the manifest recorded"
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
            print(f"REFUSED {rel}: neither its 1.56.0 bytes nor its 1.57.0 bytes ({have})")
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
