r"""Roadmap 53 CORRECTED -- walk_preview was not the defect I said it was.

    python patches\\patch_roadmap_53_correct.py --check
    python patches\\patch_roadmap_53_correct.py
    python patches\\patch_roadmap_53_correct.py --selftest
    python tools\\roadmap_status.py --write

THREE EDITS: item 53's STATUS, its title, and the ranked block. The measured
sections below it -- "CHASED AND CLOSED" and "MEASURED, AND ONLY HALF
ANSWERED" -- and "WHERE THE CONSTANT WOULD GO" are untouched.

WHAT WAS WRONG

The previous re-scope ranked `walk_preview`'s `has_lux` first, as a check
that finds nothing and carries on. Read (18,781 B, sha256 3400109C...) it is
not one:

    308  has_lux = (dest/"presentation"/"lux.applied.tscn").is_file()
    311  has_lux = "addons/lux" in (dest/level).read_text()   # fallback
    325  else: build a preview RIG -- DirectionalLight3D, shadows, bias
    376  lighting = "lux (content-owned)" if has_lux else "preview rig"
    393  return {..., "lighting": lighting, ...}

Two-way detection, no unlit render, and the choice is REPORTED. Withdrawn.
The 152-vs-OmniLight3D-0 incident belongs to `walk_fixtures.gd`, not here.

That leaves ONE ranked defect -- `_preset_for` -- and the literals as
tidiness with one correctly-stated consequence.

WHY THE WITHDRAWAL IS IN THE ITEM RATHER THAN JUST REVERTED

It was ranked from a grep line whose line number had already moved, 249 to
308. That is the same failure the item warns about, committed inside the
section arguing against it. An item that quietly dropped it would lose the
only part a future reader can learn from.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r53co"
EDITS = [
    ("*STATUS: OPEN 2026-08-17 -- RE-SCOPED. The first draft led with a grep count -- `lux.applied.tscn` and its two siblings as string literals in 8 modules, 27 sites -- and that is the SYMPTOM, not the cost. A shared constant does not decouple anything: a Lux rename still breaks Level Factory, in one file instead of eight, and that name has been stable across 0.15.x-0.16.0. What costs something TODAY is two checks that find nothing and proceed: `walk_preview`'s `has_lux` reads False and silently renders unlit whatever the reason the file is absent, and `_preset_for`'s display-name mapping is a silent no-op on a wrong name, PROVEN ON HARDWARE per its own comment -- while `lux.quality.json` already echoes the applied preset back and nothing compares them. Ranked accordingly; the constant is third. The `--unlit` interface question is DECIDED: leave it*", '*STATUS: OPEN 2026-08-17 -- CORRECTED, second re-scope. The previous one ranked `walk_preview`\'s `has_lux` first as a check that finds nothing and carries on. IT IS NOT ONE: it has a documented two-way detection, it does not render unlit but substitutes a preview RIG, and it reports which it used -- `lighting: "lux (content-owned)" | "preview rig"` in its return value. Withdrawn, with what it actually does, at `walk_preview.py:308-314,376` (18,781 B, sha256 3400109C...). That leaves ONE ranked defect: `_preset_for` is a silent no-op on a wrong Lux preset display name, PROVEN ON HARDWARE per its own comment, and `lux.quality.json` already echoes the applied preset back while nothing compares them. The 27 filename literals across 8 modules stay third and stay tidiness. `--unlit` interface: DECIDED, leave it*', "STATUS"),
    ('**53. Two Lux checks find nothing and carry on, and the filename literals\nare the symptom rather than the cost.**', '**53. One Lux check is a silent no-op, and the filename literals are\ntidiness with one real consequence.**', "title"),
    ('**WHAT ACTUALLY COSTS SOMETHING, IN ORDER.**\n\n**FIRST -- `walk_preview` renders unlit and says nothing.**\n\n```\nwalk_preview.py:249  has_lux = (dest / "presentation" / "lux.applied.tscn").is_file()\n```\n\nFalse is not an answer, and this treats it as one. The file is absent when\nLux was renamed, yes -- but also when `lux_apply` failed, when the mode\ndropped it, when the export did not carry it, or when somebody ran the\npreview on an unlit package. All five render a preview that is lit\ndifferently from the level, and the file\'s own words on why that matters are\nalready written down four bullets above the relevant note in\n`WALKABLE_SITE.md`: *"a preview that is lit differently from the level is\nworse than no preview, because it gets believed."* One file. No speculation.\nThe filename is incidental to it.\n\n**SECOND -- `_preset_for` is a silent no-op on a wrong name, and the\ncheck is free.**\n\nIt maps `time_of_day` onto Lux preset DISPLAY names -- "Blue Hour", "Delco\nSummer Afternoon", "Gas Station Fluorescent" -- and its own comment records\nthat a wrong name makes `blend_to_preset` do nothing, proven on hardware in\nthe Lux visual pass. Unlike everything else in this item, that has already\ncost something.\n\nIt is also nearly closed already, because the artifact answers it. Level\nFactory asks for a preset; `lux.quality.json` reports the one applied:\n\n```\nrequested   _preset_for(model)         ->  "Blue Hour"\napplied     lux.quality.json["preset"] ->  "Blue Hour"     (lot_demo_001, 2026-08-17)\n```\n\nNothing compares those two strings. A comparison turns a silent no-op into a\nfinding, needs no new data, and would have been exercised by the re-export\nrecorded below.\n\n**THIRD -- the filename literals, and they are genuinely third.**\n\n```\n9  packages/exporting/export.py        2  packages/pipeline/planner.py\n4  adapters/lux/__init__.py            2  packages/preview/walk_preview.py\n4  packages/exporting/localize.py      2  packages/service/facade.py\n3  apps/cli/commands/__init__.py       1  packages/exporting/closure.py\n```\n\n27 matching lines, 8 modules, 4 packages, for `lux.applied.tscn`,\n`lux.quality.json` and `lux.validation.json`. (Includes comment mentions; a\ncode-only pass returns the same eight modules.) No two readers agree on the\nsubset that matters -- `closure.py`\'s `_METADATA_FILES` names the two JSONs,\n`export.py`\'s `_PRESENTATION_FILES` names the scene and one JSON,\n`planner.py`\'s `expected_outputs` names all three.\n\n**Worth tidying, and honest about what tidying buys.** A shared constant does\nnot decouple: a Lux rename still edits Level Factory, in one place rather\nthan eight. That is a real improvement to a failure that has not happened --\nthe name has been stable across 0.15.x to 0.16.0 -- bought with an eight-file\nchange across four packages. Do it when something else already has those\nfiles open. Not as a project.\n\n', '**WHAT ACTUALLY COSTS SOMETHING.**\n\n**THE ONE WITH MEASURED HARM -- `_preset_for` is a silent no-op, and the\ncheck that closes it is free.**\n\nIt maps `time_of_day` onto Lux preset DISPLAY names -- "Blue Hour", "Delco\nSummer Afternoon", "Gas Station Fluorescent" -- and its own comment records\nthat a wrong name makes `blend_to_preset` do nothing, proven on hardware in\nthe Lux visual pass. Nothing else in this item has already cost something.\n\nIt is also nearly closed, because the artifact answers it. Level Factory asks\nfor a preset; Lux reports the one it applied:\n\n```\nrequested   _preset_for(model)          ->  "Blue Hour"\napplied     lux.quality.json["preset"]  ->  "Blue Hour"     (lot_demo_001, 2026-08-17)\n```\n\nNothing compares those two strings. A comparison needs no new data, turns a\nsilent no-op into a finding, and would have been exercised by every lit\nexport this pipeline has produced.\n\n**AND THE FILENAME LITERALS -- third, tidiness, with one real consequence.**\n\n```\n9  packages/exporting/export.py        2  packages/pipeline/planner.py\n4  adapters/lux/__init__.py            2  packages/preview/walk_preview.py\n4  packages/exporting/localize.py      2  packages/service/facade.py\n3  apps/cli/commands/__init__.py       1  packages/exporting/closure.py\n```\n\n27 matching lines, 8 modules, 4 packages, for `lux.applied.tscn`,\n`lux.quality.json` and `lux.validation.json`. (Includes comment mentions; a\ncode-only pass returns the same eight modules.) No two readers agree on the\nsubset that matters -- `closure.py`\'s `_METADATA_FILES` names the two JSONs,\n`export.py`\'s `_PRESENTATION_FILES` names the scene and one JSON,\n`planner.py`\'s `expected_outputs` names all three.\n\nA shared constant does not decouple: a Lux rename still edits Level Factory,\nin one place rather than eight, against a name stable across 0.15.x to\n0.16.0. THE ONE REAL CONSEQUENCE, stated correctly: a rename would send\n`walk_preview` to its fallback, and if that missed too the preview would\nreport `"lighting": "preview rig"` for a package that DOES carry Lux. Wrong,\nbut reported -- it lands in the return value and in `walk.source.json`\'s\nsibling fields, so it is findable rather than invisible. Worth tidying when\nsomething else already has those files open. Not as a project.\n\nWITHDRAWN: `walk_preview` DOES NOT SILENTLY RENDER UNLIT\n\nThe previous re-scope ranked it first, on the strength of a grep line\n(`walk_preview.py:249  has_lux = ...`) read without opening the function.\nRead (18,781 B, sha256 3400109C...):\n\n```python\n308:  has_lux = (dest / "presentation" / "lux.applied.tscn").is_file()\n309:  if not has_lux:\n311:      has_lux = "addons/lux" in (dest / level).read_text(encoding="utf-8")\n314:  if has_lux:      # instance the level as-is; Lux owns the lighting\n325:  else:            # build a preview RIG -- DirectionalLight3D, shadows, bias\n376:  lighting = "lux (content-owned)" if has_lux else "preview rig"\n393:  return {..., "lighting": lighting, ...}\n```\n\nTwo-way detection with a documented fallback; no unlit render, a substituted\nrig; and the choice is REPORTED in the return value. That is the opposite of\na check that finds nothing and proceeds. Its own comment records this being\nfixed once already, for the failure it was just accused of: `localize_export`\nstrips `addons/lux` by contract, so an earlier version found nothing, added\nthe dev rig ON TOP of Lux\'s WorldEnvironment and washed out the applied look.\nIt now asks what `write_entry_scene` keys on, so the two cannot disagree.\n\nThe 152-fixture-lights-against-`OmniLight3D 0` incident is not this line\neither. That is `walk_fixtures.gd` and the walk project not inheriting\n`lux.applied.tscn` -- a different mechanism in a different place, attached\nhere by mistake.\n\nTHE LINE NUMBER HAD MOVED, 249 to 308, WHICH WAS THE TELL. A note citing a\nline that no longer says what the note says is a note about a file that has\nchanged. This is the third mechanism in this item\'s neighbourhood published\nahead of the read, and the second inside a section arguing for reading first\n-- so it is recorded here rather than quietly corrected, on the same rule\nitem 49 adopted: a mechanism claim cites a verified read or it does not go\nin.\n\n', "ranked block"),
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
                  f"time(s), expected 1 -- has patch_roadmap_53_rescope.py run?")
            return 1
    if done == len(EDITS):
        print(f"  already applied  {ROADMAP}")
        return 0
    if done:
        print(f"REFUSING: {done} of {len(EDITS)} edits present -- part-patched")
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
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    md = (root / ROADMAP).read_bytes().decode("utf-8").replace(_CRLF, "\n")
    m = "**53. One Lux check is a silent no-op"
    check("item 53 has the corrected title", m in md)
    if m not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    prose = md.split("<!-- END GENERATED -->", 1)[-1]
    check("...and 'Two Lux checks' is gone from the prose",
          "Two Lux checks find nothing" not in prose)

    i = md.index(m)
    s = " ".join(md[:i].rstrip().splitlines()[-1].split())
    body = md[i:md.index("### Not to be worked on", i)]
    flat = " ".join(body.split())

    check("the STATUS says CORRECTED and what was withdrawn",
          s.startswith("*STATUS: OPEN 2026-08-17 -- CORRECTED")
          and "IT IS NOT ONE" in s)
    check("...quoting the return value that proves it reports",
          'lighting: "lux (content-owned)"' in s and '"preview rig"' in s)
    check("...citing the file it was read from",
          "walk_preview.py:308-314,376" in s and "sha256 3400109C" in s)
    check("...and that ONE ranked defect remains",
          "That leaves ONE ranked defect" in s and "_preset_for" in s)

    check("_preset_for is the ranked one, on measured harm",
          "THE ONE WITH MEASURED HARM" in body
          and "proven on hardware" in flat
          and "Nothing else in this item has already cost something" in flat)
    check("...with the free comparison spelled out",
          'lux.quality.json["preset"]' in body
          and "Nothing compares those two strings" in flat)

    check("the literals keep third place and the honest limit",
          "third, tidiness, with one real consequence" in flat
          and "does not decouple" in flat)
    check("...with the consequence stated CORRECTLY",
          '"lighting": "preview rig"' in body
          and "for a package that DOES carry Lux" in body
          and "Wrong,\nbut reported" in body)

    check("the withdrawal is recorded, not silently dropped",
          "WITHDRAWN: `walk_preview` DOES NOT SILENTLY RENDER UNLIT" in body)
    check("...quoting the code that refutes it",
          "build a preview RIG" in body
          and '"lighting": lighting' in body)
    check("...naming what the 152-vs-0 incident actually belongs to",
          "`walk_fixtures.gd`" in body
          and "attached\nhere by mistake" in body)
    check("...and the tell that was missed",
          "THE LINE NUMBER HAD MOVED, 249 to 308" in body
          and "a note about a file that has\nchanged" in body)
    check("...held to item 49's rule rather than excused",
          "cites a verified read or it does not go\nin" in body)

    check("the sections below were not disturbed",
          "WHERE THE CONSTANT WOULD GO, MEASURED" in body
          and 'CHASED AND CLOSED: "A VARIED LOT IS CURRENTLY UNLIT"' in body
          and '"fixture_lights": 136' in body
          and "THE INTERFACE QUESTION: DECIDED, LEAVE IT" in body)

    nums = [int(x) for x in re.findall(r"^\*\*(\d+)\. ", md, re.M)]
    check("the numbering is untouched", nums[-3:] == [51, 52, 53])
    check("item 53 introduces no item-shaped headings of its own",
          not re.findall(r"^\*\*(\d+)\. ", body[40:], re.M))
    check("every fenced block in 53 is closed", body.count("```") % 2 == 0)
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  one defect, honestly ranked, and the wrong one kept where it can be read"
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
        print("    python patches\\patch_roadmap_53_correct.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print()
        print("  patch_roadmap_53_rescope.py --selftest will now FAIL, as")
        print("  patch_roadmap_53.py's already does. Each asserts a moment.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
