r"""The varied lot IS lit -- measured, and the last step named.

    python patches\\patch_lux_varied_lot_measured.py --check
    python patches\\patch_lux_varied_lot_measured.py
    python patches\\patch_lux_varied_lot_measured.py --selftest
    python patches\\patch_lux_varied_lot_measured.py --revert

Run from the FACTORY ROOT. TWO FILES, TWO REPOS -- commit separately.
Requires patch_lux_varied_lot_stale.py to have run.

WHAT CHANGED SINCE THAT PATCH

It said the render-time question was "unmeasured". That understated it. The
re-export of `lot_demo_001` (2026-08-17, cached workspace, both modes) shows
`lux_apply` DID run on the five-building assembly:

    presentation/lux.applied.tscn   141,265 B
    fixture_lights                  136, from 136 markers
    preset                          "Blue Hour"   (applied: true)

So `WALKABLE_SITE.md:124-126` is not merely superseded by a code branch, it is
contradicted by an artifact. What is left is ONE step, and it is manual: a
spawn count is not a render count, and Lux says so itself -- `"note":
"previews need a render context"`.

BOTH FILES ARE CORRECTED, because both currently overstate the uncertainty.

WHY THE CACHED-NUMBER CAVEAT IS IN THERE

`lux.quality.json` is stamped 2026-08-15 and copied through; only
`lux.applied.tscn` is stamped today, because `localize` rewrites its `res://`
paths at export. 136 is correct for unchanged inputs and is not a fresh
measurement, and an item that did not say so would be claiming a number it
did not take.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

WALK = "level_factory/docs/WALKABLE_SITE.md"
ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_luxmeas"
OLD_R = 'WHAT THE READING DOES NOT SETTLE\n\nThe assembly INSTANCES the composed buildings. Whether a LuxRoot over the\nassembly reaches inside instanced sub-scenes at render time is not a question\nany amount of reading answers, and this pipeline has a recorded instance of\nlight not travelling: `WALKABLE_SITE.md:115-120` reports `lux.quality.json`\nat 152 fixture lights while the preview ran `OmniLight3D 0`, with the note\n*"a preview that is lit differently from the level is worse than no preview,\nbecause it gets believed."* Different mechanism, same hazard.\n\nIt is answerable by the thing already on the list -- re-export `lot_demo_001`\nunder 0.39.0/0.40.0 and open it. Five buildings is exactly the shape item\n49\'s fix leaves untouched, and nothing has re-measured it since.\n\n'
NEW_R = 'MEASURED, AND ONLY HALF ANSWERED\n\nRe-exported 2026-08-17 from the cached `lot-demo-ws`, both modes, no Blender\nor Godot needed. All three predictions held. `lot/` holds FIVE subdirectories\n-- item 49\'s fix correctly declined to touch the varied shape, which is the\ncondition `_assembly_building_dir` was written to fail. `resource_manifest.json`\nis gone (0.40.0). Closure `ok: true`, 0 missing, 0 misrooted, 0 unresolved\nrelative, in `portable-godot`, `art-unlit` and `pure-shell` alike:\n\n```\nLF_lot_demo_001.portable-godot   resource_count 36   lot/ 5\nLF_lot_demo_001.art-unlit        resource_count  7   lot/ 5\nLF_lot_demo_001.pure-shell       resource_count  2   lot/ 0\n```\n\nThe 29 between the first two is the localized Lux runtime -- `resource_count`\ncounts only `.tscn/.tres/.gd/.gdshader`, so it is the scripted part of the\n"33 Lux files dropped and nothing else" measured for 0.36.0. The lit varied\npackage ships Lux\'s runtime; the unlit one does not.\n\n**AND THE VARIED LOT IS LIT.** The claim above is not merely superseded by a\ncode branch, it is contradicted by the artifact:\n\n```\npresentation/lux.applied.tscn   141,265 B\npresentation/lux.quality.json   {"applied": true,\n                                 "fixture_lights": 136,\n                                 "fixture_msg": "Spawned 136 fixture light(s)\n                                                 from 136 marker(s)",\n                                 "preset": "Blue Hour"}\n```\n\n`lux_apply` ran on the five-building assembly, spawned 136 lights from 136\nmarkers and applied the preset. Incidentally that exercises this item\'s own\n`_preset_for` coupling and it HELD: the brief says `time_of_day: night`,\n`_preset_for` returns `"Blue Hour"`, Lux reports `"Blue Hour"`. Fragile by\nconstruction, not broken today.\n\nWHAT IS STILL NOT ANSWERED, AND IT IS NOW ONE STEP\n\nLux\'s own output says it: `"note": "previews need a render context"`. 136 is\nwhat was SPAWNED in a headless run. It is not a count of what RENDERS, and\nthose are the two numbers `WALKABLE_SITE.md:115-120` already recorded\ndisagreeing -- `lux.quality.json` at 152 fixture lights while the preview ran\n`OmniLight3D 0`, with the note *"a preview that is lit differently from the\nlevel is worse than no preview, because it gets believed."*\n\nSo `lux_apply` demonstrably reaches the assembly\'s markers. Whether those\nlights survive to a frame needs the `portable-godot` folder opened in a clean\nGodot project WITH a render context, and nothing substitutes for that -- not\nanother export, not a bigger scan. It is the one remaining step and it is\nmanual.\n\nONE CAVEAT ON THE NUMBER. `lux.quality.json` is stamped 2026-08-15 and copied\nthrough unchanged; `lux.applied.tscn` is stamped today because `localize`\nrewrote its `res://` paths on export. 136 is therefore a CACHED figure from\nthe last real `lux_apply`, correct for unchanged inputs and not a fresh\nmeasurement.\n\n'
OLD_W = '  WHAT IS STILL UNMEASURED, and it is not this: the assembly INSTANCES the\n  composed buildings, and whether a LuxRoot over the assembly reaches inside\n  instanced sub-scenes at render time is a question no reading settles. The\n  bullet four above this one is the reason to ask it -- `lux.quality.json`\n  reported 152 fixture lights while the preview ran `OmniLight3D 0`. Answering\n  it needs a varied lot exported and opened, which nothing has done since\n  level_factory 0.39.0.\n'
NEW_W = '  WHAT IS STILL UNMEASURED, and it is now one step rather than a question:\n  the assembly INSTANCES the composed buildings, and whether a LuxRoot over\n  the assembly survives to a frame inside them is a render-time question.\n  Measured 2026-08-17 on `lot_demo_001`, five buildings, exported both modes:\n  `presentation/lux.applied.tscn` ships at 141,265 B and\n  `presentation/lux.quality.json` reads `{"applied": true, "fixture_lights":\n  136, "fixture_msg": "Spawned 136 fixture light(s) from 136 marker(s)",\n  "preset": "Blue Hour"}`. So `lux_apply` reaches the assembly\'s markers on a\n  varied lot -- which is what the bullet above denied. What it does NOT\n  establish is rendering: Lux\'s own note is *"previews need a render\n  context"*, and a spawn count is not a render count. That is precisely the\n  pair four bullets up -- 152 reported against `OmniLight3D 0` running.\n  Answering it needs the package opened in a clean Godot project with a\n  render context; no export answers it.\n'
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
              f"expected 1 -- has patch_lux_varied_lot_stale.py run?")
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
        print("REFUSING: run from the factory root: " + ", ".join(missing))
        return 1
    rc = _one(root / WALK, OLD_W, NEW_W, check=check, label=WALK)
    if rc:
        return rc
    return _one(root / ROADMAP, OLD_R, NEW_R, check=check, label=ROADMAP)


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    md = (root / ROADMAP).read_bytes().decode("utf-8").replace(_CRLF, "\n")
    m53 = "**53. Lux is decoupled in the graph"
    check("item 53 is there", m53 in md)
    if m53 not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    body = md[md.index(m53):md.index("### Not to be worked on", md.index(m53))]
    flat = " ".join(body.split())

    check("the roadmap no longer calls it merely unmeasured",
          "WHAT THE READING DOES NOT SETTLE" not in body
          and "MEASURED, AND ONLY HALF ANSWERED" in body)
    check("...with the three predictions and the one that mattered",
          "holds FIVE subdirectories" in flat
          and "declined to touch the varied shape" in flat)
    check("...and the per-mode counts",
          "resource_count 36" in body and "resource_count  7" in body
          and "resource_count  2" in body)
    check("...explaining the 29-file gap rather than just showing it",
          "the localized Lux runtime" in flat
          and "33 Lux files dropped" in flat)
    check("the artifact that contradicts the doc is quoted",
          "141,265 B" in body and '"fixture_lights": 136' in body
          and "from 136 marker(s)" in body)
    check("...and the preset coupling is recorded as EXERCISED",
          "`_preset_for` coupling and it HELD" in flat
          and "Fragile by construction, not broken today" in flat)
    check("the remaining step is named as one step, and manual",
          "IT IS NOW ONE STEP" in body
          and "WITH a render context" in body
          and "It is the one remaining step and it is\nmanual." in body)
    check("...resting on Lux's own words, not ours",
          '"note": "previews need a render context"' in body
          and "It is not a count of what RENDERS" in body)
    check("...and the prior disagreement it echoes",
          "152 fixture lights" in flat and "OmniLight3D 0" in flat)
    check("the cached-number caveat is stated",
          "ONE CAVEAT ON THE NUMBER" in body
          and "a CACHED figure" in flat
          and "not a fresh\nmeasurement" in body)

    w = (root / WALK).read_text(encoding="utf-8").replace(_CRLF, "\n")
    wf = " ".join(w.split())
    check("the doc bullet is still present and still marked superseded",
          "**A varied lot is currently UNLIT** regardless" in w
          and "**SUPERSEDED 2026-08-17" in w)
    check("...and its uncertainty paragraph now carries the measurement",
          "it is now one step rather than a question" in wf
          and "141,265 B" in w and '"fixture_lights":' in w)
    check("...saying plainly that the bullet above it was denied by this",
          "which is what the bullet above denied" in wf)
    check("...and that no export answers the rest",
          "no export answers it" in wf)

    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  half answered, and the half that is left is one manual step"
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
        print("    python patches\\patch_lux_varied_lot_measured.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print()
        print("  TWO REPOS -- WALKABLE_SITE.md from level_factory\\,")
        print("  PIPELINE_ROADMAP.md from the factory root.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
