r"""Give the roadmap a status convention, and stamp what this week settled.

    python patch_roadmap_status_0812.py --check
    python patch_roadmap_status_0812.py
    python patch_roadmap_status_0812.py --revert

Run from the FACTORY ROOT. Then:

    python roadmap_status.py --write     # fill the index it just created
    python roadmap_status.py --check     # exits 1 when the index drifts

`PIPELINE_ROADMAP.md` is 194 KB with 41 numbered items, and asked "what is
open?" on 2026-08-12 the honest answer was that nobody could say. Closures are
prose; there is one literal DONE in the file; nothing checks any of it. Same
failure as `PIPELINE_MAP.md` drifting from the planner, and `roadmap_status.py`
is the same answer -- derive the summary from the artefact.

This patch does two things and neither of them rewrites an item's argument:

  1. Adds the convention and the markers the index lives between.
  2. Adds a `*STATUS:` line to sixteen items, each carrying the evidence.

WHAT IS CLOSED, AND ON WHAT

  27, 33  the export shipped a scene without its geometry. 21 unresolved -> 0,
          132 misrooted -> 0, and a clean-project run at parser_error_count 0.
  29      "the exported package contains one building and no ground" -- it now
          carries five archetypes plus site_base.glb.
  34      the themed export measured ~27 m against a ~150 m greybox. It is the
          whole site now.
  30      "seventy-two anchors on disk, zero lights in the tree" -- the shipped
          presentation scene has 116 OmniLight3D and 11 SpotLight3D under
          LuxFixtureLights, spawned by the loader the item says is missing.
  38      already written in the past tense; made explicit.

  36      NARROWED. Its walk plumbing described hand-assembling a project
          because Lot wrote res://C:/... absolutes and the export shipped no
          player. absolute_path_count is 0 and cmd_walk wraps the export. The
          nine things a human found on that walkthrough are untouched.

  31, 32  ANALYSIS. Reductions of engine documentation about what Godot's GI
          techniques require of whom. Nothing closes them, and leaving them in
          a defect queue makes the queue lie about its size.

Six nav/collision items are stamped OPEN with today's date. That is not
bookkeeping: 3 and 12 were re-confirmed against the code and against
SESSION_0811's numbers, and saying "still true on 2026-08-12" is worth more
than silence, which is indistinguishable from nobody having looked.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

DOC = Path("PIPELINE_ROADMAP.md")
SIDECAR = ".pre_status"


OLD_HEAD = '''## What to do next'''

NEW_HEAD = '''## What to do next

Status convention: one line directly above an item, carrying the evidence.

    *STATUS: CLOSED 2026-08-12 -- 127 lights in the shipped presentation scene*

    **30. Nothing instantiates the light loader ...**

Vocabulary is `OPEN`, `CLOSED`, `RETRACTED`, `NARROWED`, `SUPERSEDED`,
`ANALYSIS`. The last one is not a hedge: items 31 and 32 are reductions of
engine documentation, nothing closes them, and counting them as open defects
makes this file lie about its own size.

The table below is DERIVED from those lines by `roadmap_status.py`, not typed.
`roadmap_status.py --check` exits 1 when it drifts and `--write` regenerates
it, the way `factory_map.py` maintains the stage table in `PIPELINE_MAP.md`.
An item with no status line is reported as resting on a sentence --
`roadmap_status.py --unclassified` lists them, and that list is the remaining
work of adopting this.

<!-- BEGIN GENERATED: roadmap_status.py -- do not edit by hand -->
<!-- END GENERATED -->'''


#: item number -> (exact heading line, status line, needs a blank line above)
#: The heading lines are copied from the file, not retyped; `_apply` refuses
#: unless each occurs exactly once.
STAMPS = {
    3: ("**3. Lot places enemies twice, and nothing checks the two agree.** `lot.py:1337`",
        "*STATUS: OPEN 2026-08-12 -- both call sites re-confirmed while threading `solids` through `place_enemies`*",
        False),
    8: ("**8. Nothing checks the SIZE of the island an anchor snaps to.** The",
        "*STATUS: OPEN 2026-08-12 -- unchanged; this file's own \"highest-leverage item\", ~400 map_get_path queries*",
        False),
    10: ("**10. `nav_gate.py` certifies geometry that never ships.** It loads the glb at",
         "*STATUS: OPEN 2026-08-12 -- unchanged*",
         False),
    12: ("**12. Props bake as walkable navmesh, and nothing can reach them.**",
         "*STATUS: OPEN 2026-08-12 -- candidate cause of the 1,179 player_stuck_events in SESSION_0811*",
         False),
    14: ("**14. Seed 5017 has a collision trap the path query cannot see.** The first real",
         "*STATUS: OPEN 2026-08-12 -- unchanged; re-measure after the first run on a level that has walls*",
         False),
    16: ("**16. The navmesh contains routes the collision geometry blocks.** The library",
         "*STATUS: OPEN 2026-08-12 -- unchanged; this file's own \"biggest open question\"*",
         False),
    27: ("**27. The portable export ships a scene without its geometry, and every gate in",
         "*STATUS: CLOSED 2026-08-12 -- 36 resources, closure ok, portability PASS. SESSION_0812*",
         False),
    29: ("**29. The art path themes one building; the site is never themed, and the site",
         "*STATUS: CLOSED 2026-08-12 -- the export carries five archetypes plus site_base.glb, not one building*",
         False),
    30: ("**30. Nothing instantiates the light loader, so shipping the anchors would not",
         "*STATUS: CLOSED 2026-08-12 -- 116 OmniLight3D + 11 SpotLight3D under LuxFixtureLights in the shipped scene*",
         False),
    31: ("**31. Lighting: what the engine requires of the geometry, and what Lux can",
         "*STATUS: ANALYSIS -- engine constraints, not a defect. Note project.godot writes gl_compatibility*",
         False),
    32: ("**32. Two lighting systems, and none of the interior one is switched on.**",
         "*STATUS: ANALYSIS -- a working model plus an engine fact; the interior lights do now spawn (item 30)*",
         False),
    33: ("**33. The export does not contain the level, and the closure judge said so on",
         "*STATUS: CLOSED 2026-08-12 -- 21 unresolved -> 0, 132 misrooted -> 0, engine parser_error_count 0*",
         False),
    34: ("**34. The greybox is a site; the themed export is a fragment of one.** Measured",
         "*STATUS: CLOSED 2026-08-12 -- themed_site_assemble; the export is the whole site, five buildings*",
         False),
    36: ("**36. Walking it. Zoo's inserts are exact; the layer with no slot is the one",
         "*STATUS: NARROWED 2026-08-12 -- walk plumbing superseded by cmd_walk wrapping the export; the nine findings stand*",
         True),
    38: ("**38. Light anchors hung below the slab, and four Deli Counter tests that were",
         "*STATUS: CLOSED 2026-08-02 -- cap_thick threaded into derive_light_anchors and build_light_manifest*",
         True),
    41: ("**41. The dressing layer is STRUCTURAL ART routed through the decoration",
         "*STATUS: OPEN 2026-08-12 -- unchanged, and the one on this list a viewer notices*",
         True),
}


def _edits():
    yield (OLD_HEAD, NEW_HEAD)
    for _n, (head, status, lead) in sorted(STAMPS.items()):
        yield (head, ("\n" if lead else "") + status + "\n\n" + head)


EDITS = {DOC: tuple(_edits())}

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
              f"bytes ({len(data) - len(raw):+,})  {len(edits)} edit(s), eol "
              f"{'CRLF' if eol == _CRLF else 'LF'}")
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
    if not check:
        print("  next: python roadmap_status.py --write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
