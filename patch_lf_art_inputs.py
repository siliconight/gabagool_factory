"""Index the light manifest, and refuse a themed lot that cannot carry its art.

Run from the factory root:

    python patch_lf_art_inputs.py --check
    python patch_lf_art_inputs.py

Step 2 of `level_factory/docs/PER_BUILDING_ART.md`. Pure: a directory listing
and a refusal. No Blender, no Godot, no behaviour change to any lot that builds
today.

WHY `.lights.json` IS NOT ADDED TO `REQUIRED`, which is the obvious move and is
wrong. `pick_lot` selects from whatever `index` calls complete, keyed on the
candidate seed. Adding a fourth required suffix removes archetypes from that
pool, which reshuffles every draw -- so seed 5118 would select a DIFFERENT five
buildings than the ones already built, walked and evaluated. The repo's own
rule, from `_write_site_spec`: *"re-placing a level that has already been
evaluated would be a different level wearing the same grade."* Measured in
`deli_counter/build/`: 138 `.glb`, 136 `.slots.json`, 135 `.lights.json`, so
this is not hypothetical -- the sets genuinely differ.

So `.lights.json` is indexed as an OPTIONAL field, and the requirement lives
where it actually applies: the themed path, which is the only path that bakes
fixtures.

WHY IT RAISES RATHER THAN FILTERS. A missing manifest could drop its archetype
out of the lot, and the lot would be four buildings instead of five with every
stage reporting success. That exact failure is already in `WALKABLE_SITE.md`'s
trap list -- a varied lot placed the mission shell five times while five
composes wrote correct scenes beside it, because an absence was read as
"nothing to do". A shorter lot is not a smaller version of the brief; it is a
different brief nobody asked for.
"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path("level_factory/packages/pipeline/building_library.py")

EDITS = [
    ("art inputs constant", '''\
REQUIRED = (".glb", ".gameplay.json", ".slots.json")
''', '''\
#: What a building needs to be PLACED. Do not extend this set casually:
#: `pick_lot` draws from whatever `index` calls complete, so adding a suffix
#: removes archetypes from the pool and reshuffles every existing draw. A seed
#: that has already been built and evaluated would select a different five
#: buildings and wear the same grade.
REQUIRED = (".glb", ".gameplay.json", ".slots.json")

#: What a building additionally needs to be DRESSED AS ITSELF.
#:
#: Zoo's fixtures pass consumes a `.lights.json` and names its output from that
#: manifest's `building_id`. Planned once per mission, one such bake was
#: attached to all five buildings of a varied lot -- measured 2026-08-06, an
#: identical 30.5 x 3.7 x 17.9 fixture box inside five different shells. Per
#: building art needs a per building manifest, and 135 of the library's 138
#: shells already ship one.
#:
#: Deliberately NOT part of `REQUIRED`. See the module patch note and
#: docs/PER_BUILDING_ART.md.
ART_REQUIRED = (".lights.json",)
'''),
    ("index the light manifest", '''\
    ``complete`` entries are ``{"id", "family", "glb", "gameplay", "slots"}``,
    sorted by id so a listing order cannot change what a seed selects.
    ``incomplete`` entries say what each one is missing, because a silently
    shorter library is how a lot quietly stops being varied.
    """
''', '''\
    ``complete`` entries are ``{"id", "family", "glb", "gameplay", "slots",
    "lights"}``, sorted by id so a listing order cannot change what a seed
    selects. ``incomplete`` entries say what each one is missing, because a
    silently shorter library is how a lot quietly stops being varied.

    ``lights`` is ``""`` when the archetype has no ``.lights.json``. It is
    reported and never used to EXCLUDE, because completeness here decides what
    `pick_lot` draws from and changing that changes which buildings an already
    evaluated seed selects. The themed path applies the requirement itself, via
    `art_incomplete`.
    """
'''),
    ("carry lights on the entry", '''\
        complete.append({
            "id": aid, "family": family(aid),
            "glb": str(parts[".glb"]),
            "gameplay": str(parts[".gameplay.json"]),
            "slots": str(parts[".slots.json"]),
        })
    return complete, incomplete
''', '''\
        lights = root / (aid + ".lights.json")
        complete.append({
            "id": aid, "family": family(aid),
            "glb": str(parts[".glb"]),
            "gameplay": str(parts[".gameplay.json"]),
            "slots": str(parts[".slots.json"]),
            "lights": str(lights) if lights.is_file() else "",
        })
    return complete, incomplete


def art_incomplete(lot: list[dict]) -> list[dict]:
    """Which of the PICKED buildings cannot be dressed as themselves.

    Reports rather than decides, so the caller can say what it wants to do --
    and so this stays the pure directory-and-arithmetic module it claims to be.
    """
    out = []
    for e in lot or []:
        missing = [suf for suf, key in ((".lights.json", "lights"),)
                   if not e.get(key)]
        if missing:
            out.append({"id": e.get("id", "?"), "missing": missing})
    return out


class ArtInputsMissing(RuntimeError):
    """A themed lot was asked for and a building cannot carry its own art."""


def require_art_inputs(lot: list[dict]) -> None:
    """Raise unless every picked building can be dressed as itself.

    RAISES rather than filtering, and the distinction is the whole point. If a
    building without a light manifest simply dropped out, a five building brief
    would produce a four building site with every stage reporting success --
    which is the failure already recorded in docs/WALKABLE_SITE.md, where five
    composes wrote correct scenes and the site placed the mission shell five
    times because an absence was read as nothing to do.

    A lot that cannot be dressed is not a smaller version of the brief. It is a
    different brief, and nobody asked for it.
    """
    gaps = art_incomplete(lot)
    if not gaps:
        return
    detail = "; ".join(f"{g['id']} (no {', '.join(g['missing'])})"
                       for g in gaps)
    raise ArtInputsMissing(
        f"{len(gaps)} of {len(lot)} building(s) in this lot cannot carry "
        f"per-building art: {detail}. A themed lot dresses each building AS "
        f"ITSELF, so every one needs its own manifest -- build the missing "
        f"ones, or run this mission without --art.")
'''),
]


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    if not TARGET.is_file():
        print(f"[patch] {TARGET} not found -- run from the factory root")
        return 1
    raw = TARGET.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    print(f"[patch] {TARGET}: {len(raw)} bytes, "
          f"endings={'CRLF' if crlf else 'LF'}")

    problems = []
    for name, before, after in EDITS:
        if after in text:
            print(f"[patch]   ALREADY APPLIED: {name}")
        elif before not in text:
            print(f"[patch]   ANCHOR NOT FOUND: {name}")
            problems.append(name)
        elif text.count(before) != 1:
            print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(before)}x): {name}")
            problems.append(name)
    if problems:
        print(f"[patch] REFUSING to write: {len(problems)} anchor(s) did not "
              f"match cleanly.")
        return 1

    for name, before, after in EDITS:
        if after in text:
            continue
        text = text.replace(before, after)
        print(f"[patch]   applied: {name}")

    if check_only:
        print("[patch] --check: no write")
        return 0
    payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
    TARGET.write_bytes(payload)
    print(f"[patch] wrote {TARGET}: {len(raw)} -> {len(payload)} bytes "
          f"({len(payload) - len(raw):+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
