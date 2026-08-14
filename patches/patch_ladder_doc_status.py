r"""Correct the ladder document: the fix landed, the library never got it.

    python patch_ladder_doc_status.py --check
    python patch_ladder_doc_status.py
    python patch_ladder_doc_status.py --revert

Run from the FACTORY ROOT.

`LADDER_INTO_SOLID_ROOF.md` says `patch_dc_roof_voids.py` is unapplied. It is
applied -- all three `deli_counter.py` hunks report ALREADY APPLIED, and
`roofs.py` and `test_roofs.py` report `already`. The patch's own `--check` says
DRIFTED only because it guards on a whole-file SHA and `deli_counter.py` has
grown 7,535 bytes from unrelated later work.

That sentence cost a wrong call on 2026-08-12: the ladder failed again, the
document was read as evidence about the code, and "it was never fixed" was said
out loud. The code was fine. The LIBRARY was three days older than the fix.

    deli_counter/build/*.slots.json   2026-08-05 21:16   <- what Zoo dresses
    patch_dc_roof_voids.py            2026-08-08 19:45   <- the fix
    deli_counter.py                   2026-08-10 01:11   <- source, patched

All five placed buildings carry one roof slot with **no `voids` key at all** --
absent, not empty, which is the pre-patch shape. `deli_generate` cache-hits and
the archetype library is not rebuilt per run, so the corrected code has never
reached the artifact the pipeline consumes.

The document also predicted its own confirmation and did not get to record it:
step 5 says the Zoo `.glb` refused to stage twice, so the roof's identity was
inferred from a 762-node listing, and that "`godot --headless` with the overlay
... settles it in one command". The 2026-08-12 walk ran that command. The
overlay reads `bldg roof_footprint zoo`, `look Roof 2.98 m y 3.90` -- against a
predicted `blocker_rel_y` of 3.9.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

DOC = Path("LADDER_INTO_SOLID_ROOF.md")
SIDECAR = ".pre_ladderstatus"


OLD = '''Built and **held**, same as item 7. `patch_dc_roof_voids.py` is unapplied.
The pure half is proved here; the builder half needs your Blender rebuild.'''

NEW = '''*STATUS: NARROWED 2026-08-12 -- code fixed and applied; the ARCHETYPE LIBRARY
still carries pre-fix roof slots and is what Zoo dresses*

**The code half landed. `patch_dc_roof_voids.py` is APPLIED** -- `roofs.py`,
`test_roofs.py`, and all three `deli_counter.py` hunks. Its own `--check`
reports `DRIFTED` on `deli_counter.py`, which is a false alarm: that patch
guards on a whole-file SHA and the file has since grown 7,535 bytes from
unrelated work. Per-anchor occurrence counts would have tolerated it. The line
that used to sit here said the patch was unapplied, and on 2026-08-12 that
sentence was read as evidence about the code and produced a wrong call.

**The builder half is still outstanding, and it is not Blender -- it is the
library.** Measured 2026-08-12 on the five placed buildings:

```
deli_counter/build/*.slots.json   2026-08-05 21:16   <- what Zoo dresses
patch_dc_roof_voids.py            2026-08-08 19:45   <- the fix
deli_counter.py                   2026-08-10 01:11   <- source, patched

arena_a02       133 slots, 1 roof slot, voids ABSENT
auto_shop_a01   142 slots, 1 roof slot, voids ABSENT
bank_tower_a03  110 slots, 1 roof slot, voids ABSENT
strip_club_a03  191 slots, 1 roof slot, voids ABSENT
warehouse_a01   112 slots, 1 roof slot, voids ABSENT
```

No `voids` key at all -- absent rather than empty, which is the pre-patch
shape. `deli_generate` cache-hits and the library is not rebuilt per run, so
the corrected code has never reached the artifact the pipeline consumes.
**Regenerate the archetype library with the current Deli Counter** and this
closes; until then it fails on every candidate, exactly as "this is not one bad
shell" predicted.

**And the prediction held on new ground.** The 2026-08-09 diagnosis was
`bank_branch_a04`. The 2026-08-12 walk ran a different candidate (`seed_5219`)
with a different set -- `arena_a02`, `auto_shop_a01`, `bank_tower_a03`,
`strip_club_a03`, `warehouse_a01` -- and failed identically, at four heights:

```
walk bot [FAIL] Ladder_ladder_0: climb, top_exit
  no opening at all at rel_y 5.20 / 3.30 / 4.70 / 3.90
  -- the slab is solid over the ladder
```

**Step 5's last inch is no longer inference.** That section records the Zoo
`.glb` refusing to stage twice and says `godot --headless` with the overlay
settles it in one command. The 2026-08-12 walk is that command: the overlay
reads `bldg roof_footprint zoo`, `look Roof 2.98 m y 3.90`, against a predicted
`blocker_rel_y` of **3.9**. Inference confirmed by direct observation.

*(Those four `[FAIL]` lines are also the first output the self-check has
produced since 2026-08-10. `patch_lf_walk_the_export.py` left the bots
resolving `res://site.tscn`, which stopped being copied into the preview when
it began wrapping the export, so both died on load while the run kept printing
a sentence about the level not passing its own check. Fixed by
`patch_lf_walk_bot_scene.py`. The instrument found this on its first working
run.)*'''


EDITS = {DOC: ((OLD, NEW),)}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0][:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
