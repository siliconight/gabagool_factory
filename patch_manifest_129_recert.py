#!/usr/bin/env python3
"""factory 1.29.0 -- re-certify on the first LIT package a Godot process loaded.

The previous note in this manifest set the condition itself: "No Godot process
has ever executed it, so the pin stays at 0.40.0 until a lit run certifies it."
That run happened on 2026-08-18 and every artifact it produced is green, so the
condition is met and the pin moves. Leaving that sentence in place would make
the manifest false in the other direction.

WHAT MOVES
    factory_version   1.28.0 -> 1.29.0
    level_factory     0.40.0 -> 0.42.0   (tag v0.42.0)
    the other nine pins            unchanged, asserted by the selftest

WHAT THE NEW DESCRIPTION RECORDS, and it is written to be checkable rather
than reassuring: the fingerprint receipt fields that prove `lux_apply` ran
instead of cached, the driver's own stdout, both closure scans, the
portability report, and the A/B probe. Then, at equal length, what was NOT
run -- and specifically that `scene_instantiated: true` means the scene
loaded, NOT that 136 lights illuminate anything. A headless process cannot
answer that and this set does not claim it does.

The 2026-08-16 text is demoted to PRIOR CERTIFICATION rather than deleted,
including the corrections applied to it earlier today.

Usage:
    pwsh> python patch_manifest_129_recert.py --check
    pwsh> python patch_manifest_129_recert.py
    pwsh> python patch_manifest_129_recert.py --selftest
    pwsh> python patch_manifest_129_recert.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "factory.manifest.json"
TAG = "pre_129recert"

E1_OLD = '"factory_version": "1.28.0",'
E1_NEW = '"factory_version": "1.29.0",'

E2_OLD = ('"level_factory": {\n      "version": "0.40.0",\n'
          '      "tag": "v0.40.0",')
E2_NEW = ('"level_factory": {\n      "version": "0.42.0",\n'
          '      "tag": "v0.42.0",')

E3_OLD = ('"description": "The certified lockstep set: these tool versions were '
          'verified TOGETHER. Re-certified 2026-08-16, on the first package '
          'this pipeline has produced that opens. WHAT WAS RUN:')

E3_NEW = (
    '"description": "The certified lockstep set: these tool versions were '
    'verified TOGETHER. Re-certified 2026-08-18, on the first LIT package '
    'this pipeline has produced that a Godot process loaded. '

    'WHAT WAS RUN: lot_demo_001 in workspaces/lot-demo-ws, run --art '
    '--gameplay. Three candidates built, all distinct. Structural checks '
    'passed, 0 blockers open, 65 findings. `lux_apply` reports SUCCEEDED and '
    'not cache, which is itself the evidence for level_factory 0.42.0: its '
    'fingerprint receipt carries `adapter_version 0.5.0` and '
    '`driver_src_hash sha256:3daa2a9e...` -- the hash of the 0.41.0 driver -- '
    'beside `tool_version Lux 0.16.0` and Lux own `repository_commit '
    '333b5013...`, which are the two fields that had been standing in for a '
    'driver they cannot see. '

    'The driver said so on its own stdout: `[lux] Spawned 136 fixture '
    'light(s) from 136 marker(s)` and `[lux] requested Blue Hour applied Blue '
    'Hour`. That second string is read off `LuxRoot.get_current_preset()` and '
    'is not the argument echoed back, which is level_factory 0.41.0 proven on '
    'hardware. `lux.quality.json` carries `preset` and `preset_applied` both '
    'Blue Hour at 136 fixture lights; `lux.validation.json` is `issues: []`. '

    'EXPORTED IN BOTH MODES. portable-godot closure scan: `ok: true`, '
    '`issues: []`, `missing_resource_count: 0`, '
    '`unresolved_relative_count: 0`, `absolute_path_count: 0`, '
    '`external_reference_count: 0`, `misrooted_resource_count: 0`, '
    '`resource_count: 36`, `required_plugin_count: 0`, '
    '`required_autoload_count: 0`, entry `mission.tscn` instancing '
    '`presentation/lux.applied.tscn`, all five buildings rerooted, '
    '`unresolved: []`. art-unlit closure scan: `ok: true`, `issues: []`, '
    '`resource_count: 7`. '

    'AND A GODOT PROCESS OPENED THE LIT ONE. `portability-test` on '
    'portable-godot returns `status: PASS`, `engine_check: passed`, '
    '`scene_instantiated: true`, `parser_error_count: 0`, '
    '`shader_error_count: 0`, Godot 4.7, zero required plugins and zero '
    'required autoloads. `probe_unlit_ab` passes all nine of its checks: the '
    'unlit package drops Lux outputs and runtime (33 files), drops nothing '
    'else, adds nothing, still carries the art (180 files), and the manifests '
    'claim `art gameplay light` against `art gameplay`. Its own summary line: '
    'the two packages differ only in the render. '

    'WHAT WAS NOT RUN, and is therefore NOT covered by this set: the walk '
    'sweep (library_walk), the pack load check, deli_counter suite, and the '
    'real_tools suite. lot suite was run, but on its own clean tree rather '
    'than as part of this build -- 336 passed, 0 failed, Lot 0.44.0, git '
    '0028666. THE BUILD WAS NOT COLD: three deli_generate and three '
    'laser_tag_evaluate jobs report cache; every art, fixture, compose, '
    'assemble, lux and walktest job ran. '

    'AND THE ONE THING A HEADLESS PROCESS CANNOT ANSWER. '
    '`scene_instantiated: true` means the scene loaded and instantiated. It '
    'does NOT mean 136 lights illuminate anything. The driver own note still '
    'reads `previews need a render context`, and opening the package in a '
    'windowed Godot is still the only way to see the light. It has still not '
    'been done, and no number in this set should be read as if it had. '

    'ONE ARTEFACT NOTE: the two packages certified here are stamped `f1.28.0` '
    'in their archive names, because they were built before this bump. That '
    'is the same order the 0.40.0 entry below records for itself. '

    'PRIOR CERTIFICATION, 2026-08-16 -- the first package this pipeline '
    'produced that opens. WHAT WAS RUN:'
)

E4_OLD = (
    '0.41.0 IS TAGGED AND IS NOT IN THIS SET: it reads the applied Lux preset '
    'off LuxRoot rather than echoing the --preset argument back into '
    'lux.quality.json, adds preset_applied, and raises LUX_PRESET_NOT_APPLIED '
    'when the two disagree. No Godot process has ever executed it, so the pin '
    'stays at 0.40.0 until a lit run certifies it.'
)
E4_NEW = (
    '0.41.0 AND 0.42.0 ARE BOTH IN THIS SET as of 2026-08-18. 0.41.0 reads '
    'the applied Lux preset off LuxRoot rather than echoing the --preset '
    'argument back into lux.quality.json, adds preset_applied, and raises '
    'LUX_PRESET_NOT_APPLIED when the two disagree. 0.42.0 folds the staged '
    'Godot driver into the Lux stage fingerprint, and without it 0.41.0 would '
    'have cache-hit and never executed: `probe` reports LUX repository '
    'commit while both drivers live in level_factory assets, so editing '
    'either moved no component of the cache key. The note that stood here '
    'said no Godot process had ever executed 0.41.0 and that the pin would '
    'stay at 0.40.0 until a lit run certified it. That run happened on '
    '2026-08-18, is recorded in the description above, and every artifact it '
    'produced is green -- so the pin is 0.42.0.'
)

EDITS = [
    ("factory_version 1.28.0 -> 1.29.0", E1_OLD, E1_NEW),
    ("level_factory pin 0.40.0 -> 0.42.0", E2_OLD, E2_NEW),
    ("description: new certification, prior one demoted", E3_OLD, E3_NEW),
    ("level_factory note: 0.41.0 and 0.42.0 are in the set", E4_OLD, E4_NEW),
]

FORBIDDEN = ("\\", "\n", "\r", "\t")
UNCHANGED_PINS = {"deli_counter", "dispatch", "laser_tag", "lot", "lux",
                  "patina", "pipeline", "pixelcoat", "zoo"}


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


def _guard() -> None:
    """A raw quote, backslash or newline in the description turns the manifest
    into a parse error. E3 opens with `"description": "` on purpose, so it is
    checked from after that opening quote onward."""
    for label, _old, new in EDITS:
        body = new.split('": "', 1)[1] if new.startswith('"description"') else new
        if body.startswith('"level_factory"') or label.startswith("factory_version") \
                or label.startswith("level_factory pin"):
            continue                      # structural edits, quotes are theirs
        bad = [c for c in FORBIDDEN if c in body] + (['"'] if '"' in body else [])
        if bad:
            raise SystemExit(
                f"REFUSING: replacement for '{label}' contains {bad!r} raw "
                f"inside a JSON string literal.")


def _pins(doc: dict) -> dict:
    return {k: (v.get("version"), v.get("tag"))
            for k, v in doc.get("tools", {}).items()}


def _plan(text: str) -> str:
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times, expected 1.")
        text = text.replace(old, new, 1)
        print(f"  ok  {label}")
    return text


def _require() -> None:
    if not MANIFEST.is_file():
        sys.exit(f"REFUSING: not found: {MANIFEST}")
    t = MANIFEST.read_text(encoding="utf-8")
    if "CORRECTED 2026-08-18" not in t:
        sys.exit("REFUSING: patch_manifest_128_corrections.py has not been "
                 "applied. This patch demotes text that one edits, and "
                 "applying them out of order would demote the stale version.")


def cmd_check() -> int:
    _require(); _guard()
    print("   ", _stamp(MANIFEST))
    t = MANIFEST.read_text(encoding="utf-8")
    if "Re-certified 2026-08-18" in t:
        print("\nALREADY APPLIED.")
        return 0
    print()
    _plan(t)
    print("\nnine other pins left untouched; asserted by --selftest")
    return 0


def cmd_apply() -> int:
    _require(); _guard()
    src = MANIFEST.read_text(encoding="utf-8")
    if "Re-certified 2026-08-18" in src:
        print("ALREADY APPLIED; nothing to do.")
        return 0
    before = json.loads(src)
    out = _plan(src)
    after = json.loads(out)          # raises BEFORE anything is written

    moved = [k for k in _pins(after) if _pins(after)[k] != _pins(before)[k]]
    if moved != ["level_factory"]:
        raise SystemExit(f"REFUSING: pins moved that should not have: {moved}")

    (MANIFEST.parent / f"{MANIFEST.name}.{TAG}").write_bytes(MANIFEST.read_bytes())
    MANIFEST.write_text(out, encoding="utf-8", newline="")
    print("\nafter:")
    print("   ", _stamp(MANIFEST))
    print(f"\nsidecar .{TAG}; `--revert` restores it.")
    return 0


def cmd_revert() -> int:
    side = MANIFEST.parent / f"{MANIFEST.name}.{TAG}"
    if not side.is_file():
        print("nothing to revert.")
        return 0
    MANIFEST.write_bytes(side.read_bytes())
    side.unlink()
    print(f"  restored {MANIFEST.name}")
    return 0


CHECKS = [
    ("the stale not-executed sentence is gone",
     lambda t: "No Godot process has ever executed it" not in t),
    ("the new certification date leads",
     lambda t: "Re-certified 2026-08-18" in t),
    ("the prior certification is demoted, not deleted",
     lambda t: "PRIOR CERTIFICATION, 2026-08-16" in t
               and "PRIOR CERTIFICATION, 2026-08-14" in t),
    ("the cache-vs-ran evidence is named",
     lambda t: "driver_src_hash sha256:3daa2a9e" in t
               and "adapter_version 0.5.0" in t),
    ("both closure scans are recorded",
     lambda t: "resource_count: 36" in t and "resource_count: 7" in t),
    ("the engine check is recorded",
     lambda t: "scene_instantiated: true" in t and "engine_check: passed" in t),
    ("the render-context limit is stated, not glossed",
     lambda t: "does NOT mean 136 lights illuminate anything" in t),
    ("the not-cold build is admitted",
     lambda t: "THE BUILD WAS NOT COLD" in t),
    ("the f1.28.0 archive stamp is explained",
     lambda t: "stamped `f1.28.0`" in t),
]


def cmd_selftest() -> int:
    if not MANIFEST.is_file():
        sys.exit(f"SELFTEST: not found: {MANIFEST}")
    t = MANIFEST.read_text(encoding="utf-8")
    try:
        doc = json.loads(t)
    except json.JSONDecodeError as e:
        raise SystemExit(f"SELFTEST FAILED: manifest is not valid JSON: {e}")
    print("  ok  still valid JSON")

    bad = []
    for name, fn in CHECKS:
        ok = fn(t)
        print(("  ok  " if ok else "  FAIL ") + name)
        if not ok:
            bad.append(name)
    if bad:
        raise SystemExit("SELFTEST FAILED: " + "; ".join(bad))

    if doc["factory_version"] != "1.29.0":
        raise SystemExit(f"SELFTEST FAILED: factory_version is "
                         f"{doc['factory_version']}")
    print("  ok  factory_version 1.29.0")
    lf = doc["tools"]["level_factory"]
    if (lf["version"], lf["tag"]) != ("0.42.0", "v0.42.0"):
        raise SystemExit(f"SELFTEST FAILED: level_factory pin is {lf}")
    print("  ok  level_factory 0.42.0 / v0.42.0")

    side = MANIFEST.parent / f"{MANIFEST.name}.{TAG}"
    if side.is_file():
        pre = json.loads(side.read_text(encoding="utf-8"))
        drift = {k: (_pins(pre)[k], _pins(doc)[k]) for k in UNCHANGED_PINS
                 if _pins(pre)[k] != _pins(doc)[k]}
        if drift:
            raise SystemExit(f"SELFTEST FAILED: other pins moved: {drift}")
        print(f"  ok  all {len(UNCHANGED_PINS)} other pins byte-identical")
        pretext = side.read_text(encoding="utf-8")
        useless = [n for n, fn in CHECKS if fn(pretext)]
        if useless:
            raise SystemExit("SELFTEST FAILED: these hold on the PRE-IMAGE "
                             "too, so they test nothing: " + "; ".join(useless))
        print("  ok  every content check fails on the pre-image")
    else:
        print("  --  no sidecar; pre-image comparison skipped")

    print("\nSELFTEST PASSED")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return cmd_check()
    if a.revert:
        return cmd_revert()
    if a.selftest:
        return cmd_selftest()
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
