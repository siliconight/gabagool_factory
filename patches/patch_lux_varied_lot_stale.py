r"""The "varied lot is currently UNLIT" claim -- chased, and it is stale.

    python patches\\patch_lux_varied_lot_stale.py --check
    python patches\\patch_lux_varied_lot_stale.py
    python patches\\patch_lux_varied_lot_stale.py --selftest
    python patches\\patch_lux_varied_lot_stale.py --revert
    python tools\\roadmap_status.py --write

TWO FILES, TWO REPOS. Run from the FACTORY ROOT; commit separately.

    level_factory/docs/WALKABLE_SITE.md   bullet 124-126 marked SUPERSEDED
                                          in place  (level_factory repo)
    PIPELINE_ROADMAP.md                   the check appended to item 53
                                          (factory repo)

WHAT WAS CHECKED

`docs/extracted/site.md:1139` quotes WALKABLE_SITE.md saying a varied lot is
never lit because `lux_apply` targets `presentation/site.tscn`. Read out of
`apps/cli/commands/__init__.py` (126,865 B, sha256 20188C0F...), lines
637-653: `lux_apply` targets `themed_site_assemble`'s `site.tscn` whenever
that job is planned. `presentation/site.tscn` is the `elif`. The claim
described the fallback branch and predates the stage that made it a fallback.

SUPERSEDED IN PLACE, NOT DELETED. The bullet is the reason somebody chased
this; removing it would let the next reader chase it again from `site.md`,
which quotes it. `site.md` itself is generated into `docs/extracted/` and is
not touched.

WHAT IT DOES NOT CLAIM. That the light LANDS. The assembly instances the
composed buildings and whether a LuxRoot reaches inside instanced sub-scenes
is a render-time question; four bullets up in the same file is a recorded
case of light not travelling (152 fixture lights reported, `OmniLight3D 0`
running). Both files say so.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

WALK = "level_factory/docs/WALKABLE_SITE.md"
ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_luxstale"
ANCHOR = "\n### Not to be worked on\n"
OLD_W = '- **A varied lot is currently UNLIT** regardless: `lux_apply` lights\n  `presentation/site.tscn`, the mission shell, which a varied lot does not\n  place. See `RENDER_PASS_SPLIT.md` and `VARIED_THEMED_LOT.md`.\n'
NEW_W = '- **A varied lot is currently UNLIT** regardless: `lux_apply` lights\n  `presentation/site.tscn`, the mission shell, which a varied lot does not\n  place. See `RENDER_PASS_SPLIT.md` and `VARIED_THEMED_LOT.md`.\n  **SUPERSEDED 2026-08-17, and left standing rather than deleted.** That was\n  true before `themed_site_assemble` existed. `commands/__init__.py:637-653`\n  now picks the assembled SITE whenever that job is planned, and only falls\n  back to the composer\'s root when it is not:\n\n  ```python\n  themed_job = _dep(job, "themed_site_assemble")\n  if themed_job:\n      composed_scene = _latest_output(jobs_dir / themed_job, "site.tscn")\n  elif compose_job:\n      composed_scene = _latest_output(jobs_dir / compose_job,\n                                      "presentation/site.tscn")\n  ```\n\n  The branch carries the comment naming this exact defect as already fixed:\n  *"Lighting the composed building instead put one LuxRoot over one building\n  and called it a level (roadmap 29/34)."* The adapter hardcodes nothing --\n  `adapters/lux/__init__.py:53` reads `job_spec["composed_scene"]` -- so the\n  scene targeting was never Lux\'s to get wrong.\n\n  WHAT IS STILL UNMEASURED, and it is not this: the assembly INSTANCES the\n  composed buildings, and whether a LuxRoot over the assembly reaches inside\n  instanced sub-scenes at render time is a question no reading settles. The\n  bullet four above this one is the reason to ask it -- `lux.quality.json`\n  reported 152 fixture lights while the preview ran `OmniLight3D 0`. Answering\n  it needs a varied lot exported and opened, which nothing has done since\n  level_factory 0.39.0.\n'
ADD = 'CHASED AND CLOSED: "A VARIED LOT IS CURRENTLY UNLIT"\n\n`level_factory/docs/extracted/site.md:1137-1145` carries, as a known\nconsequence, that a varied lot never gets lit at all:\n\n> "**A varied lot is currently UNLIT** regardless: `lux_apply` lights\n> `presentation/site.tscn`, the mission shell, which a varied lot does not\n> place."  -- `WALKABLE_SITE.md:124-126`\n\nIf current that would enlarge this item considerably -- it would mean `--art`\non a multi-building mission has been shipping unlit packages by accident\nrather than by flag. It is NOT current. From\n`apps/cli/commands/__init__.py` (126,865 B, sha256 20188C0F...), lines\n637-653:\n\n```python\nthemed_job  = _dep(job, "themed_site_assemble")\ncompose_job = _dep(job, "presentation_compose")\nif themed_job:\n    # The themed SITE: Lot\'s assembly of the composed building at\n    # the candidate\'s own placements. Lighting the composed building\n    # instead put one LuxRoot over one building and called it a\n    # level (roadmap 29/34).\n    composed_scene = _latest_output(jobs_dir / themed_job, "site.tscn")\nelif compose_job:\n    composed_scene = _latest_output(jobs_dir / compose_job,\n                                    "presentation/site.tscn")\n```\n\n`lux_apply` lights the ASSEMBLED SITE whenever `themed_site_assemble` is\nplanned, which is whenever the art layer runs; `presentation/site.tscn` is\nthe `elif`. And the adapter hardcodes nothing -- `adapters/lux/__init__.py:53`\nreads `job_spec["composed_scene"]` and refuses without it -- so the scene\ntargeting was never Lux\'s to get wrong, which is worth knowing for this\nitem\'s own question about where the seam belongs.\n\n**BOTH SOURCES THAT SECTION RESTS ON ARE STALE.** `WALKABLE_SITE.md:124-126`\npredates `themed_site_assemble`, and its own "Related open work" lists the\n`--render` split as the thing that would "light the varied lot". The other,\n`VARIED_THEMED_LOT.md:8-11` -- "`run <mission> --art` -> ONE building repeated\nN times" -- predates one-compose-per-archetype, which\n`tests/test_presentation_lot.py` now pins with `len(cmds) == 1 + len(lot)`.\n`WALKABLE_SITE.md` has been marked superseded in place rather than edited\naway. `site.md` is generated into `docs/extracted/` and is left alone; it was\nhonest about itself -- "the known consequence is documented rather than\nmeasured" -- and that caveat is the only reason this was catchable instead of\nbelieved.\n\nWHAT THE READING DOES NOT SETTLE\n\nThe assembly INSTANCES the composed buildings. Whether a LuxRoot over the\nassembly reaches inside instanced sub-scenes at render time is not a question\nany amount of reading answers, and this pipeline has a recorded instance of\nlight not travelling: `WALKABLE_SITE.md:115-120` reports `lux.quality.json`\nat 152 fixture lights while the preview ran `OmniLight3D 0`, with the note\n*"a preview that is lit differently from the level is worse than no preview,\nbecause it gets believed."* Different mechanism, same hazard.\n\nIt is answerable by the thing already on the list -- re-export `lot_demo_001`\nunder 0.39.0/0.40.0 and open it. Five buildings is exactly the shape item\n49\'s fix leaves untouched, and nothing has re-measured it since.\n\n'
_CRLF = "\r\n"


def _eol(b: str) -> str:
    c = b.count(_CRLF)
    return _CRLF if c > (b.count("\n") - c) else "\n"


def _as(t: str, eol: str) -> str:
    return t.replace(_CRLF, "\n").replace("\n", eol)


def _one(p: Path, old: str, new: str, *, check: bool, label: str) -> int:
    raw = p.read_bytes()
    b = raw.decode("utf-8")
    eol = _eol(b)
    o, n = _as(old, eol), _as(new, eol)
    if n in b:
        print(f"  already applied  {label}")
        return 0
    if b.count(o) != 1:
        print(f"REFUSING: the anchor in {label} occurs {b.count(o)} time(s), "
              f"expected 1")
        return 1
    data = b.replace(o, n, 1).encode("utf-8")
    if check:
        print(f"  would patch  {label}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})   [eol="
              f"{'CRLF' if eol == _CRLF else 'LF'}]")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {label}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 "
          f"{hashlib.sha256(data).hexdigest()[:16]}")
    return 0


def _apply(root: Path, *, check: bool) -> int:
    missing = [r for r in (WALK, ROADMAP) if not (root / r).is_file()]
    if missing:
        print("REFUSING: not here -- run from the factory root: "
              + ", ".join(missing))
        return 1
    rm = (root / ROADMAP).read_bytes().decode("utf-8")
    if "**53. Lux is decoupled in the graph" not in rm:
        print("REFUSING: item 53 is not in the roadmap -- run "
              "patches\\patch_roadmap_53.py first")
        return 1
    rc = _one(root / WALK, OLD_W, NEW_W, check=check, label=WALK)
    if rc:
        return rc
    return _one(root / ROADMAP, ANCHOR,
                "\n" + ADD + "### Not to be worked on\n",
                check=check, label=ROADMAP)


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    w = (root / WALK).read_text(encoding="utf-8").replace(_CRLF, "\n")
    wf = " ".join(w.split())
    check("the bullet is still there, not deleted",
          "**A varied lot is currently UNLIT** regardless" in w)
    check("...and is marked superseded with a date",
          "**SUPERSEDED 2026-08-17, and left standing rather than deleted.**"
          in w)
    check("...citing the lines that supersede it",
          "commands/__init__.py:637-653" in w)
    check("...and quoting the branch, not describing it",
          'composed_scene = _latest_output(jobs_dir / themed_job, "site.tscn")'
          in w)
    check("...and that the adapter hardcodes nothing",
          "adapters/lux/__init__.py:53" in wf
          and "never Lux's to get wrong" in wf)
    check("...and keeps the render-time question open",
          "WHAT IS STILL UNMEASURED" in w
          and "instanced sub-scenes" in wf)
    check("...pointing at the recorded case of light not travelling",
          "152 fixture lights" in wf and "OmniLight3D 0" in wf)

    md = (root / ROADMAP).read_bytes().decode("utf-8").replace(_CRLF, "\n")
    m53 = "**53. Lux is decoupled in the graph"
    check("item 53 is there", m53 in md)
    if m53 not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    body = md[md.index(m53):md.index("### Not to be worked on",
                                     md.index(m53))]
    flat = " ".join(body.split())
    check("the check is recorded inside item 53",
          "CHASED AND CLOSED:" in body)
    check("...stating what it would have meant if true",
          "shipping unlit packages by accident rather than by flag" in flat)
    check("...and that it is not current, with the hash-stamped source",
          "It is NOT current" in flat and "sha256 20188C0F" in body)
    check("...quoting the branch verbatim",
          'if themed_job:' in body and 'elif compose_job:' in body)
    check("...and naming BOTH stale sources with what superseded each",
          "WALKABLE_SITE.md:124-126" in body
          and "VARIED_THEMED_LOT.md:8-11" in body
          and "len(cmds) == 1 + len(lot)" in body)
    check("...and says site.md is generated and left alone",
          "generated into `docs/extracted/`" in flat)
    check("...and credits site.md's own caveat",
          "documented rather than\nmeasured" in body
          or "documented rather than measured" in flat)
    check("the unsettled half is kept as a question",
          "WHAT THE READING DOES NOT SETTLE" in body
          and "not a question any amount of reading answers" in flat)
    check("...with the way to answer it",
          "re-export `lot_demo_001`" in flat
          and "nothing has re-measured it since" in flat)

    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  a stale doc marked stale, and the half nobody has measured kept"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        rc = 0
        for rel in (WALK, ROADMAP):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if side.is_file():
                p.write_bytes(side.read_bytes())
                print(f"  reverted     {rel}")
            else:
                print(f"  no sidecar for {rel}")
                rc = 1
        return rc
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lux_varied_lot_stale.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print()
        print("  TWO REPOS -- commit WALKABLE_SITE.md from level_factory\\,")
        print("  PIPELINE_ROADMAP.md from the factory root.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
