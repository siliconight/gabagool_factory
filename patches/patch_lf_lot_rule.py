"""Move "which buildings is this lot" into the pure module, so the planner can ask.

Run from the factory root:

    python patch_lf_lot_rule.py --check
    python patch_lf_lot_rule.py

Step 3a of `level_factory/docs/PER_BUILDING_ART.md`. Pure and inert: the rule
is unchanged, it just lives somewhere both callers can reach.

WHY. To plan one dressing job per building, `plan_mission` has to know which
buildings. That rule currently lives in `_lot_for_compose`, in
`apps/cli/commands/__init__.py` -- an APP importing from a package is right, a
package importing from an app is not, so the planner cannot call it where it
is.

WHY NOT JUST RE-DERIVE IT IN THE PLANNER. Because the spec builder's own
comment already refuses that, and it is right:

    Both stages call `_lot_for_compose`, which is one function with one rule,
    not two derivations that happen to agree.

A third caller deriving the same lot from `(library, seed, count)` would agree
until someone changes a signature, and then a mission would dress buildings it
did not place. One function, three callers.

WHAT MOVES AND WHAT DOES NOT. The selection moves verbatim. The PRINTING stays
with the callers, because the two of them say different things about the same
fact (`[compose]` reports archetypes that cannot be themed, `[site]` reports
archetypes excluded from the row) and a pure module should not own a voice.
`lot_for` returns both the lot and what was excluded, so each caller keeps its
own wording.
"""
from __future__ import annotations

import sys
from pathlib import Path

LIB = Path("level_factory/packages/pipeline/building_library.py")
CLI = Path("level_factory/apps/cli/commands/__init__.py")

EDITS: list[tuple[Path, str, str, str]] = [
    (LIB, "lib: the selection rule", '''\
def footprints_for(lot: list[dict], measure) -> list:
''', '''\
def lot_for(library, building_count, candidate_id) -> tuple[list[dict], list[dict]]:
    """``(lot, incomplete)`` -- which buildings this candidate places.

    THE one rule, so that the planner (which must fan art jobs out per
    building), the compose spec and the site spec are not three derivations
    that happen to agree. They agreed by luck until someone changed a
    signature; this is the same answer by construction.

    A varied lot is opt-in on `lot_library` and only means anything when the
    brief asks for more than one building -- otherwise this is the single-shell
    path and the answer is no lot at all.

    Takes primitives rather than a `MissionBrief` so this module stays free of
    `packages.core.models`: it is a directory listing and arithmetic, and it
    should keep being importable by anything.

    Returns `incomplete` rather than printing it. The two existing callers
    describe the same exclusion differently -- one is about what cannot be
    THEMED, the other about what is missing from the ROW -- and a module with
    no side effects should not pick between their sentences.
    """
    count = max(1, int(building_count or 1))
    if not library or count < 2:
        return [], []
    complete, incomplete = index(library)
    seed = int(str(candidate_id).rsplit("_", 1)[-1])
    return pick_lot(complete, seed, count), incomplete


def footprints_for(lot: list[dict], measure) -> list:
'''),
    (CLI, "cli: call the one rule", '''\
    library = getattr(model, "lot_library", None)
    count = max(1, int(getattr(model, "building_count", 1) or 1))
    if not library or count < 2:
        return []
    from packages.pipeline import building_library
    complete, incomplete = building_library.index(library)
    if incomplete:
        # Same voice as the site builder: a silently shorter library is how a
        # lot quietly stops being varied.
        print(f"[compose] {len(incomplete)} archetype(s) not themeable "
              f"(incomplete manifest): "
              + ", ".join(e["id"] for e in incomplete[:5]))
    seed = int(str(candidate_id).rsplit("_", 1)[-1])
    return building_library.pick_lot(complete, seed, count)
''', '''\
    from packages.pipeline import building_library
    lot, incomplete = building_library.lot_for(
        getattr(model, "lot_library", None),
        getattr(model, "building_count", 1),
        candidate_id)
    if incomplete:
        # Same voice as the site builder: a silently shorter library is how a
        # lot quietly stops being varied.
        print(f"[compose] {len(incomplete)} archetype(s) not themeable "
              f"(incomplete manifest): "
              + ", ".join(e["id"] for e in incomplete[:5]))
    return lot
'''),
]


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    for path in (LIB, CLI):
        if not path.is_file():
            print(f"[patch] {path} not found -- run from the factory root")
            return 1
    files: dict[Path, tuple[bytes, bool, str]] = {}
    for path in (LIB, CLI):
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        files[path] = (raw, crlf, raw.decode("utf-8").replace("\r\n", "\n"))
        print(f"[patch] {path}: {len(raw)} bytes, "
              f"endings={'CRLF' if crlf else 'LF'}")

    problems = []
    for path, name, before, after in EDITS:
        text = files[path][2]
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

    for path, name, before, after in EDITS:
        raw, crlf, text = files[path]
        if after in text:
            continue
        files[path] = (raw, crlf, text.replace(before, after))
        print(f"[patch]   applied: {name}")

    if check_only:
        print("[patch] --check: no write")
        return 0
    for path, (raw, crlf, text) in files.items():
        payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
        path.write_bytes(payload)
        print(f"[patch] wrote {path}: {len(raw)} -> {len(payload)} bytes "
              f"({len(payload) - len(raw):+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
