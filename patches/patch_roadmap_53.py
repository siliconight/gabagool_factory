r"""Roadmap 47 CLOSED, and item 53 opened for what it did not finish.

    python patches\\patch_roadmap_53.py --check
    python patches\\patch_roadmap_53.py
    python patches\\patch_roadmap_53.py --selftest
    python tools\\roadmap_status.py --write

TWO EDITS

1. Item 47's STATUS: NARROWED -> CLOSED. It said the first cold package was
   "blocked by item 48" and "cannot be [proven] until 48 is". 48 and 49 are
   both CLOSED and the cold `unlit_probe_001` package now exports `ok: true`
   in both modes, so the sentence the item was waiting on came true and the
   roadmap did not say so.
2. Item 53 -- the decoupling item 47 exists to serve is real in the DAG and
   absent at the file level, plus the interface question nobody has decided.

WHY 53 IS SEPARATE RATHER THAN A REOPENED 47

47 asked for a package a recipient with their own lighting can use. That
exists and is measured. 53 asks whether Lux can be CHANGED without touching
level building, which is a different claim about the same seam, and its
evidence is a grep over eight modules rather than an export.

NOTE ON LINE ENDINGS: PIPELINE_ROADMAP.md is now LF. It was CRLF through
2026-08-16 and git normalised it ("CRLF will be replaced by LF the next time
Git touches it"). `_eol()` reads the FILE, so this patch handles either --
which is the whole reason that helper keys off the file and never off an
anchor.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r53"
ANCHOR = "\n### Not to be worked on\n"
OLD47 = "*STATUS: NARROWED 2026-08-15 -- stages 1 through 3b have all RUN; the layer split is proven and the first cold package is blocked by item 48. `LAYER_LIGHT` (0.35.0) splits Lux's apply pass out of the art layer, keeping `zoo_fixtures_build` and `lux_fixture_gate` in it; `MODE_ART_UNLIT` (0.36.0) subtracts Lux's result at EXPORT time so one build ships two archives; 0.37.0 ships `themed_site_assemble`'s site.tscn, which reached no package at all and without which an unlit one opened to nothing. Measured on lot_demo_001: unlit entry 571 B instancing NOTHING -> 688 B instancing `res://site.tscn`; 33 Lux files dropped and nothing else; shared interior folder. 3b RAN 2026-08-15 on `unlit_probe_001` through Blender and headless Godot and answered both of its questions: `lux_apply` never ran, `lux_fixture_gate` did, `dispatch_handoff <- themed_site_assemble`. Export was then blocked -- IDENTICALLY in `art-unlit` and `portable-godot`, which acquits `--unlit` -- by a functional regression that is item 48, not this item. The layer split is proven; a package built end-to-end from a cold run is not, and cannot be until 48 is*"
NEW47 = "*STATUS: CLOSED 2026-08-16 -- DELIVERED, and the cold package it was waiting on exists. All three shapes landed: `LAYER_LIGHT` (0.35.0) is a real fourth layer with `_LAYER_REQUIRES = {LAYER_LIGHT: LAYER_ART}` so it cannot be asked for without art, and ONLY Lux's apply pass moved -- `zoo_fixtures_build` and `lux_fixture_gate` stayed in `LAYER_ART`, so an unlit package still ships validated light FIXTURES and drops only the render solution; `MODE_ART_UNLIT` (0.36.0) is the export mode; `--unlit` is the flag on `run`, `plan` and `batch run`. `dispatch_dep = lux_jid if LAYER_LIGHT in layers else themed_jid` rewires the graph around the hole rather than special-casing it. PROVEN COLD on `unlit_probe_001` through Blender 5.1.1 and headless Godot 4.7: `lux_apply` never ran, `lux_fixture_gate` did, `dispatch_handoff <- themed_site_assemble`, and after items 48 and 49 closed the export came back `ok: true`, `issues: []`, `unresolved_relative_count: 0` in BOTH `portable-godot` and `art-unlit`. The A/B is the answer to question 1 stated by an artifact: on a mission where Lux NEVER RAN the two packages are byte-identical -- 56 files, 7,158,515 bytes, zero files differing -- because there is nothing to subtract. FOUR QUESTIONS ANSWERED: absent, not ignorable (33 Lux files dropped on lot_demo_001 and nothing else); the light anchors DO ship, because the fixture bake and its gate stayed in the art layer; the entry scene is `site.tscn`, shipped by 0.37.0; and the fourth-layer / sub-flag / third-mode question was answered ALL THREE rather than one. WHAT IS NOT DONE, and is now item 53: the decoupling this item exists to serve is real in the DAG and absent at the FILE level -- Lux's output names are string literals in 8 modules -- and the CLI expresses the fourth layer by SUBTRACTION (`--art` means art AND light, `--unlit` removes it; there is no positive `--light`), which is an interface decision nobody has made*"
INSERT = '*STATUS: OPEN 2026-08-16 -- MEASURED. Item 47 separated Lux in the DAG and did not separate it at the file level: `lux.applied.tscn`, `lux.quality.json` and `lux.validation.json` are string literals in EIGHT modules across four packages, 27 matching lines. They do not fail alike -- the planner would fail loudly on a missing expected output while `walk_preview`\'s `has_lux` would read False and silently render unlit. `_preset_for` additionally hardcodes Lux\'s preset DISPLAY names, where a wrong name is a documented silent no-op. Also carries the undecided interface: the fourth layer is expressed by subtraction and there is no positive `--light`*\n\n**53. Lux is decoupled in the graph and coupled by filename in eight\nmodules.**\nItem 47 asked for a fourth layer so that Lux could change without touching\nlevel building. In the DAG it worked: `lux_apply` is simply not planned when\n`LAYER_LIGHT` is absent, and `dispatch_dep` rewires around the hole. The\nfixture bake and its gate stayed in `LAYER_ART`, so the level-design data is\non the level side of the seam and only the render solution is on Lux\'s.\n\n**What survives the seam is the filenames.** Measured 2026-08-16 over\n`level_factory\\`, excluding `.pre_*`, `__pycache__` and `tests\\`:\n\n```\n9  packages/exporting/export.py\n4  adapters/lux/__init__.py\n4  packages/exporting/localize.py\n3  apps/cli/commands/__init__.py\n2  packages/pipeline/planner.py\n2  packages/preview/walk_preview.py\n2  packages/service/facade.py\n1  packages/exporting/closure.py\n```\n\n27 matching lines, 8 modules, 4 packages. (That count includes comment\nmentions; a code-only pass over the same tree returns the same eight\nmodules.) The names are `lux.applied.tscn`, `lux.quality.json` and\n`lux.validation.json`, and no two readers even agree on which subset matters\n-- `closure.py`\'s `_METADATA_FILES` names the two JSONs, `export.py`\'s\n`_PRESENTATION_FILES` names the scene and one JSON, `planner.py`\'s\n`expected_outputs` names all three.\n\n**THEY DO NOT FAIL ALIKE, WHICH IS THE PART THAT MATTERS.** Rename a Lux\noutput tomorrow and:\n\n```\nplanner.py           expected_outputs misses -> the JOB fails, loudly\nwalk_preview.py:249  has_lux = (dest/"presentation"/"lux.applied.tscn").is_file()\n                     -> reads False, and the preview renders UNLIT in silence\n```\n\nA guard that fails loudly and a check that reads False are not the same\nevent, and the second is the one this file keeps finding.\n\n**AND THE PRESETS ARE COUPLED BY DISPLAY NAME.** `_preset_for` maps\n`time_of_day` onto Lux preset names as strings -- "Blue Hour", "Delco Summer\nAfternoon", "Gas Station Fluorescent" -- and its own comment records why that\nis dangerous: Lux registers presets under DISPLAY names, and a wrong name\nmakes `blend_to_preset` a silent no-op, proven on hardware in the Lux visual\npass. A rename in Lux\'s preset library does not break this. It stops it\nworking.\n\n**THE FIX IS ONE CONSTANT LUX OWNS AND EIGHT READERS IMPORT.** Where it lives\nis the decision: `adapters/lux/__init__.py` is Level Factory\'s boundary onto\nLux and already names all three, so it is the obvious home; the honest home\nis Lux itself, exported and consumed, which makes a Lux rename a Lux release\nrather than a Level Factory bug hunt. Both are defensible and they cost\ndifferently.\n\nTHE INTERFACE QUESTION, STILL UNDECIDED\n\n`--art` means art AND light. `--unlit` subtracts light. There is no positive\n`--light`. So the planner has a fourth layer and the CLI expresses it by\nnegation, with the coupled thing as the easy path and the decoupled one\nneeding a second flag.\n\nThe stated reason for the split was granularity -- that changing Lux should\nnot require touching level building. Under that reason the interface that\nsays so is `--art` = art, `--light` = light (implying art), and `--unlit`\ndisappears because it has nothing left to subtract. That is a breaking CLI\nchange and every existing brief, script and doc that says `--art` today means\nart+light, including `tools/run_3b_unlit.ps1`.\n\nNOT A DEFECT, AND DELIBERATELY NOT FILED AS ONE. Nothing is broken. This is a\ndecision that gets more expensive the longer anything builds on the current\nspelling, which is the only reason it is written down rather than left in a\nconversation.\n\n'
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
    out, already = b, 0

    o, n = _as(OLD47, eol), _as(NEW47, eol)
    if n in out:
        already += 1
    elif out.count(o) == 1:
        out = out.replace(o, n, 1)
    else:
        print(f"REFUSING: item 47's NARROWED status occurs {out.count(o)} "
              f"time(s), expected 1")
        return 1

    a = _as(ANCHOR, eol)
    if _as("**53. Lux is decoupled in the graph", eol) in out:
        already += 1
    elif out.count(a) == 1:
        out = out.replace(
            a, _as("\n" + INSERT + "### Not to be worked on\n", eol), 1)
    else:
        print(f"REFUSING: the closing heading occurs {out.count(a)} time(s)")
        return 1

    if already == 2:
        print(f"  already applied  {ROADMAP}")
        return 0
    if already:
        print("REFUSING: one of two edits is already present -- part-patched")
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

    # -- 47 ----------------------------------------------------------------
    m47 = "**47. A recipient with their own lighting"
    check("item 47 is there", m47 in md)
    if m47 not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    s47 = " ".join(md[:md.index(m47)].rstrip().splitlines()[-1].split())
    check("item 47 is CLOSED", s47.startswith("*STATUS: CLOSED 2026-08-16"))
    check("...and the 'blocked by item 48' claim is gone",
          "blocked by item 48" not in s47
          and "cannot be until 48 is" not in s47)
    check("...naming all three shapes that landed",
          "LAYER_LIGHT" in s47 and "MODE_ART_UNLIT" in s47
          and "`--unlit` is the flag" in s47)
    check("...and that only the APPLY pass moved",
          "ONLY Lux's apply pass moved" in s47
          and "still ships validated light FIXTURES" in s47)
    check("...with the cold-run proof in both modes",
          "PROVEN COLD" in s47
          and "BOTH `portable-godot` and `art-unlit`" in s47)
    check("...and the A/B that answers question 1 by artifact",
          "byte-identical" in s47 and "7,158,515 bytes" in s47
          and "nothing to subtract" in s47)
    check("...and all four questions marked answered",
          "FOUR QUESTIONS ANSWERED" in s47 and "33 Lux files dropped" in s47
          and "ALL THREE rather than one" in s47)
    check("...and hands the unfinished half to 53",
          "is now item 53" in s47)

    # -- 53 ----------------------------------------------------------------
    m53 = "**53. Lux is decoupled in the graph"
    check("item 53 is present", m53 in md)
    if m53 not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    i53 = md.index(m53)
    s53 = " ".join(md[:i53].rstrip().splitlines()[-1].split())
    check("53 carries a STATUS line",
          s53.startswith("*STATUS: OPEN 2026-08-16"))
    body = md[i53:md.index("### Not to be worked on", i53)]
    flat = " ".join(body.split())

    check("53 credits the half that DID work",
          "In the DAG it worked" in flat
          and "`dispatch_dep` rewires around the hole" in flat)
    check("53 gives the per-module counts, not just a total",
          "9  packages/exporting/export.py" in body
          and "1  packages/exporting/closure.py" in body)
    check("...and the total, with what the count includes",
          "27 matching lines, 8 modules, 4 packages" in body
          and "includes comment mentions" in flat)
    check("...and that the readers disagree on the subset",
          "_METADATA_FILES" in body and "_PRESENTATION_FILES" in body
          and "expected_outputs" in body)
    check("the asymmetry is the headline, not the count",
          "THEY DO NOT FAIL ALIKE" in body
          and "renders UNLIT in silence" in flat)
    check("...quoting the line that would go quiet",
          'has_lux = (dest/"presentation"/"lux.applied.tscn").is_file()'
          in body)
    check("the preset coupling is there with its own evidence",
          "_preset_for" in body and "Blue Hour" in body
          and "silent no-op, proven on hardware" in flat)
    check("...and says a rename would not break it, it would stop it working",
          "It stops it working." in flat)
    # CASE. Written as `"one constant Lux owns" in flat.lower()` -- a needle
    # with a capital L searched inside a lowercased haystack, which can never
    # match. Both halves now match the file as written.
    check("the fix names the decision, not just the shape",
          "THE FIX IS ONE CONSTANT LUX OWNS AND EIGHT READERS IMPORT." in flat
          and "the honest home is Lux itself" in flat)
    check("the interface question is carried with its cost",
          "There is no positive `--light`" in flat
          and "breaking CLI change" in flat
          and "tools/run_3b_unlit.ps1" in body)
    check("...and is not filed as a defect",
          "NOT A DEFECT, AND DELIBERATELY NOT FILED AS ONE" in body
          and "Nothing is broken." in flat)

    nums = [int(x) for x in re.findall(r"^\*\*(\d+)\. ", md, re.M)]
    check("the numbering is contiguous through 53", nums[-3:] == [51, 52, 53])
    check("every fenced block in 53 is closed", body.count("```") % 2 == 0)
    check("53 ends with a blank line", body.endswith("\n\n"))
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  47 closed on the package it was waiting for; 53 has what it did not do"
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
        print("    python patches\\patch_roadmap_53.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
