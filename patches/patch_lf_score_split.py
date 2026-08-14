r"""Laser Tag's score is read as two scores, because it measures two things.

    python patch_lf_score_split.py --explain
    python patch_lf_score_split.py --check
    python patch_lf_score_split.py
    python patch_lf_score_split.py --verify <lasertag.report.json>
    python patch_lf_score_split.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

## What was measured

Across 11 August, `lot_demo_001` seed 5118 was evaluated four times while the
level and the encounter changed substantially:

    palette + lighting + occluder fixes         45 / FAIL
    the 35 m conservatism                       45 / FAIL
    crew of four, all on one spawn tile         10 / BROKEN
    crew of four on a cleared ring              45 / FAIL

The number moved exactly once, and that once was **the harness failing to run**
-- four capsules interpenetrating, zero shots fired, every run timing out. It
did not move when the site's materials changed, when enemy occlusion moved from
declared footprints to measured collision, or when the crew went from killing
0.72 enemies per run to killing 2, 3 and 4 of 6.

**The total tracked whether the evaluation happened, not whether the map got
better.**

## Why, from the scorer's own arithmetic

`LT_ScoreCalculator` adds five categories, and they do not measure one thing:

    cover           20    shots blocked by collision, agents in the space
    npc_pathing     20    stuck events where agents actually walk
    sightlines      20    LT_MapSampler exposure against real collision
    -------------------
    traversal       25    did the crew COMPLETE THE ROUTE
    combat_pacing   15    when did a scenario-configured enemy open fire

The first sixty points are geometry, measured with agents moving through it.
The last forty are the encounter and the AI. `_score_traversal` reads
`route_completion_rate`, and the bot only advances its route in the ``else`` of
"can I see an enemy" (`site_spawns.OPENING_RANGE` documents this) -- so with six
guards alive on a 260 m plate, traversal is zero **whatever the map looks
like**. `_score_pacing` reads the enemy's first shot, which `player_count`,
`enemy_count` and `enemy_sight_range` dominate.

Reporting all five as one number means a good map with an unbalanced encounter
is indistinguishable from a bad map. That is precisely what 45 has been hiding.

## The change

`packages/validation/lasertag_report.py` gains `category_scores`, `map_score`
and `encounter_score`, and `metrics()` reports them alongside the total. The
total is NOT removed -- it is Laser Tag's own number and changing what it means
would be a second opinion about somebody else's report.

    lasertag_score            45      unchanged, still the readiness signal
    lasertag_map_score        40/60   cover + npc_pathing + sightlines
    lasertag_encounter_score   5/40   traversal + combat_pacing

`summarize()` prints the split on the run line, so the two stop arriving as one
number nobody can act on.

## Deliberately NOT done

**Nothing starts blocking.** TDD 5.5 forbids a readiness score from blocking a
build and this module's own header is emphatic about it; a map score is still a
readiness signal. What changes is that it is a signal about the map.

**Candidate ranking is untouched.** `metrics()` gains keys; nothing that
consumes them is rewired here. Ranking on `lasertag_map_score` instead of
`lasertag_score` is a real improvement and a real decision -- three candidates
that already carry grades were ranked under the old key, and re-ranking them
silently would be the defect this tree keeps finding. The keys are here to make
that decision possible, not to make it quietly.

**The category names are read, not assumed.** A report whose `categories` block
is missing or renamed returns `None` for both halves rather than a plausible
number computed from four fifths of a table. `--verify` prints what it found.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPORT = Path("level_factory") / "packages" / "validation" / "lasertag_report.py"
SIDECAR = ".pre_scoresplit"


SPLIT_OLD = '''def report_runs(data: Mapping[str, object]):'''

SPLIT_NEW = '''#: The categories that measure the GEOMETRY, with agents moving through it.
#: `cover` is shots stopped by collision, `npc_pathing` is stuck events where
#: agents actually walk, `sightlines` is `LT_MapSampler` exposure sampled
#: against real collision. Sixty points, all of them about the level.
MAP_CATEGORIES = ("cover", "npc_pathing", "sightlines")

#: The categories that measure the ENCOUNTER and the bot, not the level.
#:
#: `traversal` reads `route_completion_rate`, and `LT_BotPlayerController` only
#: advances its route in the ``else`` of "can I see an enemy" -- so with six
#: guards alive on a 260 m plate it is zero whatever the map looks like.
#: `combat_pacing` reads the enemy's first shot, which `player_count`,
#: `enemy_count` and `enemy_sight_range` dominate.
#:
#: MEASURED, not asserted. `lot_demo_001` seed 5118 was evaluated four times on
#: 11 August while materials, lighting, enemy occlusion and the encounter all
#: changed. The total read 45, 45, 10, 45 -- and the one move was the harness
#: failing to run, not the map changing. Forty of the hundred points were
#: reporting on a `.tres` and an `@export`.
ENCOUNTER_CATEGORIES = ("traversal", "combat_pacing")


def category_scores(data: Mapping[str, object]) -> dict:
    """The report's per-category scores, or ``{}`` if it did not write them."""
    block = data.get("categories")
    if not isinstance(block, Mapping):
        return {}
    return {str(k): v for k, v in block.items()
            if isinstance(v, (int, float))}


def _partial(data: Mapping[str, object], names) -> object:
    """Sum ``names`` out of the report's categories, or ``None``.

    ``None`` when any of them is missing, rather than a total computed from
    whatever happened to be present. A number that silently describes four
    fifths of a table is worse than no number: it looks actionable and is not,
    which is the whole complaint this split exists to answer.
    """
    scores = category_scores(data)
    if not scores or any(name not in scores for name in names):
        return None
    return sum(scores[name] for name in names)


