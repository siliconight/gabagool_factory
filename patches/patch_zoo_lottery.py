"""Zoo 1.47.0: the lottery dispensers, built to a brief.

Cold run 9135's frames put the real-look till beside three flat red boxes.
`core/counter_lottery.py` builds each dispenser as an acrylic case on a black
foot showing a different invented ticket game, painted into the till's image
(`counter_register.paint_art`) so it rides in the till's draw. With the
dispensers out of it the service counter's shared `plastic` kind holds
nothing, and the counter is seven draws again -- what it was at 1.45.0.

The first prop built to the walker's authorship guide
(`docs/reference/HUMAN_AUTHORSHIP_GUIDE.md`): a brief first, a cause for each
detail, quiet where nothing needs saying.

Recorded as `zoo_lottery/manifest.json` (each file's SHA-256 at 1.46.0 and at
1.47.0) and `zoo_lottery/files/` (the after-state); the patch refuses to
write unless every target is byte-for-byte its recorded before-state or
already its after-state.

    python patch_zoo_lottery.py            # apply
    python patch_zoo_lottery.py --check    # say what it would do
    ZOO_ROOT=<copy> python patch_zoo_lottery.py
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
NEW = HERE / "zoo_lottery"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def main(check=False):
    manifest = json.loads((NEW / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["from_version"] == "1.46.0" and manifest["to_version"] == "1.47.0", manifest
    todo, done, wrong = [], [], []
    for row in manifest["files"]:
        rel, before, after = row["path"], row["before"], row["after"]
        src = NEW / "files" / rel
        assert src.exists(), f"zoo_lottery/files/{rel} is missing"
        new = src.read_bytes()
        assert _sha(new) == after, f"zoo_lottery/files/{rel} is not the file the manifest recorded"
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
            print(f"REFUSED {rel}: neither its 1.46.0 bytes nor its 1.47.0 bytes ({have})")
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
