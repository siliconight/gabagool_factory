r"""Close the ladder document, and correct how the absence was described.

    python patch_ladder_doc_closed.py --check
    python patch_ladder_doc_closed.py
    python patch_ladder_doc_closed.py --revert

Run from the FACTORY ROOT. Applies on top of `patch_ladder_doc_status.py`.

TWO CHANGES.

**It is closed.** The library was rebuilt on 2026-08-12 -- 138 shells through
Blender -- and the roof slots now carry the holes. `build_freshness.py --list`
reports "138 shell(s) newer than deli_counter.py -- up to date".

**And the previous status block described the absence wrongly.** It said the
roof slot had "no `voids` key at all", read from the slot's TOP LEVEL. `voids`
lives inside `fit`, beside `openings` and `collision`, which is where
`roofs._slot` puts it and where `floors._slot` has always put its own. So that
sentence was measured at the wrong nesting depth.

The CONCLUSION was not resting on it. It rested on three mtimes and on
`build_freshness.py` independently reporting all 138 shells stale, and the
rebuild has now produced the voids that were predicted. But a document that
records a measurement has to record the one that was taken, and the corrected
version is stronger evidence than the wrong one was: the emitted rectangles
match `ladder_geom.through_hole` to the centimetre.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

DOC = Path("LADDER_INTO_SOLID_ROOF.md")
SIDECAR = ".pre_ladderclosed"


OLD = '''**The builder half is still outstanding, and it is not Blender -- it is the
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
shell" predicted.'''


NEW = '''**The builder half was the LIBRARY, not Blender -- and it is now rebuilt.**
The artefact the pipeline consumes was three days older than the fix:

```
deli_counter/build/*.slots.json   2026-08-05 21:16   <- what Zoo dresses
patch_dc_roof_voids.py            2026-08-08 19:45   <- the fix
deli_counter.py                   2026-08-10 01:11   <- source, patched
```

`deli_generate` cache-hits and the library is not rebuilt per run, so corrected
code sat three days from the artefact it corrected. `build_freshness.py`
reported **all 138 shells stale**, having been written for exactly this on
2026-08-05 and never once run.

**Rebuilt 2026-08-12** (`python build.py --all`, 138 shells). The roof slots
now carry the holes:

```
bank_tower_a03  fit.voids = [{x0  15.45, y0 7.30, x1  16.55, y1  8.60},
                             {x0  15.25, y0 6.75, x1  16.75, y1  8.25}]
warehouse_a01   fit.voids = [{x0 -16.55, y0 8.90, x1 -15.45, y1 10.20},
                             {x0 -16.75, y0 9.25, x1 -15.25, y1 10.75}]
```

Two rectangles each -- a **1.10 m** ladder aperture and a 1.50 m stair one. The
ladder width is `ladder_geom.through_hole`'s, the same figure this document
measured in `slab_col_2-colonly` at `x=15.45 / x=16.55`, and the same shape the
NEW ORDER simulation above predicted. `build_freshness.py --list` now reports
"138 shell(s) newer than deli_counter.py -- up to date".

*(CORRECTION. The version of this block written earlier on 2026-08-12 said the
roof slot had "no `voids` key at all", read from the slot's TOP level. `voids`
lives inside `fit`, beside `openings` and `collision` -- where `roofs._slot`
puts it and where `floors._slot` always has. That sentence was measured at the
wrong nesting depth. The conclusion did not rest on it: it rested on the three
mtimes above and on `build_freshness.py` independently reporting 138 stale
shells, and the rebuild produced the predicted rectangles. Recorded because a
document that reports a measurement has to report the one that was taken.)*'''


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
            print(f"  apply patch_ladder_doc_status.py first")
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
