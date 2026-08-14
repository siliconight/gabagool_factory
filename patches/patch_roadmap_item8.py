r"""Roadmap item 8: close the line that has been contradicting its own paragraph.

    python patch_roadmap_item8.py --check
    python patch_roadmap_item8.py
    python patch_roadmap_item8.py --selftest
    python patch_roadmap_item8.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

THE CONTRADICTION. Item 8 -- "Nothing checks the SIZE of the island an anchor
snaps to", which the file itself calls "the highest-leverage item in this
file" -- carries this status line:

    *STATUS: OPEN 2026-08-12 -- unchanged; this file's own
     "highest-leverage item", ~400 map_get_path queries*

Its own body, three lines below, says:

    Closed 2026-07-28, in two versions, and the second one is the lesson.
    Lot 0.26.0 built the census and it reported 0 stranded on a run where
    sixteen of twenty-one anchors could not be walked to ... Lot 0.28.0
    clusters on strict reachability only.

Two answers to one question, in the same item, and the derived table in
`PIPELINE_MAP`'s sibling section reports the wrong one. Exactly the shape of
`lot`'s VERSION saying 0.33.0 while its CHANGELOG said 0.41.0 -- and this one
sat on the item a reader would start with.

WHICH ONE IS RIGHT, ESTABLISHED BY MEASUREMENT RATHER THAN BY READING.

Code, on disk today:

    level_factory/adapters/walktest/__init__.py:324  emits
        "WALKTEST_ANCHOR_ISOLATED", "anchor"
    ... and carries the `stranded` set through leg suppression at 276-360
    lot/lot.py:1607  # stranded anchor once already -- it "reached" its own
                     # twin and passed

That last comment IS the 0.26.0 lesson, recorded at the site of the fix.

Report, from the candidate that shipped -- `lot_demo_001.candidate.seed_5219`,
`out/site_navqa.walktest.json`:

    top-level keys include  anchors, anchors_behind_a_barrier,
                            anchors_without_standing_room, stranded_anchors
    anchors                 22
    reaches                 21 on every one
    cluster_size            22, main_cluster_size 22
    no_standing_room        False on every one
    snap_m                  0.15 - 0.90, all inside SNAP_MAX 2.0

Twenty-two anchors, each reaching the other twenty-one, one cluster, nothing
stranded. The measurement item 8 asked for exists, runs, and passes.

WHAT THIS PATCH DOES AND DOES NOT DO. It replaces one status line. The item's
prose is already correct and is not touched -- it is the status stamp that
drifted, not the argument. The evidence recorded is the report's own numbers
rather than "closed", because a status line that says only OPEN or CLOSED is
how this one got to be wrong for two weeks without anyone noticing.

AFTERWARDS, REGENERATE THE TABLE. `roadmap_status.py --write` derives the
table from these lines the way `factory_map.py` maintains the DAG table, and
`--check` exits 1 on drift. The table is not edited by hand here.

NOT CLOSED, AND WORTH SAYING: item 9's residual gap stands. Lot still cannot
answer "is this anchor over anything?" offline -- it knows ground tiles,
footprint holes and storey elevations, and nothing checks the props. Every
result above came from Godot after the fact. That is a different item.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_item8"

OLD = ('*STATUS: OPEN 2026-08-12 -- unchanged; this file\'s own '
       '"highest-leverage item", ~400 map_get_path queries*')

NEW = ('*STATUS: CLOSED 2026-08-14 -- shipped as Lot 0.28.0 + Level Factory '
       '0.18.0; the seed_5219 report carries anchors[22], reaches 21 on every '
       'one, one cluster of 22, 0 stranded, 0 without standing room. The '
       'status line said OPEN while this item\'s own body said closed on '
       '2026-07-28*')

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor.

    This one is mixed: 3,388 CRLF in 202,985 bytes, the rest bare LF. The
    status line is a single line with no internal newline, so the replacement
    is EOL-neutral -- but the count is checked below rather than assumed.
    """
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    p = root / TARGET
    if not p.is_file():
        print(f"REFUSING: {TARGET} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")

    if NEW in body:
        print("  already applied")
        return 0
    if body.count(OLD) != 1:
        print(f"REFUSING: the item-8 status line occurs {body.count(OLD)} "
              f"time(s), expected 1")
        return 1
    # The item's argument must still be there -- this closes a stamp, not a
    # finding.
    if "Nothing checks the SIZE of the island an anchor snaps to" not in body:
        print("REFUSING: item 8's own heading is not where it was")
        return 1

    before_crlf = raw.count(_CRLF.encode())
    out = body.replace(OLD, NEW, 1)
    data = out.encode("utf-8")
    if data.count(_CRLF.encode()) != before_crlf:
        print("REFUSING: the CRLF count changed -- the edit is not "
              "line-ending neutral")
        return 1

    if check:
        print(f"  would patch  {TARGET}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {TARGET}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    t = (root / TARGET).read_text(encoding="utf-8")
    #: Prose assertions run against a whitespace-collapsed copy. The phrases
    #: below wrap across lines in the source, and the first draft of this
    #: selftest failed on two of them for that reason alone -- an assertion
    #: about content should not be an assertion about where the text wrapped.
    flat = " ".join(t.split())

    check("item 8 now reads CLOSED", NEW in t)
    check("the old OPEN stamp is gone", OLD not in t)
    check("it carries the report's numbers, not just a verdict",
          "anchors[22]" in t and "0 stranded" in t)
    check("it names the versions that shipped it",
          "Lot 0.28.0" in t and "Level Factory 0.18.0" in t)
    check("it records that the line contradicted its own body",
          "own body said closed" in t)
    check("item 8's argument is untouched",
          "The measurement to add uses only the engine" in flat
          and "connectivity metric built out of a permissive predicate "
              "measures the predicate" in flat)
    check("item 9's residual gap is untouched",
          "Lot still cannot answer" in flat
          and "is this anchor over anything?" in flat)
    check("the other status lines are untouched",
          t.count("*STATUS: OPEN 2026-08-12 -- unchanged*") >= 1)

    # The derived table must now be stale -- that is the point, and
    # roadmap_status.py --write is the next step.
    if "| 8 | **OPEN**" in t:
        print("  note  the generated table still says OPEN -- run "
              "`python tools\\roadmap_status.py --write`")
    else:
        check("the table already agrees", "| 8 | **CLOSED**" in t)

    print()
    print("  item 8's stamp agrees with item 8's argument"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        p = root / TARGET
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {TARGET}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {TARGET}")
        return 0

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  python patches\\patch_roadmap_item8.py --selftest")
        print("  python tools\\roadmap_status.py --write   "
              "# regenerate the derived table")
        print("  python tools\\roadmap_status.py --check   # expect exit 0")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
