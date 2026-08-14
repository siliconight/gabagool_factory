"""What Deli Counter already knows about every building it has ever built.

    python library_census.py <deli_counter/build>          # summary
    python library_census.py <build> --detail STAIRWELL     # who, and what

Pure: reads the JSON manifests already on disk. No Blender, no Godot, no
rebuild. Runs over the whole library in about a second.

## Why this exists

`final_stand` walks with a stair rising into an uncut ceiling and an objective
you cannot reach. Its own `final_stand.validation.json` says:

    passed = True
    gates.stairwell.passed  = True   warnings: 10
    gates.enterability.passed = True warnings: 3
    gates.navigability.passed = True warnings: 1
    gates.tactical.passed = True     warnings: 2

and `final_stand.navgate.json` says:

    ok = True
    markers.checked = 1
    markers.reachable = 0
    markers.unreachable = ['objective_final_boss (snap 0.7m)']

Every gate ran. Every gate measured the defect. Every gate passed. A build whose
objective is unreachable reports `ok = True`.

So the question "what rules do we need so the other GLBs don't have these
defects" has a different answer than expected: the rules are written and they
already fire. Nothing is listening. Before deciding which warnings should
BLOCK, it is worth knowing how many buildings each one would stop -- a gate
promoted without that number is a gate that either changes nothing or empties
the library, and nobody finds out which until the next run.

That number is what this prints.

## What it deliberately does not do

It does not decide anything. It does not edit a manifest, promote a warning, or
filter a library. It reports what is already recorded, so the promotion is a
decision taken against a count rather than against four screenshots.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

def _factory_root() -> Path:
    """The directory holding `factory.manifest.json`, found by walking up.

    Was `Path(__file__).resolve().parent`, which required this file to sit AT
    the factory root and kept eleven scripts pinned there. Walking up means it
    works from `tools/`, `patches/` or anywhere else, and still returns the
    root when it IS the root -- the first candidate tested is its own
    directory.

    The manifest is the marker because it is the one file that defines this
    place and exists in no tool repo. `.git` would match every tool repo.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / "factory.manifest.json").is_file():
            return base
    return here.parent


ROOT = _factory_root()
sys.path.insert(0, str(ROOT / "level_factory"))


def source_ids(root: Path, argv: list[str]):
    """``(ids, excluded)`` for a build dir — or ``None`` when it cannot judge.

    THIS SCRIPT GLOBS THE DIRECTORY. It does not go through
    `building_library.index`, and the 2026-08-09 handoff said it did — worth
    correcting rather than quietly fixing, because the plan that rested on it
    ("one place, cannot drift, and every count corrects itself") was true of
    one of the three readers and not of the other two. Fixing `index` alone
    would have left every number this script prints counted against a library
    containing the pipeline's own composed output, and left it DISAGREEING with
    `library_themed_fit.py`, which does go through `index` — two instruments
    reporting different denominators for the same directory.

    So: the rule is IMPORTED, never restated. `library_themed_fit.py` gives the
    argument in full and it is the same one — a report that computes the answer
    a second way tells you what the report thinks, not what the pipeline does.

    REFUSES rather than printing an unfiltered count. An unfiltered number here
    is not a smaller truth, it is the defect: `lf_lot_demo_001_5017` counted as
    a building is how "6 of 134" and "103 navigable, 15 holed, 17 unjudged"
    came to be consistent with each other and wrong together. `--unfiltered`
    prints it anyway, loudly, for comparing against a figure taken before this.
    """
    ids = sorted(p.name[: -len(".glb")] for p in root.glob("*.glb"))
    if "--unfiltered" in argv:
        print("!! --unfiltered: counts below include the pipeline's own "
              "composed output and Deli Counter's facades")
        return ids, []
    try:
        from packages.pipeline import building_library as bl
        rule = bl.source_exclusion
    except Exception as exc:                    # noqa: BLE001 -- reported
        print(f"could not import building_library.source_exclusion: {exc}")
        print(f"  expected it under {ROOT / 'level_factory'}")
        print("  this file must SIT in the factory root next to level_factory/")
        print("  re-run with --unfiltered to count the raw directory anyway")
        return None
    keep, excluded = [], []
    for aid in ids:
        why = rule(root, aid)
        (excluded if why else keep).append((aid, why) if why else aid)
    return keep, excluded


