r"""Roadmap item 48 -- the same job, the same seed, a different building.

    python patches\patch_roadmap_48.py --check
    python patches\patch_roadmap_48.py
    python patches\patch_roadmap_48.py --selftest
    python patches\patch_roadmap_48.py --revert

Run from the FACTORY ROOT. Then regenerate the derived table:

    python tools\roadmap_status.py --write

TWO EDITS, ONE FILE

1. Item 47's STATUS line is rewritten. Stage 3b RAN. It answered both of the
   questions it existed to answer, and then hit something that is not 47's
   problem -- so 47 should say 3b ran, and the new thing should be its own
   item rather than a paragraph buried in 47.

2. Item 48 is inserted before "### Not to be worked on", the same anchor
   patch_roadmap_47.py used.

WHY THIS IS WRITTEN TONIGHT

Every number in it came off disk in the last hour: two site specs, four
adapter fingerprints, and a run log. Reconstructed tomorrow, the timestamps
would be an argument instead of a measurement -- and the workspace that holds
them is a scratch workspace this session created and could just as easily
delete.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r48"

# ---------------------------------------------------------------- edit 1
#
# BOTH ENDS OF THE LINE. Rewriting only the tail leaves the head saying
# "3b remains" three sentences above a sentence saying "3b RAN" -- which is
# how a status line stops being read.
EDIT_47 = [
    (
        # The `*STATUS: NARROWED 2026-08-15 -- ` prefix is load-bearing. The
        # bare phrase occurs TWICE: once here and once in the DERIVED table
        # at line ~728, which roadmap_status.py rewrites. Anchoring on the
        # phrase alone made this patch refuse, correctly, on the first try.
        "*STATUS: NARROWED 2026-08-15 -- stages 1-3a shipped and measured; "
        "3b remains.",
        "*STATUS: NARROWED 2026-08-15 -- stages 1 through 3b have all RUN; "
        "the layer split is proven and the first cold package is blocked by "
        "item 48.",
    ),
    (
        "REMAINS: 3b, a mission RUN with `--art --unlit` through Blender and "
        "Godot -- factory 1.24.0 certifies the set without it*",
        "3b RAN 2026-08-15 on `unlit_probe_001` through Blender and headless "
        "Godot and answered both of its questions: `lux_apply` never ran, "
        "`lux_fixture_gate` did, `dispatch_handoff <- themed_site_assemble`. "
        "Export was then blocked -- IDENTICALLY in `art-unlit` and "
        "`portable-godot`, which acquits `--unlit` -- by a functional "
        "regression that is item 48, not this item. The layer split is "
        "proven; a package built end-to-end from a cold run is not, and "
        "cannot be until 48 is*",
    ),
]

# ---------------------------------------------------------------- edit 2
INSERT = '''*STATUS: OPEN 2026-08-15 -- MEASURED on unlit_probe_001, one workspace, one seed. `lot_assemble.candidate.seed_5017` succeeded twice in `_runs/3b/run.log` (lines 31 and 51) and drew a different building each time: graybox `cr_garage` (17 openings, 178 colliders, 12 markers), art `landmark_hall_a03` (13 openings, 176 colliders, 7 markers), with `shell.glb` byte-identical across both fingerprints. Everything that graded the mission graded the first draw. The functional lock caught it and refused the export -- this item is the redraw, not the lock*

**48. The same job and the same seed draw a different building on the art
pass, and everything that graded the mission graded the other one.**
`unlit_probe_001` was a fresh workspace built for roadmap 47 stage 3b: one
mission, one candidate, seed 5017, run once from empty. In it,
`unlit_probe_001.lot_assemble.candidate.seed_5017` -- one job id, one
candidate, one seed -- ran twice and produced two different sites.

```
_runs/3b/run.log:31   under `batch create`
_runs/3b/run.log:51   under `run --art --unlit --gameplay`
```

The two draws, from the adapter fingerprints and the two site specs:

```
                          building           openings  colliders  markers
graybox  22:01:21Z        cr_garage                17        178       12
art      21:49:26Z        landmark_hall_a03        13        176        7
```

(Those two timestamps are the fingerprints that survive on disk. The FIRST
graybox assemble, the one under `batch create`, has been overwritten by the
third -- `fingerprint.last.json` keeps only the last. Its building is known
from the lock and the graders it fed, which measured `cr_garage`.)

`shell.glb` hashes `a929d7d2...` in BOTH fingerprints. The lot is the same
lot. The building standing in it is not.

**The pipeline says so itself, in a line written to reassure:**

```
[site] graded lot (art run): 98 of 123 shell(s) can carry a theme
       -- the graded draw and the shipped draw come from the same pool
```

Same pool, different filter. A seeded draw over 98 candidates does not land
on the same element as a seeded draw over 123, and the sentence that says
"the same pool" carries both numbers -- the reassurance and the evidence
against it are the same string.

**Everything that graded the mission graded the first draw.**
`walktest_navqa`, `laser_tag_evaluate`, the structural checks (14 findings)
and the functional lock all completed under `batch create`, before the art
run re-drew. Their verdicts describe `cr_garage`. The package would have
shipped `landmark_hall_a03`.

**The lock caught it, and that is the good news.** Export refused, in both
modes:

```
export blocked by functional regression:
  - collision_fingerprint changed after art pass
  - gameplay-anchor registry changed after art pass
```

That is the functional lock doing precisely the job it was built for, on its
first mission that ever put it to the test. Nothing else in the pipeline is
positioned to notice: the graders never see the second site, and the export
closure scan checks that files resolve, not that they are the ones that were
graded. **Any fix that makes this export succeed by relaxing the lock is the
wrong fix.**

**And a third `lot_assemble`, graybox, at 22:01:21Z drew `cr_garage` again**
-- so the unthemed draw is stable across invocations and the themed one is
the departure. That rules out plain seed nondeterminism.

THE SECOND HALF: NOTHING CAN JOIN A GRADE TO A SITE

Even where the draw does not move, no artifact can prove the graded scene is
the assembled one, because the two sides record disjoint identifiers:

```
lot_assemble         building_hashes + site_spec_hash   no scene hash
walktest_navqa       scene_hash                          no building hashes
laser_tag_evaluate   scene_hash                          no building hashes
```

There is no key in common, so "did the graders grade what shipped?" is not a
question this system can be asked -- it is inferred from job ordering. On
`lot_demo_001` the inference happens to hold, and only by 19 seconds:
`lot_assemble` at `2026-08-13T23:20:57`, walktest at `23:21:16.383`, Laser
Tag at `23:21:16.984`. The two graders' own `scene_hash` values differ from
each other (`b3bd2815...`, `abf3edf5...`), so they do not agree on a subject
identifier either.

**`lot_demo_001`'s lock has never guarded an art pass.** It was approved
`2026-08-14T22:56`, 23h36m after that assemble, so it records a post-art
state and there is nothing left for it to disagree with. It exports cleanly
for that reason and not because its draw is stable. Item 47's stages 1-3a
were all measured on that mission, which is why none of them saw this.

QUESTIONS BEFORE CODE

1. **May the draw narrow after a candidate is approved at all?**
   `candidate_selected` is a HUMAN approval. As it stands, the art pass
   re-runs the draw behind that approval and can hand back a different
   building. The cheapest correct answer may be that the themed re-draw is
   simply not allowed to change the building -- theme the one that was
   approved, or fail.
2. **Or constrain the graybox draw to the 98 from the start?** Then the
   graded and shipped buildings are the same object by construction. It
   costs 25 shells of variety and buys the entire question.
3. **Is `lot_assemble` one job or two?** One job id producing two different
   sites in one workspace is exactly what makes this invisible in a job
   listing, in `index.sqlite`, and in the run log -- both lines say
   "succeeded".
4. **What does a fingerprint have to carry for the question to be
   askable?** The minimum is a shared key: the assemble emitting the scene
   hash it wrote, or the graders emitting the building set they loaded.
   Either one turns the joinability gap into a query.

RELATED, AND NOT THE SAME

Item 43 was "a whole CLI spelling stopped working and nothing noticed." Item
5 was "a run that evaluated nothing reported a clean pass." Both are the same
family as the second half of this item -- a check that cannot see what it
claims to cover -- but the first half is not that. The first half is a
producer that gives two answers to one question, and it was caught, by the
one guard built to catch it.

'''

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    """KEYED OFF THE FILE, never off an anchor.

    PIPELINE_ROADMAP.md is CRLF while every file under level_factory/ is LF,
    and `Path.read_text()` normalises newlines -- so a check written with
    read_text reports a CRLF file as LF and an LF-only patch then refuses a
    file it could have handled.
    """
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    out = body
    already = 0

    # -- edit 1: item 47's status now says 3b ran ------------------------
    done47 = 0
    for old, new in EDIT_47:
        o, n = _as(old, eol), _as(new, eol)
        if n in out:
            done47 += 1
        elif out.count(o) == 1:
            out = out.replace(o, n, 1)
        else:
            print(f"REFUSING: an item 47 STATUS fragment occurs "
                  f"{out.count(o)} time(s), expected 1 -- has that line been "
                  f"edited since factory 1.24.0?\n  {old[:60]}...")
            return 1
    if done47 and done47 != len(EDIT_47):
        print(f"REFUSING: item 47's STATUS line is half-rewritten "
              f"({done47} of {len(EDIT_47)} fragments already new)")
        return 1
    already += 1 if done47 else 0

    # -- edit 2: item 48 -------------------------------------------------
    anchor = _as("\n### Not to be worked on\n", eol)
    marker = _as("**48. The same job and the same seed draw", eol)
    if marker in out:
        already += 1
    elif out.count(anchor) == 1:
        out = out.replace(
            anchor, _as("\n" + INSERT + "### Not to be worked on\n", eol), 1)
    else:
        print(f"REFUSING: the 'Not to be worked on' heading occurs "
              f"{out.count(anchor)} time(s), expected 1")
        return 1

    if already == 2:
        print(f"  already applied  {ROADMAP}")
        return 0
    if already == 1:
        print("REFUSING: exactly one of the two edits is already present -- "
              "the file is half-patched. Revert or fix by hand.")
        return 1

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import re
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    disk = (root / ROADMAP).read_bytes().decode("utf-8")
    check("the file's line endings are preserved",
          disk.count(_CRLF) > 0 or "\r" not in disk)
    md = disk.replace(_CRLF, "\n")
    flat = " ".join(md.split())

    # -- edit 1 ----------------------------------------------------------
    i47 = md.index("**47. A recipient")
    s47 = md[:i47].rstrip().splitlines()[-1]
    check("item 47's status now says 3b RAN", "3b RAN 2026-08-15" in s47)
    check("...at BOTH ends of the line, so it does not contradict itself",
          "1 through 3b have all RUN" in s47 and "3b remains" not in s47
          and "REMAINS: 3b" not in s47)
    check("...and hands the blocker to item 48",
          "that is item 48, not this item" in s47)
    check("...and still records what 3b actually observed",
          "`lux_apply` never ran" in s47 and "which acquits `--unlit`" in s47)

    # -- edit 2 ----------------------------------------------------------
    marker = "**48. The same job and the same seed draw"
    check("item 48 is present", marker in md)
    if marker not in md:
        # Bail cleanly rather than raising out of the middle of the report.
        # A selftest that ends in a traceback is a selftest whose remaining
        # checks nobody can read.
        print()
        print(f"  {bad} FAILURE(S) -- item 48 is not in the file; "
              f"run the patch first")
        return 1
    i48 = md.index(marker)
    before = md[:i48].rstrip().splitlines()[-1]
    check("it carries a STATUS line directly above it",
          before.startswith("*STATUS: ") and before.endswith("*"))
    check("the status is OPEN and carries the measurement, not a plan",
          before.startswith("*STATUS: OPEN 2026-08-15")
          and "cr_garage" in before and "landmark_hall_a03" in before)
    check("the numbering is contiguous through 48",
          [int(m) for m in re.findall(r"^\*\*(\d+)\. ", md, re.M)][-3:]
          == [46, 47, 48])

    body = md[i48:md.index("### Not to be worked on", i48)]
    bflat = " ".join(body.split())

    check("it cites the two run.log lines by number",
          "_runs/3b/run.log:31" in body and "_runs/3b/run.log:51" in body)
    # NOT `"17" in body` -- "17" is a substring of "178" and of a timestamp,
    # so that check could not fail. Match the table rows themselves.
    check("it gives both draws with their counts",
          re.search(r"graybox\s+22:01:21Z\s+cr_garage\s+17\s+178\s+12", body)
          is not None
          and re.search(
              r"art\s+21:49:26Z\s+landmark_hall_a03\s+13\s+176\s+7", body)
          is not None)
    check("it records that the shell is identical",
          "a929d7d2" in body and "The lot is the same" in bflat)
    check("it quotes the reassurance line and both of its numbers",
          "98 of 123" in body and "the same pool" in bflat)
    check("it names what graded the FIRST draw",
          "walktest_navqa" in body and "laser_tag_evaluate" in body
          and "before the art run re-drew" in bflat)
    check("it quotes the lock's actual refusal, both findings",
          "collision_fingerprint changed after art pass" in body
          and "gameplay-anchor registry changed after art pass" in body)
    check("it says the lock is not the defect",
          "relaxing the lock is the wrong fix" in bflat)
    check("it rules out plain seed nondeterminism with the third assemble",
          "22:01:21Z" in body and "rules out plain seed nondeterminism"
          in bflat)
    check("the joinability half names the disjoint identifiers",
          "building_hashes" in body and "scene_hash" in body
          and "no key in common" in bflat)
    check("...with lot_demo_001's 19 seconds as the only evidence there",
          "2026-08-13T23:20:57" in body and "23:21:16.383" in body
          and "23:21:16.984" in body)
    check("...and that its lock post-dates its assemble",
          "2026-08-14T22:56" in body and "23h36m" in body)
    check("all four questions are there",
          "1. **May the draw narrow" in body
          and "2. **Or constrain the graybox draw" in body
          and "3. **Is `lot_assemble` one job or two?**" in body
          and "4. **What does a fingerprint have to carry" in body)
    check("it separates the two halves rather than merging them",
          "the first half is not that" in bflat)

    # -- structural ------------------------------------------------------
    check("every fenced block in item 48 is closed",
          body.count("```") % 2 == 0)
    check("the item ends with a blank line before the next heading",
          body.endswith("\n\n"))
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  measured tonight, off disk, while the workspace still exists"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        p = root / ROADMAP
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {ROADMAP}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {ROADMAP}")
        return 0
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_roadmap_48.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
        print()
        print("  the table at the top is DERIVED -- it will not show 48")
        print("  until --write regenerates it.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
