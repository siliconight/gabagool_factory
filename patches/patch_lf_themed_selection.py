"""A THEMED lot draws only from shells that can carry a theme.

Run from the factory root:

    python patch_lf_themed_selection.py --check
    python patch_lf_themed_selection.py

Pure: two manifests per shell, JSON and arithmetic. No workspace, no Lot, no
Godot, and NO CHANGE to what a greybox lot selects -- see THE CONSTRAINT.

WHAT WAS MEASURED, 2026-08-08.

Two buildings from one walked site, read off their own manifests:

    pharmacy_a02   137 slots  coverage {wall 118, doorway 6, breach 2,
                              window 2}   9 Zoo modules drawn   stands solid
    final_stand      9 slots  coverage {}                0 modules drawn
                              holes where its walls should be

An empty `coverage` map is a shell the themed kit does not fill. Over the real
build dir: 136 slot manifests, 13 of them with `coverage: {}`, and the 15
lowest-slot shells are the same set.

The reachability half, from `<id>.navgate.json`: 135 manifests, 107 with
markers the nav bake could not reach, 17 with `markers.checked == 0`, and 11
with everything reachable.

THE TWO RULES ARE ONLY SAFE TOGETHER. Reachability alone selects
`rowhouse_raid` (1 slot), `harbor_score` (3), `07_police_station` (4) and
`stop_n_go` (5) -- the four shells in the library with the least in them to
strand, which is the least themeable set it could possibly pick. Coverage
alone keeps 121 shells whose markers nothing can reach. Intersected, and
intersected with the pool `index` actually offers, SIX shells survive, one per
family:

    bank_branch_a04  cr_garage  freight_terminal_a03
    gas_station_a02  parking_garage  pvp_station_ref

`survival_demo` is the seventh all-reachable, non-hollow shell and is NOT in
that list: it ships no `.slots.json` at all, so `REQUIRED` drops it one step
before fitness is asked. It reads as "not in the empty-coverage list" only
because it is in no coverage list at all -- a missing manifest counted as a
good one. That is the arithmetic that turns 6 into 7.

UNJUDGED IS NOT PASSING. `markers.checked == 0` is a question nobody put to
the shell. A predicate reading `reachable == checked` alone passes all 17 of
them, and this repo has already written down twice what that is: a check that
cannot fail is indistinguishable from one that passed.

WHY THE RULE IS KEYED ON EMPTY AND NOT ON A THRESHOLD. 0 is measured-bad and
128 is measured-good and nothing between them has been measured. A cutoff at
20 or at 40 would be an invention wearing a number, and the next reader would
take it for a finding.

THE CONSTRAINT THAT GOVERNS THIS PATCH.

`pick_lot` draws from whatever `index` calls complete. Changing that pool
re-selects every lot that has already been built and evaluated -- the rule
`_write_site_spec` states in its own words, "re-placing a level that has
already been evaluated would be a different level wearing the same grade".
It is why `.lights.json` was kept out of `REQUIRED` in step 2 and it binds
here identically.

So `REQUIRED` is untouched, `index` still indexes exactly what it indexed, and
the greybox draw is byte-identical. The narrowing lives behind an explicit
`themed=True` and is applied in the two places that build a THEMED spec.
`test_themed_selection.py` pins seeds 5017-5421 of the real library against ids
captured before this patch; seed 5118 is `lot_demo_001`'s first candidate, four
of whose five buildings are unfit for a themed lot, so a leak shows there first.

WHY IT REFUSES INSTEAD OF SHORTENING. docs/PER_BUILDING_ART.md's trap list
already names this failure: an archetype dropping silently out of a themed lot
is how a five-building brief becomes a four-building site with every stage
reporting success. That is the defect recorded in docs/WALKABLE_SITE.md, where
five composes wrote correct scenes and the site placed the mission shell five
times because an absence was read as nothing to do. A lot that cannot be
themed is not a smaller version of the brief.

The refusal is keyed on FAMILIES, because families are what `pick_lot` draws
without replacement. Six fit families is today's ceiling: a seven-building
themed brief refuses, and says which six it has and why the rest are short.

WHAT THIS DOES NOT DO, stated so the next reader does not assume it does.
Nothing here fans the art DAG out per building (step 3b/3c) and nothing here
reads a `.lights.json`. It changes WHICH buildings a themed lot selects, not
how they are dressed. `require_art_inputs` still has no caller.
"""
from __future__ import annotations