def _load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _code(w: str) -> str:
    """The stable head of a warning, so counts group rather than fragment."""
    m = re.match(r"^([A-Z][A-Z_ ]{3,}?)[: ]", w.strip())
    if m:
        parts = m.group(1).split()
        return parts[-1] if len(parts) > 1 else parts[0]
    return w.strip().split(":")[0][:44]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.splitlines()[2].strip())
        return 2
    root = Path(argv[0])
    detail = None
    if "--detail" in argv:
        detail = argv[argv.index("--detail") + 1].upper()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2

    got = source_ids(root, argv)
    if got is None:
        return 2
    ids, excluded = got
    per_gate = collections.Counter()
    per_code = collections.Counter()
    code_owners: dict[str, list[str]] = collections.defaultdict(list)
    passed_with_warnings = []
    unreachable = []
    ok_but_unreachable = []
    no_manifest = []

    for aid in ids:
        v = _load(root / f"{aid}.validation.json")
        n = _load(root / f"{aid}.navgate.json")
        if v is None:
            no_manifest.append(aid)
        else:
            warned = 0
            for gate, body in (v.get("gates") or {}).items():
                ws = (body or {}).get("warnings") or []
                if not ws:
                    continue
                warned += len(ws)
                per_gate[gate] += len(ws)
                for w in ws:
                    c = _code(str(w))
                    per_code[c] += 1
                    if aid not in code_owners[c]:
                        code_owners[c].append(aid)
            if warned and v.get("passed"):
                passed_with_warnings.append((aid, warned))
        if n is not None:
            checked = int((n.get("markers") or {}).get("checked") or 0)
            reach = int((n.get("markers") or {}).get("reachable") or 0)
            if checked and reach < checked:
                unreachable.append((aid, reach, checked))
                if n.get("ok"):
                    ok_but_unreachable.append(aid)

    print(f"library: {root}")
    print(f"  {len(ids)} shells, {len(ids) - len(no_manifest)} with a "
          f"validation manifest")
    if excluded:
        # Printed, not merely subtracted. Every denominator in this repo taken
        # before 2026-08-09 was taken against a library that included these,
        # so the difference has to be visible to compare an old figure to a
        # new one at all.
        print(f"  {len(excluded)} entr(y/ies) in this directory are NOT source "
              f"archetypes and are excluded from every count below:")
        for aid, why in excluded:
            print(f"      {aid:34} {why}")
    print()
    print(f"PASSED WITH WARNINGS: {len(passed_with_warnings)} of "
          f"{len(ids) - len(no_manifest)}")
    worst = sorted(passed_with_warnings, key=lambda t: -t[1])[:8]
    for aid, n_w in worst:
        print(f"    {aid:28} {n_w:>3} warning(s), passed=True")
    print()
    print("WARNINGS BY GATE (every one of these gates reports passed=True):")
    for gate, n_w in per_gate.most_common():
        print(f"    {gate:22} {n_w:>5}")
    print()
    print("WARNINGS BY CODE -- and how many shells a blocking promotion stops:")
    for code, n_w in per_code.most_common(14):
        owners = code_owners[code]
        print(f"    {code:44} {n_w:>5} on {len(owners):>4} shell(s)")
    print()
    print(f"UNREACHABLE MARKERS: {len(unreachable)} shell(s)")
    for aid, r, c in unreachable[:8]:
        print(f"    {aid:28} {r}/{c} reachable")
    if len(unreachable) > 8:
        print(f"    ... and {len(unreachable) - 8} more")
    print(f"  of which navgate still says ok=True: {len(ok_but_unreachable)}")
    if no_manifest:
        print()
        print(f"NO VALIDATION MANIFEST: {len(no_manifest)} shell(s) -- these "
              f"have never been judged at all")
        print("    " + ", ".join(no_manifest[:8]))

    if detail:
        print()
        print(f"--- shells carrying a '{detail}' warning ---")
        hits = [c for c in per_code if detail in c.upper()]
        for c in hits:
            print(f"  {c}: {len(code_owners[c])} shell(s)")
            print("    " + ", ".join(code_owners[c][:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
