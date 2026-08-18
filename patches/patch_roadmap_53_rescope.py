r"""Roadmap 53 RE-SCOPED -- the grep count was the symptom, not the cost.

    python patches\\patch_roadmap_53_rescope.py --check
    python patches\\patch_roadmap_53_rescope.py
    python patches\\patch_roadmap_53_rescope.py --selftest
    python tools\\roadmap_status.py --write

THREE EDITS to item 53: its STATUS, its title, and the middle of its body.
The two measured sections added later -- "CHASED AND CLOSED" and "MEASURED,
AND ONLY HALF ANSWERED" -- are left exactly as they are. They were expensive
and they are still true.

WHY

The item led with 27 literal sites across 8 modules. That is a real count and
the wrong headline. A shared constant does not decouple anything: a Lux
rename still edits Level Factory, in one file instead of eight, against a
name stable across 0.15.x-0.16.0. Meanwhile two checks cost something today
and neither is fixed by a constant:

    walk_preview.py:249   has_lux reads False and renders unlit in silence,
                          for a rename OR a failed job OR a dropped mode OR
                          an unlit package
    _preset_for           silent no-op on a wrong display name, PROVEN ON
                          HARDWARE -- and lux.quality.json already echoes the
                          applied preset back, so the check is a string
                          comparison over data that exists

Re-ranked accordingly, with the constant third and honest about what tidying
it buys.

NOTE: patch_roadmap_53.py --selftest WILL FAIL after this runs. That is
correct. Its checks assert the text as it stood when it ran, and this
supersedes that text. A patch selftest describes a moment, not an invariant.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r53re"
EDITS = [
    ("*STATUS: OPEN 2026-08-16 -- MEASURED. Item 47 separated Lux in the DAG and did not separate it at the file level: `lux.applied.tscn`, `lux.quality.json` and `lux.validation.json` are string literals in EIGHT modules across four packages, 27 matching lines. They do not fail alike -- the planner would fail loudly on a missing expected output while `walk_preview`'s `has_lux` would read False and silently render unlit. `_preset_for` additionally hardcodes Lux's preset DISPLAY names, where a wrong name is a documented silent no-op. Also carries the undecided interface: the fourth layer is expressed by subtraction and there is no positive `--light`*", "*STATUS: OPEN 2026-08-17 -- RE-SCOPED. The first draft led with a grep count -- `lux.applied.tscn` and its two siblings as string literals in 8 modules, 27 sites -- and that is the SYMPTOM, not the cost. A shared constant does not decouple anything: a Lux rename still breaks Level Factory, in one file instead of eight, and that name has been stable across 0.15.x-0.16.0. What costs something TODAY is two checks that find nothing and proceed: `walk_preview`'s `has_lux` reads False and silently renders unlit whatever the reason the file is absent, and `_preset_for`'s display-name mapping is a silent no-op on a wrong name, PROVEN ON HARDWARE per its own comment -- while `lux.quality.json` already echoes the applied preset back and nothing compares them. Ranked accordingly; the constant is third. The `--unlit` interface question is DECIDED: leave it*", "STATUS"),
    ('**53. Lux is decoupled in the graph and coupled by filename in eight\nmodules.**', '**53. Two Lux checks find nothing and carry on, and the filename literals\nare the symptom rather than the cost.**', "title"),
    ("**THE FIX IS ONE CONSTANT LUX OWNS AND EIGHT READERS IMPORT.** Where it lives\nis the decision: `adapters/lux/__init__.py` is Level Factory's boundary onto\nLux and already names all three, so it is the obvious home; the honest home\nis Lux itself, exported and consumed, which makes a Lux rename a Lux release\nrather than a Level Factory bug hunt. Both are defensible and they cost\ndifferently.\n\nTHE INTERFACE QUESTION, STILL UNDECIDED\n\n`--art` means art AND light. `--unlit` subtracts light. There is no positive\n`--light`. So the planner has a fourth layer and the CLI expresses it by\nnegation, with the coupled thing as the easy path and the decoupled one\nneeding a second flag.\n\nThe stated reason for the split was granularity -- that changing Lux should\nnot require touching level building. Under that reason the interface that\nsays so is `--art` = art, `--light` = light (implying art), and `--unlit`\ndisappears because it has nothing left to subtract. That is a breaking CLI\nchange and every existing brief, script and doc that says `--art` today means\nart+light, including `tools/run_3b_unlit.ps1`.\n\nNOT A DEFECT, AND DELIBERATELY NOT FILED AS ONE. Nothing is broken. This is a\ndecision that gets more expensive the longer anything builds on the current\nspelling, which is the only reason it is written down rather than left in a\nconversation.\n\n", '**WHAT ACTUALLY COSTS SOMETHING, IN ORDER.**\n\n**FIRST -- `walk_preview` renders unlit and says nothing.**\n\n```\nwalk_preview.py:249  has_lux = (dest / "presentation" / "lux.applied.tscn").is_file()\n```\n\nFalse is not an answer, and this treats it as one. The file is absent when\nLux was renamed, yes -- but also when `lux_apply` failed, when the mode\ndropped it, when the export did not carry it, or when somebody ran the\npreview on an unlit package. All five render a preview that is lit\ndifferently from the level, and the file\'s own words on why that matters are\nalready written down four bullets above the relevant note in\n`WALKABLE_SITE.md`: *"a preview that is lit differently from the level is\nworse than no preview, because it gets believed."* One file. No speculation.\nThe filename is incidental to it.\n\n**SECOND -- `_preset_for` is a silent no-op on a wrong name, and the\ncheck is free.**\n\nIt maps `time_of_day` onto Lux preset DISPLAY names -- "Blue Hour", "Delco\nSummer Afternoon", "Gas Station Fluorescent" -- and its own comment records\nthat a wrong name makes `blend_to_preset` do nothing, proven on hardware in\nthe Lux visual pass. Unlike everything else in this item, that has already\ncost something.\n\nIt is also nearly closed already, because the artifact answers it. Level\nFactory asks for a preset; `lux.quality.json` reports the one applied:\n\n```\nrequested   _preset_for(model)         ->  "Blue Hour"\napplied     lux.quality.json["preset"] ->  "Blue Hour"     (lot_demo_001, 2026-08-17)\n```\n\nNothing compares those two strings. A comparison turns a silent no-op into a\nfinding, needs no new data, and would have been exercised by the re-export\nrecorded below.\n\n**THIRD -- the filename literals, and they are genuinely third.**\n\n```\n9  packages/exporting/export.py        2  packages/pipeline/planner.py\n4  adapters/lux/__init__.py            2  packages/preview/walk_preview.py\n4  packages/exporting/localize.py      2  packages/service/facade.py\n3  apps/cli/commands/__init__.py       1  packages/exporting/closure.py\n```\n\n27 matching lines, 8 modules, 4 packages, for `lux.applied.tscn`,\n`lux.quality.json` and `lux.validation.json`. (Includes comment mentions; a\ncode-only pass returns the same eight modules.) No two readers agree on the\nsubset that matters -- `closure.py`\'s `_METADATA_FILES` names the two JSONs,\n`export.py`\'s `_PRESENTATION_FILES` names the scene and one JSON,\n`planner.py`\'s `expected_outputs` names all three.\n\n**Worth tidying, and honest about what tidying buys.** A shared constant does\nnot decouple: a Lux rename still edits Level Factory, in one place rather\nthan eight. That is a real improvement to a failure that has not happened --\nthe name has been stable across 0.15.x to 0.16.0 -- bought with an eight-file\nchange across four packages. Do it when something else already has those\nfiles open. Not as a project.\n\nWHERE THE CONSTANT WOULD GO, MEASURED\n\nDecided 2026-08-17: the Lux adapter, as the name a reader goes to. But the\nimport graph does not allow the literal version of that.\n`adapters/ -> packages/` is pervasive (every adapter imports\n`packages.adapters.sdk` and `packages.core.hashing`), while\n`packages/ -> adapters/` happens in exactly ONE file --\n`packages/adapters/registry.py:13-22`, which imports all ten adapters and is\na registry by design. A generic package importing one specific tool adapter\nwould invert that, and `adapters/lux/__init__.py` imports `packages.*` at\nmodule level, so it risks a real cycle rather than only an ugly edge.\n\nThe shape that survives: define in `packages/adapters/sdk.py` -- the shared\nsurface every adapter already imports -- and RE-EXPORT from\n`adapters/lux/__init__.py`, so `adapters.lux.LUX_APPLIED_SCENE` still\nresolves and the adapter stays the name. Moving the definition into Lux\nitself later is then a one-file change, because the eight readers already go\nthrough one symbol.\n\nTHE INTERFACE QUESTION: DECIDED, LEAVE IT\n\n`--art` means art AND light; `--unlit` subtracts. There is no positive\n`--light`, and there will not be one. Decided 2026-08-17. The spelling is\ncosmetic next to the two checks above, a positive `--light` is a breaking CLI\nchange touching every brief, script and doc that says `--art` today\n(including `tools/run_3b_unlit.ps1`), and the planner\'s fourth layer is real\nwhatever the flag calls it. Recorded as decided so it stops being reopened.\n\n', "body"),
]
_CRLF = "\r\n"


def _eol(b: str) -> str:
    c = b.count(_CRLF)
    return _CRLF if c > (b.count("\n") - c) else "\n"


def _as(t: str, eol: str) -> str:
    return t.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    b = raw.decode("utf-8")
    eol = _eol(b)
    out, done = b, 0
    for old, new, what in EDITS:
        o, n = _as(old, eol), _as(new, eol)
        if n in out:
            done += 1
        elif out.count(o) == 1:
            out = out.replace(o, n, 1)
        else:
            print(f"REFUSING: item 53's {what} anchor occurs {out.count(o)} "
                  f"time(s), expected 1")
            return 1
    if done == len(EDITS):
        print(f"  already applied  {ROADMAP}")
        return 0
    if done:
        print(f"REFUSING: {done} of {len(EDITS)} edits already present -- "
              f"part-patched")
        return 1
    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})   [eol="
              f"{'CRLF' if eol == _CRLF else 'LF'}]")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 "
          f"{hashlib.sha256(data).hexdigest()[:16]}")
    return 0


def selftest(root: Path) -> int:
    import re
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    md = (root / ROADMAP).read_bytes().decode("utf-8").replace(_CRLF, "\n")
    m = "**53. Two Lux checks find nothing and carry on"
    check("item 53 has the re-scoped title", m in md)
    if m not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    prose = md.split("<!-- END GENERATED -->", 1)[-1]
    check("...and the old title is gone from the prose",
          "coupled by filename in eight" not in prose)

    i = md.index(m)
    s = " ".join(md[:i].rstrip().splitlines()[-1].split())
    body = md[i:md.index("### Not to be worked on", i)]
    flat = " ".join(body.split())

    check("the STATUS says RE-SCOPED and why",
          s.startswith("*STATUS: OPEN 2026-08-17 -- RE-SCOPED")
          and "that is the SYMPTOM, not the cost" in s)
    check("...and states plainly what a constant does not buy",
          "A shared constant does not decouple anything" in s
          and "in one file instead of eight" in s)
    check("...and names the two that cost something today",
          "`walk_preview`'s `has_lux`" in s and "`_preset_for`" in s
          and "PROVEN ON HARDWARE" in s)
    check("...and records the interface decision as made",
          "is DECIDED: leave it" in s)

    check("the body ranks by consequence",
          "**WHAT ACTUALLY COSTS SOMETHING, IN ORDER.**" in body)
    check("1 is the silent preview, with all the reasons the file can be gone",
          "has_lux = (dest / \"presentation\" / \"lux.applied.tscn\").is_file()"
          in body
          and "False is not an answer" in flat
          and "All five render a preview" in flat)
    check("...and rests it on that file's own sentence",
          "worse than no preview, because it gets believed" in flat)
    check("2 is the preset no-op, with the comparison that closes it",
          "silent no-op on a wrong name, and the check is free" in flat
          and 'lux.quality.json["preset"]' in body
          and "Nothing compares those two strings" in flat)
    check("3 is the literals, demoted and honest",
          "THIRD -- the filename literals, and they are genuinely third."
          in body
          and "does\nnot decouple: a Lux rename still edits Level Factory" in body
          and "Not as a project." in flat)
    check("...keeping the per-module counts",
          "9  packages/exporting/export.py" in body
          and "1  packages/exporting/closure.py" in body)
    check("the import-direction measurement is recorded",
          "packages/adapters/registry.py:13-22" in body
          and "is a registry by design" in flat)
    check("...with the shape that survives it",
          "define in `packages/adapters/sdk.py`" in flat
          and "RE-EXPORT from" in body)
    check("the interface question is closed, not carried",
          "THE INTERFACE QUESTION: DECIDED, LEAVE IT" in body
          and "there will not be one" in flat
          and "so it stops being reopened" in flat)

    check("the expensive measured sections survived untouched",
          'CHASED AND CLOSED: "A VARIED LOT IS CURRENTLY UNLIT"' in body
          and "MEASURED, AND ONLY HALF ANSWERED" in body
          and '"fixture_lights": 136' in body)

    nums = [int(x) for x in re.findall(r"^\*\*(\d+)\. ", md, re.M)]
    check("the numbering is untouched", nums[-3:] == [51, 52, 53])
    # THE TRAP THIS PATCH FELL INTO FIRST. The ranked list was headed `**1.`,
    # `**2.`, `**3.` -- which is the shape `roadmap_status.py` parses as an
    # ITEM heading. The numbering came out 51, 52, 53, 1, 2, 3: three phantom
    # items inside item 53, and a derived table built from them.
    check("item 53 introduces no item-shaped headings of its own",
          not re.findall(r"^\*\*(\d+)\. ", body[40:], re.M))
    check("every fenced block in 53 is closed", body.count("```") % 2 == 0)
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  ranked by what it costs, not by how many times it is spelled"
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
        print("    python patches\\patch_roadmap_53_rescope.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print()
        print("  patch_roadmap_53.py --selftest will now FAIL. Correct:")
        print("  it asserts the text this supersedes.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