import sys
from pathlib import Path

LIBRARY = Path("level_factory/packages/pipeline/building_library.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")

LIBRARY_EDITS = [
    ("json import", '''\
import re
from pathlib import Path
''', '''\
import json
import re
from pathlib import Path
'''),

    ("index docstring names navgate", '''\
    ``complete`` entries are ``{"id", "family", "glb", "gameplay", "slots",
    "lights"}``, sorted by id so a listing order cannot change what a seed
    selects.\
''', '''\
    ``complete`` entries are ``{"id", "family", "glb", "gameplay", "slots",
    "lights", "navgate"}``, sorted by id so a listing order cannot change what
    a seed selects.\
'''),

    ("index the navgate manifest", '''\
        lights = root / (aid + ".lights.json")
        complete.append({
            "id": aid, "family": family(aid),
            "glb": str(parts[".glb"]),
            "gameplay": str(parts[".gameplay.json"]),
            "slots": str(parts[".slots.json"]),
            "lights": str(lights) if lights.is_file() else "",
        })
''', '''\
        lights = root / (aid + ".lights.json")
        navgate = root / (aid + ".navgate.json")
        complete.append({
            "id": aid, "family": family(aid),
            "glb": str(parts[".glb"]),
            "gameplay": str(parts[".gameplay.json"]),
            "slots": str(parts[".slots.json"]),
            "lights": str(lights) if lights.is_file() else "",
            "navgate": str(navgate) if navgate.is_file() else "",
        })
'''),

    ("themed fit inputs constant", '''\
#: Deliberately NOT part of `REQUIRED`. See the module patch note and
#: docs/PER_BUILDING_ART.md.
ART_REQUIRED = (".lights.json",)
''', '''\
#: Deliberately NOT part of `REQUIRED`. See the module patch note and
#: docs/PER_BUILDING_ART.md.
ART_REQUIRED = (".lights.json",)

#: What a building must SAY about itself to be picked for a THEMED lot.
#:
#: `<id>.slots.json` carries `coverage` -- how many slots of each kind the
#: themed kit actually filled. `<id>.navgate.json` carries
#: `markers.checked/reachable` -- whether the nav bake could reach what the
#: mission needs. Both are read; neither is required to be INDEXED.
#:
#: Not part of `REQUIRED` for the reason stated there. Three of the library's
#: shells ship no navgate manifest at all, and dropping them from `complete`
#: would reshuffle every draw that has already been graded. These decide
#: themed selection only, via `themed_report`.
THEMED_FIT_INPUTS = (".slots.json", ".navgate.json")
'''),

    ("fitness section", '''\
def pick_lot(entries: list[dict], seed: int, count: int) -> list[dict]:
''', '''\
def _manifest(path) -> dict | None:
    """The JSON object at ``path``, or ``None``.

    Absent, unreadable and not-an-object all answer ``None``, on purpose: a
    truncated manifest is a shell nobody has successfully judged, which is the
    same answer a missing one gives. Nothing here should raise -- this module
    is a directory listing and arithmetic, and it runs while a plan is built.
    """
    if not path:
        return None
    try:
        with open(str(path), "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def slot_coverage(entry) -> dict:
    """``coverage`` from a shell's slot manifest -- ``{}`` when there is none.

    Measured 2026-08-08 by walking two buildings out of one site.
    `pharmacy_a02` -- 137 slots, coverage {wall 118, doorway 6, breach 2,
    window 2}, 9 Zoo modules drawn -- stands solid. `final_stand` -- 9 slots,
    coverage {}, 0 modules -- has holes where its walls should be. An empty
    coverage map is a shell the themed kit does not fill.

    Keyed on EMPTY downstream, never on a count: 0 is measured-bad, 128 is
    measured-good, and nothing between them has been measured. A threshold
    here would be an invention wearing a number.
    """
    data = _manifest(entry.get("slots") if isinstance(entry, dict) else entry)
    cov = (data or {}).get("coverage")
    return dict(cov) if isinstance(cov, dict) else {}


def marker_reach(entry) -> tuple[int, int] | None:
    """``(checked, reachable)`` from a shell's navgate manifest, or ``None``.

    ``None`` is "the question was never put to this shell" -- no manifest, or
    one with no markers block. That is a different fact from ``(0, 0)``, which
    is a gate that ran and checked nothing, and both differ from ``(4, 2)``.
    Fitness refuses all three; they are kept apart so the report can say which.
    """
    data = _manifest(
        entry.get("navgate") if isinstance(entry, dict) else entry)
    markers = (data or {}).get("markers")
    if not isinstance(markers, dict):
        return None
    try:
        return (int(markers.get("checked", 0) or 0),
                int(markers.get("reachable", 0) or 0))
    except (TypeError, ValueError):
        return None


def themed_fitness(entry) -> dict:
    """``{"id", "family", "fit", "reasons"}`` -- can this shell wear a theme?

    Two conditions, and they are only safe TOGETHER. Reachability alone
    selects `rowhouse_raid` (1 slot), `harbor_score` (3), `07_police_station`
    (4) and `stop_n_go` (5) -- the shells with the least in them to strand,
    which is the least themeable set the library could offer. Coverage alone
    keeps 121 shells whose markers nothing can reach. Together they leave six.

    UNJUDGED IS NOT PASSING. `markers.checked == 0` is a question nobody
    asked, and 17 of the indexed library are in that state. A predicate
    reading `reachable == checked` alone passes every one of them, which is
    the shape this repo has already paid for twice: a check that cannot fail
    is indistinguishable from one that passed.

    Each reason reads ``"<head>: <detail>"``. The head is a stable bucket the
    refusal tallies on; the detail carries this shell's own numbers.
    """
    reasons: list[str] = []
    if not slot_coverage(entry):
        reasons.append("empty slot coverage: the themed kit fills nothing "
                       "in this shell")
    reach = marker_reach(entry)
    if reach is None:
        reasons.append("no navgate manifest: reachability unjudged")
    else:
        checked, reachable = reach
        if checked <= 0:
            reasons.append("markers unjudged: checked 0, so nothing was "
                           "asked and nothing passed")
        elif reachable != checked:
            reasons.append(f"markers unreachable: only {reachable} of "
                           f"{checked} reachable")
    return {"id": (entry or {}).get("id", "?"),
            "family": (entry or {}).get("family", ""),
            "fit": not reasons, "reasons": reasons}


def themed_report(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """``(fit, unfit)`` index rows, each unfit one carrying its ``reasons``.

    Reports rather than decides, the same way `art_incomplete` does, so the
    caller owns the sentence and this stays the pure module it claims to be.
    Rows are copies of the index entries, so `pick_lot` and `footprints_for`
    read them unchanged.
    """
    fit, unfit = [], []
    for e in entries or []:
        verdict = themed_fitness(e)
        row = dict(e)
        row["reasons"] = verdict["reasons"]
        (fit if verdict["fit"] else unfit).append(row)
    return fit, unfit


class ThemedShellsUnavailable(RuntimeError):
    """A themed lot was asked for and the library cannot fill it."""


def require_themed_shells(entries: list[dict], count: int) -> list[dict]:
    """The fit subset, or raise naming exactly what is short.

    RAISES rather than shortening, and the distinction is the whole point --
    the same one `require_art_inputs` makes one function up. If unfit shells
    simply dropped out, a five building brief would produce a smaller site
    with every stage reporting success, which is the failure already recorded
    in docs/WALKABLE_SITE.md and named again in docs/PER_BUILDING_ART.md's
    trap list. A lot that cannot be themed is not a smaller version of the
    brief. It is a different brief, and nobody asked for it.

    Keyed on FAMILIES because families are what `pick_lot` draws without
    replacement. Two fit variants of one family cannot fill two places in a
    varied lot without repeating an archetype, which is item 37 again.
    """
    want = max(1, int(count or 1))
    fit, unfit = themed_report(entries)
    families = sorted({e.get("family", "") for e in fit})
    if len(families) >= want:
        return fit
    tally: dict[str, int] = {}
    for e in unfit:
        for reason in e.get("reasons") or ():
            tally[str(reason).split(":", 1)[0]] = (
                tally.get(str(reason).split(":", 1)[0], 0) + 1)
    detail = "; ".join(f"{n} with {head}" for head, n in sorted(tally.items()))
    raise ThemedShellsUnavailable(
        f"a themed lot of {want} needs {want} fit families and the library "
        f"offers {len(families)}: {', '.join(families) or '(none)'}. "
        f"{len(unfit)} of {len(fit) + len(unfit)} indexed shell(s) are unfit "
        f"-- {detail or 'no reason recorded'}. A themed lot dresses each "
        f"building AS ITSELF, so a shell whose slots the kit does not fill, "
        f"or whose markers the nav bake cannot reach, is not a smaller "
        f"version of this brief -- build or judge the missing shells, or run "
        f"this mission without --art.")


def pick_lot(entries: list[dict], seed: int, count: int) -> list[dict]:
'''),

    ("lot_for signature", '''\
def lot_for(library, building_count, candidate_id) -> tuple[list[dict], list[dict]]:
''', '''\
def lot_for(library, building_count, candidate_id, *,
            themed: bool = False) -> tuple[list[dict], list[dict]]:
'''),

    ("lot_for docstring: the themed pool", '''\
    Returns `incomplete` rather than printing it. The two existing callers
    describe the same exclusion differently -- one is about what cannot be
    THEMED, the other about what is missing from the ROW -- and a module with
    no side effects should not pick between their sentences.
    """
''', '''\
    Returns `incomplete` rather than printing it. The two existing callers
    describe the same exclusion differently -- one is about what cannot be
    THEMED, the other about what is missing from the ROW -- and a module with
    no side effects should not pick between their sentences.

    `themed` NARROWS THE POOL, and is off by default for the reason `REQUIRED`
    gives: `pick_lot` draws from whatever it is handed, so a narrower pool
    re-selects every lot that has already been built and graded. The greybox
    path must not pass it. The themed path must, in every place that builds a
    themed spec, or the compose stage and the site stage select different
    buildings and the site finds no composed scene for the ones it placed.
    """
'''),

    ("lot_for body", '''\
    count = max(1, int(building_count or 1))
    if not library or count < 2:
        return [], []
    complete, incomplete = index(library)
    seed = int(str(candidate_id).rsplit("_", 1)[-1])
    return pick_lot(complete, seed, count), incomplete
''', '''\
    count = max(1, int(building_count or 1))
    if not library or count < 2:
        return [], []
    complete, incomplete = index(library)
    if themed:
        # Raises rather than returning a shorter pool. `pick_lot` would
        # happily fall back to unused variants and then to repeats, and a
        # themed lot that quietly repeats an archetype is item 37 again.
        complete = require_themed_shells(complete, count)
    seed = int(str(candidate_id).rsplit("_", 1)[-1])
    return pick_lot(complete, seed, count), incomplete
'''),
]

