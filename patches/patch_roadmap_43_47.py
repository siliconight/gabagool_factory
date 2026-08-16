r"""roadmap 43 + 47 -- one closed, one narrowed, and a diagnosis corrected.

    python patches\patch_roadmap_43_47.py --check
    python patches\patch_roadmap_43_47.py
    python patches\patch_roadmap_43_47.py --selftest
    python patches\patch_roadmap_43_47.py --revert

Run from the FACTORY ROOT. Then regenerate the derived table:

    python tools\roadmap_status.py --write

ITEM 43 CLOSES, AND ITS BODY WAS WRONG

The item says, in its own words: "`run --target presentation` plans no art
stages ... No `lux_apply`, no `dispatch_handoff`, no presentation compose."

That is not what was happening. The art stages planned and RAN. The run
printed them:

    bank_block_001.pixelcoat_build       succeeded
    bank_block_001.zoo_kit_build         succeeded
    bank_block_001.patina_dressing       succeeded
    bank_block_001.zoo_dressing_build    succeeded
    bank_block_001.presentation_compose  failed        <-- here
    bank_block_001.lux_fixture_gate      succeeded

One stage failed and three never ran behind it. All nine test failures are
that, and the item's list of nine symptoms is a list of downstream absences
mistaken for nine facts.

So the STATUS line closes it, and a correction block goes into the body
above the wrong paragraph rather than deleting it. The wrong diagnosis is
part of the record: it was written from the test names without opening the
run, and it read as nine independent findings for a day.

ITEM 47 NARROWS

Stages 1, 2 and 3a shipped and are measured on real data. Stage 3b -- a
mission actually RUN with `--art --unlit` through Blender and Godot -- is
not, and the item should say which half is which rather than closing on the
half that is done.

The item's own prediction was right and is worth leaving in place: "the seam
is already half-cut in three places." It was. `_PRESENTATION_FILES` is
exactly what `MODE_ART_UNLIT` drops. What the item did not predict is that
the seam had a hole behind it -- the assembled themed site reached no
package at all, so cutting Lux out left nothing to open.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r4347"

OLD_43 = (
    "*STATUS: OPEN 2026-08-14 -- found by `pytest level_factory/tests`, "
    "which had been aborting in collection since an unknown date; nine tests "
    "across tests/service and tests/integration fail and all nine trace to "
    "this*"
)
NEW_43 = (
    "*STATUS: CLOSED 2026-08-15 -- one failed stage, not nine failures, and "
    "not the cause written below. `presentation_compose` failed on a missing "
    "`*_dressing.glb`: the test-fixture Zoo stub's `--dress` branch wrote its "
    "index and no geometry, while its own `--fixtures` branch twenty lines "
    "above had always written both. NOT a 0.32.0 regression -- the guard "
    "appears twice in `adapters/presentation/__init__.py.pre_032` and twice "
    "in the current file, unchanged, predating 0.32.0 by ~9 days. Fixed in "
    "level_factory 0.33.0; tests/service + tests/integration 28 passed, 0 "
    "failed*"
)

OLD_47 = (
    "*STATUS: OPEN 2026-08-14 -- raised, not worked. The seam is already "
    "half-cut in three places: `_PRESENTATION_FILES` names Lux's two outputs "
    "by hand, `pure-shell` drops them, and `lux_strategy` is already a "
    "choice. What is missing is a third strategy value and a split of "
    "LAYER_ART*"
)
NEW_47 = (
    "*STATUS: NARROWED 2026-08-15 -- stages 1-3a shipped and measured; 3b "
    "remains. `LAYER_LIGHT` (0.35.0) splits Lux's apply pass out of the art "
    "layer, keeping `zoo_fixtures_build` and `lux_fixture_gate` in it; "
    "`MODE_ART_UNLIT` (0.36.0) subtracts Lux's result at EXPORT time so one "
    "build ships two archives; 0.37.0 ships `themed_site_assemble`'s "
    "site.tscn, which reached no package at all and without which an unlit "
    "one opened to nothing. Measured on lot_demo_001: unlit entry 571 B "
    "instancing NOTHING -> 688 B instancing `res://site.tscn`; 33 Lux files "
    "dropped and nothing else; shared interior folder. REMAINS: 3b, a "
    "mission RUN with `--art --unlit` through Blender and Godot -- factory "
    "1.24.0 certifies the set without it*"
)

CORRECTION_43_ANCHOR = (
    "**43. A whole CLI spelling stopped working and nothing noticed.**"
)
CORRECTION_43 = (
    "**43. A whole CLI spelling stopped working and nothing noticed.**\n"
    "\n"
    "> **CORRECTED 2026-08-15, and the paragraph below is kept because being\n"
    "> wrong this way is the finding.** The art stages planned and ran. The\n"
    "> run printed `pixelcoat_build succeeded`, `zoo_kit_build succeeded`,\n"
    "> `patina_dressing succeeded`, `zoo_dressing_build succeeded`, then\n"
    "> `presentation_compose failed` -- and `themed_site_assemble`,\n"
    "> `lux_apply` and `dispatch_handoff` never ran behind it. The nine\n"
    "> symptoms listed below are ONE failure and eight downstream absences.\n"
    ">\n"
    "> The list read as nine independent facts because it was assembled from\n"
    "> test names without opening the run. `diagnostics\n"
    "> <mission>.presentation_compose` named the cause in one command:\n"
    "> `input_validation_error -- no '*_dressing.glb' ... the job that bakes\n"
    "> it reported success without publishing one`.\n"
    ">\n"
    "> The test could not have told anyone either: it asserted `stage in\n"
    "> r.stdout`, and the line `bank_block_001.presentation_compose  failed`\n"
    "> CONTAINS `presentation_compose`. Six of its eight stage checks passed\n"
    "> on the run that broke.\n"
)

ADDENDUM_47_ANCHOR = (
    "**47. A recipient with their own lighting has to take ours or take "
    "graybox.**"
)
ADDENDUM_47 = (
    "**47. A recipient with their own lighting has to take ours or take "
    "graybox.**\n"
    "\n"
    "> **SHIPPED 2026-08-15 (stages 1-3a).** `--art` still means art + light\n"
    "> and `--target presentation` still plans the full stack; `--unlit`\n"
    "> subtracts. Only Lux's APPLY pass moved -- `zoo_fixtures_build` bakes\n"
    "> the physical hardware and `lux_fixture_gate` machine-checks it, and\n"
    "> both stay in the art layer, so an unlit package ships validated\n"
    "> fixtures and their `LuxEmit` markers as a contract another lighting\n"
    "> system can read.\n"
    ">\n"
    "> **The prediction below was right and incomplete.** The seam WAS\n"
    "> half-cut where the item said. What it did not predict is that there\n"
    "> was a hole behind it: `themed_site_assemble` writes a 31,872 byte\n"
    "> `site.tscn` that reached NO package, and the lit export only worked\n"
    "> because Lux's output stood in for the assembly. Cutting Lux out left\n"
    "> 180 files, 28.6 MB of geometry, and an entry that instanced nothing --\n"
    "> which `export_closure_scan.json` reported as `ok: true,\n"
    "> resource_count: 6`, because closure walks FROM the entry and an entry\n"
    "> referencing nothing is trivially closed.\n"
)

EDITS: list[tuple[str, str]] = [
    (OLD_43, NEW_43),
    (OLD_47, NEW_47),
    (CORRECTION_43_ANCHOR, CORRECTION_43),
    (ADDENDUM_47_ANCHOR, ADDENDUM_47),
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(raw: bytes) -> str:
    """From the FILE. PIPELINE_ROADMAP.md is CRLF and `Path.read_text`
    normalises that away, which is how an earlier patch reported LF for it
    and refused to match a single anchor."""
    return "\r\n" if b"\r\n" in raw else "\n"


def _as(text: str, eol: str) -> str:
    return text if eol == "\n" else text.replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    eol = _eol(raw)
    out, done = raw.decode("utf-8"), 0
    print(f"  {ROADMAP} line endings: {'CRLF' if eol != chr(10) else 'LF'}")

    for old, new in EDITS:
        old_f, new_f = _as(old, eol), _as(new, eol)
        if new_f in out:
            done += 1
            continue
        if out.count(old_f) != 1:
            print(f"REFUSING: an anchor occurs {out.count(old_f)} time(s), "
                  f"expected 1:\n    {old.splitlines()[0][:72]}")
            return 1
        out = out.replace(old_f, new_f, 1)
    if done == len(EDITS):
        print(f"  already applied  {ROADMAP}")
        return 0

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
    print()
    print("  NOW REGENERATE THE TABLE -- it is DERIVED, and it is stale:")
    print("    python tools\\roadmap_status.py --write")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    raw = (root / ROADMAP).read_bytes()
    s = raw.decode("utf-8")
    flat = " ".join(s.split())

    check("the roadmap is still CRLF", b"\r\n" in raw)
    check("item 43 is CLOSED", "*STATUS: CLOSED 2026-08-15 -- one failed stage"
          in s.replace("\r", ""))
    check("item 47 is NARROWED",
          "*STATUS: NARROWED 2026-08-15 -- stages 1-3a shipped"
          in s.replace("\r", ""))
    check("43 says the cause below it is wrong",
          "not the cause written below" in flat)
    check("and the wrong paragraph is KEPT, not deleted",
          "run --target presentation` plans no art stages" in flat
          or "plans no art\nstages" in s.replace("\r", ""))
    check("47 names what remains",
          "REMAINS: 3b" in flat)
    check("and says the certified set does not include it",
          "certifies the set without it" in flat)

    # The vocabulary is fixed. A verb outside it is a status nobody can grep.
    VERBS = {"OPEN", "CLOSED", "RETRACTED", "NARROWED", "SUPERSEDED",
             "ANALYSIS"}
    used = set(re.findall(r"\*STATUS:\s+([A-Z]+)", s))
    check(f"every STATUS verb is in the vocabulary: {sorted(used)}",
          used <= VERBS)

    n = len(re.findall(r"\*STATUS:", s))
    print(f"       {n} STATUS lines in the roadmap")
    check("no item lost its status line", n >= 24)

    # The table is DERIVED. This does not regenerate it; it says so.
    print()
    print("  NOT DONE HERE: the derived table. Run")
    print("    python tools\\roadmap_status.py --write")
    print("    python tools\\roadmap_status.py --check")
    print("  The table is generated OUTPUT -- reading it as source is how an")
    print("  earlier patch failed on text it had produced itself.")

    print()
    print("  43 closed, 47 narrowed"
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
        print("  the derived table is NOT reverted; re-run roadmap_status.py")
        return 0
    return _apply(root, check="--check" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
