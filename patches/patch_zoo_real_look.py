"""Zoo 1.46.0: the real look, trialled on the video poker, the ATM and both
registers.

The walker, 2026-10-02, on the screens-that-run frames: "this looks like it
is made with a 90s GPU, what can we do to make these things look better/more
real without destroying performance?" -- then "replace the retro look, do the
first three as a trial", and after the video-poker cabinet: "yes, do the ATM
and register the same way". The first three:

  1. art at three times the density, in a smooth face, sampled with
     filtering (`core/smooth_type.py`, `core/smooth_faces/`,
     `tools/mint_smooth_type.py`);
  2. shading painted in (`core/paint.py`);
  3. the shape of a made thing (`core/machine_parts.py`): chamfered corners,
     a toe kick set in, a tube that bulges behind a sloped surround, keys
     standing off a deck.

WHAT IT REWRITES: `video_poker_forms`, `atm_forms`, `register_forms` and
`counter_register` from their constants down, their recipes, three genomes,
and the tests that pinned the pixel look. Shared code gains defaults that
leave every other species as it was: `card_art.atlas(gutter=, bleed=)`,
`materials.make_*_material(smooth=)`, `_card_atlas.build_art(smooth=)`,
`shutters.over(proud=)`.

HOW THIS PATCH RECORDS IT. The release rewrites whole modules, so an anchored
before/after pair per edit would be the module twice. Instead
`zoo_real_look/manifest.json` lists every file with the SHA-256 of what it
was at Zoo 1.45.0 (null for a new file) and of what it becomes, and
`zoo_real_look/files/` holds the after-state. The patch refuses to write
anything unless EVERY target is byte-for-byte its recorded before-state (or
already its after-state), which is the anchor assertion made of the whole
file rather than of a fragment.

    python patch_zoo_real_look.py            # apply
    python patch_zoo_real_look.py --check    # say what it would do
    ZOO_ROOT=<copy> python patch_zoo_real_look.py

The minted faces are in the manifest too; `tools/mint_smooth_type.py --fonts
<pixelcoat>/assets/fonts --all` regenerates them from Pixelcoat 0.54.0's
vendored CC0 fonts.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
NEW = HERE / "zoo_real_look"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def main(check=False):
    manifest = json.loads((NEW / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["from_version"] == "1.45.0" and manifest["to_version"] == "1.46.0", manifest
    todo, done, wrong = [], [], []
    for row in manifest["files"]:
        rel, before, after = row["path"], row["before"], row["after"]
        src = NEW / "files" / rel
        assert src.exists(), f"zoo_real_look/files/{rel} is missing"
        new = src.read_bytes()
        assert _sha(new) == after, f"zoo_real_look/files/{rel} is not the file the manifest recorded"
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
            print(f"REFUSED {rel}: neither its 1.45.0 bytes nor its 1.46.0 bytes ({have})")
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