COMMANDS_EDITS = [
    ("compose lot is themed", '''\
    from packages.pipeline import building_library
    lot, incomplete = building_library.lot_for(
        getattr(model, "lot_library", None),
        getattr(model, "building_count", 1),
        candidate_id)
''', '''\
    from packages.pipeline import building_library
    # THEMED. Both call sites of this function build a themed spec -- the
    # presentation compose's `lot_archetypes` and `themed_site_assemble`'s
    # scene map -- so the pool is the shells that can carry a theme, and a
    # library too small for the brief refuses here rather than composing a
    # short row. The greybox site spec does NOT come through here.
    lot, incomplete = building_library.lot_for(
        getattr(model, "lot_library", None),
        getattr(model, "building_count", 1),
        candidate_id,
        themed=True)
'''),

    ("site spec narrows only when themed", '''\
        from packages.pipeline import building_library
        complete, incomplete = building_library.index(library)
        if incomplete:
            print(f"[site] {len(incomplete)} archetype(s) excluded from the lot "
                  f"for a missing manifest: "
                  + ", ".join(e["id"] for e in incomplete[:5]))
        lot = building_library.pick_lot(complete, seed, count)
''', '''\
        from packages.pipeline import building_library
        complete, incomplete = building_library.index(library)
        if incomplete:
            print(f"[site] {len(incomplete)} archetype(s) excluded from the lot "
                  f"for a missing manifest: "
                  + ", ".join(e["id"] for e in incomplete[:5]))
        if themed_map:
            # The themed pool is narrower, and it must be the SAME narrowing
            # `_lot_for_compose` applied: compose published one scene per
            # archetype and `themed_map` is keyed on those ids. A wider pool
            # here selects buildings that have no composed scene, `_source`
            # finds no match, and the row stands as greybox with every stage
            # reporting success -- which is the defect this file keeps
            # finding, one layer down.
            #
            # NOT applied to the greybox branch above it. That branch places
            # levels that have already been built and graded, and re-selecting
            # them would be different levels wearing the same grades.
            before = len(complete)
            complete = building_library.require_themed_shells(complete, count)
            print(f"[site] themed lot: {len(complete)} of {before} shell(s) "
                  f"can carry a theme")
        lot = building_library.pick_lot(complete, seed, count)
'''),
]