def map_score(data: Mapping[str, object]):
    """Of 60. What Laser Tag measured about the LEVEL."""
    return _partial(data, MAP_CATEGORIES)


def encounter_score(data: Mapping[str, object]):
    """Of 40. What Laser Tag measured about the scenario and the bot."""
    return _partial(data, ENCOUNTER_CATEGORIES)


def report_runs(data: Mapping[str, object]):'''


METRICS_OLD = '''        "lasertag_passes": len(passing_findings(data)),'''

METRICS_NEW = '''        "lasertag_passes": len(passing_findings(data)),
        # THE SAME REPORT, READ AS THE TWO THINGS IT MEASURES. The total stays
        # exactly as it was -- it is Laser Tag's number and redefining it would
        # be a second opinion about somebody else's report. These are additions.
        #
        # `lasertag_map_score` is the one to look at when a change to the LEVEL
        # is supposed to have done something. Four evaluations of seed 5118 on
        # 11 August returned 45, 45, 10, 45 while the palette, the lighting, the
        # occlusion model and the encounter all changed; the only move was the
        # harness failing to run. Sixty of those points are geometry and forty
        # are a `.tres`, and averaging them hid every change that mattered.
        "lasertag_map_score": map_score(data),
        "lasertag_encounter_score": encounter_score(data),
        "lasertag_categories": category_scores(data) or None,'''


SUMMARY_OLD = '''    tail = f", {degraded} without navigation" if degraded else ""
    if len(evaluated) == total:
        return f"laser_tag: {len(evaluated)}/{total} evaluated{tail}"
    return (f"laser_tag: {len(evaluated)}/{total} evaluated{tail}, "
            f"{total - len(evaluated)} never ran")'''

SUMMARY_NEW = '''    tail = f", {degraded} without navigation" if degraded else ""
    # The split on the run line, because a single number nobody can act on is
    # the thing this is for. Omitted rather than guessed when the reports do not
    # carry categories.
    halves = [(map_score(r), encounter_score(r)) for r in evaluated]
    scored = [(m, e) for m, e in halves if m is not None and e is not None]
    if scored:
        best_map = max(m for m, _e in scored)
        best_enc = max(e for _m, e in scored)
        tail += f", best map {best_map}/60, best encounter {best_enc}/40"
    if len(evaluated) == total:
        return f"laser_tag: {len(evaluated)}/{total} evaluated{tail}"
    return (f"laser_tag: {len(evaluated)}/{total} evaluated{tail}, "
            f"{total - len(evaluated)} never ran")'''


EDITS = {
    REPORT: ((SPLIT_OLD, SPLIT_NEW),
             (METRICS_OLD, METRICS_NEW),
             (SUMMARY_OLD, SUMMARY_NEW)),
}

_CRLF = "\r\n"


def _find(body: str, anchor: str):
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

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
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)

    data = out.encode("utf-8")
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


def _load():
    sys.path.insert(0, str(Path.cwd() / "level_factory"))
    from packages.validation import lasertag_report
    return lasertag_report


def _explain() -> int:
    lr = _load()
    if not hasattr(lr, "map_score"):
        print("  unpatched: one number for five categories.")
        print("  cover 20 + npc_pathing 20 + sightlines 20 are the LEVEL;")
        print("  traversal 25 + combat_pacing 15 are the scenario and the bot.")
        print("  Seed 5118, four evaluations on 11 Aug: 45, 45, 10, 45 --")
        print("  and the one move was the harness failing to run.")
        return 0
    print(f"  map (of 60)        {', '.join(lr.MAP_CATEGORIES)}")
    print(f"  encounter (of 40)  {', '.join(lr.ENCOUNTER_CATEGORIES)}")
    print()
    print("  a report with no `categories` block returns None for both,")
    print("  rather than a number computed from part of a table.")
    print(f"  no categories -> map {lr.map_score({})}, "
          f"encounter {lr.encounter_score({})}")
    return 0


def _verify(report: Path) -> int:
    lr = _load()
    if not hasattr(lr, "map_score"):
        print("[verify] unpatched -- apply first")
        return 1
    data = json.loads(report.read_text(encoding="utf-8"))
    cats = lr.category_scores(data)
    if not cats:
        print(f"[verify] {report.name} carries no `categories` block")
        return 1
    print(f"  {report.name}")
    for name in sorted(cats):
        half = ("map" if name in lr.MAP_CATEGORIES
                else "encounter" if name in lr.ENCOUNTER_CATEGORIES
                else "UNCLASSIFIED")
        print(f"    {name:<15} {cats[name]:>3}   {half}")
    unknown = [n for n in cats
               if n not in lr.MAP_CATEGORIES + lr.ENCOUNTER_CATEGORIES]
    print()
    print(f"  total       {lr.report_score(data)}")
    print(f"  map         {lr.map_score(data)} / 60")
    print(f"  encounter   {lr.encounter_score(data)} / 40")
    if unknown:
        print(f"  UNCLASSIFIED: {', '.join(unknown)} -- Laser Tag added a "
              f"category and neither half counts it")
        return 1
    return 0


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()
    if "--verify" in argv:
        i = argv.index("--verify")
        if i + 1 >= len(argv):
            raise SystemExit("--verify needs a path to a lasertag.report.json")
        return _verify(Path(argv[i + 1]))

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
        print()
        print("  python patch_lf_score_split.py --verify .\\lt_after.json")
        print("  Nothing blocks on this and no ranking changed. The next run's")
        print("  laser_tag line prints both halves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
