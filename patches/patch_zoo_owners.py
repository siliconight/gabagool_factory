"""Zoo 1.49.0: the owner pass -- every typeface belongs to somebody; a
screen's letters are pixels again.

Seven faces minted from the three CC0 families Pixelcoat 0.55.0 vendors
(Aileron, Vegur, MFB Oldstyle); `smooth_type.OWNERS` gives each kind of
owner its face (a shop, a maker, a notice, printed advertising, a display);
each cigarette brand has its own lettering; the ATM's legends are its
maker's and its sticker the shop's; the ATM's and the video poker's tubes
are set in the pixel face (`paint.Img.pixel_text`).

Recorded as `zoo_owners/manifest.json` (each file's SHA-256 at 1.48.0 and at
1.49.0) and `zoo_owners/files/` (the after-state); the patch refuses to
write unless every target is byte-for-byte its recorded before-state or
already its after-state. The minted faces are in the manifest;
`tools/mint_smooth_type.py --fonts <pixelcoat>/assets/fonts --all`
regenerates them.

    python patch_zoo_owners.py            # apply
    python patch_zoo_owners.py --check    # say what it would do
    ZOO_ROOT=<copy> python patch_zoo_owners.py
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
NEW = HERE / "zoo_owners"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def main(check=False):
    manifest = json.loads((NEW / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["from_version"] == "1.48.0" and manifest["to_version"] == "1.49.0", manifest
    todo, done, wrong = [], [], []
    for row in manifest["files"]:
        rel, before, after = row["path"], row["before"], row["after"]
        src = NEW / "files" / rel
        assert src.exists(), f"zoo_owners/files/{rel} is missing"
        new = src.read_bytes()
        assert _sha(new) == after, f"zoo_owners/files/{rel} is not the file the manifest recorded"
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
            print(f"REFUSED {rel}: neither its 1.48.0 bytes nor its 1.49.0 bytes ({have})")
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