TARGETS = [(LIBRARY, LIBRARY_EDITS), (COMMANDS, COMMANDS_EDITS)]


def _apply(target, edits, check_only):
    if not target.is_file():
        print(f"[patch] {target} not found -- run from the factory root")
        return 1, 0
    raw = target.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    print(f"[patch] {target}: {len(raw)} bytes, "
          f"endings={'CRLF' if crlf else 'LF'}")

    problems = []
    for name, before, after in edits:
        if after in text:
            print(f"[patch]   ALREADY APPLIED: {name}")
        elif before not in text:
            print(f"[patch]   ANCHOR NOT FOUND: {name}")
            problems.append(name)
        elif text.count(before) != 1:
            print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(before)}x): {name}")
            problems.append(name)
    if problems:
        print(f"[patch] REFUSING to write {target}: {len(problems)} anchor(s) "
              f"did not match cleanly.")
        return 1, 0

    for name, before, after in edits:
        if after in text:
            continue
        text = text.replace(before, after)
        print(f"[patch]   applied: {name}")

    payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
    if payload == raw:
        print(f"[patch]   no change ({len(raw)} bytes)")
        return 0, 0
    if check_only:
        print(f"[patch]   --check: would write {len(raw)} -> {len(payload)} "
              f"bytes ({len(payload) - len(raw):+d})")
        return 0, 0
    target.write_bytes(payload)
    print(f"[patch]   wrote {len(raw)} -> {len(payload)} bytes "
          f"({len(payload) - len(raw):+d})")
    return 0, len(payload) - len(raw)


def main(argv):
    check_only = "--check" in argv
    # Nothing is written until EVERY anchor on EVERY file has matched. A patch
    # that half-applies leaves commands/__init__.py calling a function
    # building_library.py does not have, and the next run's --check cannot tell
    # that from a fresh tree.
    for target, edits in TARGETS:
        rc, _ = _apply(target, edits, check_only=True)
        if rc:
            print("[patch] REFUSING to write anything.")
            return 1
    if check_only:
        print("[patch] --check: all anchors matched, no write")
        return 0
    total = 0
    for target, edits in TARGETS:
        rc, delta = _apply(target, edits, check_only=False)
        if rc:
            return 1
        total += delta
    print(f"[patch] total {total:+d} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
