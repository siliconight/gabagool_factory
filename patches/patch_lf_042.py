#!/usr/bin/env python3
"""level_factory 0.42.0 -- the Lux stage never hashed the program it runs.

0.41.0 changed `assets/godot/run_lux_apply.gd`. A re-run would have CACHE-HIT
and never executed it, so the evidence run for 0.41.0 would have produced the
old `lux.quality.json` and reported success.

WHY, read out of `scheduler.py:414-437` rather than guessed. The cache key is
`BuildFingerprint.digest()` over twelve components. Walking them against this
change:

    adapter_id / adapter_version / schema_versions   unchanged (0.4.0)
    tool_version / repository_commit                 LUX's repo -- `probe`
                                                     reads installation
                                                     ["repository"], and the
                                                     driver lives in
                                                     level_factory
    normalized_arguments                             --scene/--preset/--out,
                                                     unchanged
    input_hashes                                     hash_json of
                                                     fingerprint_inputs, which
                                                     hashes the scene, the
                                                     lights json and the
                                                     scene's art payload --
                                                     and nothing else
    executable_versions / declared_environment /
    seed / upstream_artifact_hashes /
    output_contract_version                          unchanged

Not one of the twelve sees the driver. The `+dirty.<hash>` suffix on
`tool_version` exists for exactly this failure -- "an on-disk fix that has not
been committed keeps cache-hitting the pre-fix artifact" -- but it tracks the
LUX repository, and this driver is not in it.

THIS IS THE SAME FAULT `adapter_version = "0.4.0"` WAS CUT FOR, one level
further out. That one hashed the scene's bytes and not the art the scene
names. This one hashes the inputs and not the program that reads them.

It is specific to this adapter, and the reason is worth writing down: Lux is
the only tool whose driver LF ships. Laser Tag runs
`res://addons/laser_tag_tool/runners/run_map_eval.gd` out of its own
repository, so `repository_commit` already covers it. `lot` and `walktest`
fold `.gd` files into their own input scans. Only the Lux adapter copies a
GDScript out of `level_factory/assets/godot/` while reporting a different
repository's commit -- and it does it in BOTH modes, `lux_apply` and
`lux_fixture_gate`.

THE FIX: hash `driver_src` into `fingerprint_inputs`, before the fixture-gate
branch returns, so one statement covers both modes. `adapter_version` goes to
0.5.0, which invalidates every existing Lux cache entry exactly once -- which
is what makes 0.41.0's evidence run actually run.

Usage:
    pwsh> python patch_lf_042.py --check
    pwsh> python patch_lf_042.py
    pwsh> python patch_lf_042.py --selftest
    pwsh> python patch_lf_042.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LF = ROOT / "level_factory"
ADAPTER = LF / "adapters" / "lux" / "__init__.py"
VERSION = LF / "VERSION"
CHANGELOG = LF / "CHANGELOG.md"
TEST = LF / "tests" / "unit" / "test_lux_driver_in_fingerprint.py"

TAG = "pre_042"
NEW_VERSION = "0.42.0"
TOUCHED = [ADAPTER, VERSION, CHANGELOG]


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _eol(path: Path) -> str:
    return "\r\n" if b"\r\n" in path.read_bytes() else "\n"


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


A1_OLD = '    adapter_version = "0.4.0"\n'
A1_NEW = (
    '    # 0.5.0 folds the STAGED DRIVER into the fingerprint. Until it did,\n'
    '    # this stage hashed its inputs and not the program that reads them:\n'
    '    # `probe` reports LUX\'s repository commit, both drivers live in\n'
    '    # level_factory/assets/godot/, and so an edit to either one moved no\n'
    '    # component of the cache key. 0.41.0 rewrote run_lux_apply.gd and the\n'
    '    # very next run would have cache-hit the artifact the OLD driver\n'
    '    # produced -- and reported success. Bumping this constant is also\n'
    '    # what invalidates every existing Lux entry once, so 0.41.0 gets an\n'
    '    # execution to be measured on.\n'
    '    adapter_version = "0.5.0"\n'
)

A2_OLD = (
    '        fp: dict[str, object] = {\n'
    '            "preset": job_spec.get("preset"),\n'
    '            "quality_tier": job_spec.get("quality_tier", "standard"),\n'
    '            "overrides": job_spec.get("overrides", {}),\n'
    '            "preview_states": sorted(job_spec.get("preview_states", [])),\n'
    '        }\n'
)
A2_NEW = A2_OLD + (
    '        # THE DRIVER IS AN INPUT, and it is hashed HERE -- above the\n'
    '        # fixture-gate branch -- so that one statement covers both modes.\n'
    '        # `lux_apply` stages run_lux_apply.gd and `lux_fixture_gate`\n'
    '        # stages run_fixture_gate.gd, both under the same `driver_src`\n'
    '        # key, and neither was visible to the cache. This is the same\n'
    '        # shape as the fault adapter_version 0.4.0 was cut for, one level\n'
    '        # further out: that one hashed the scene and not the art the\n'
    '        # scene names.\n'
    '        driver = job_spec.get("driver_src")\n'
    '        if driver and Path(str(driver)).exists():\n'
    '            fp["driver_src_hash"] = hash_file(Path(str(driver)))\n'
)

EDITS = [
    ("hash the staged driver, both modes", A2_OLD, A2_NEW),
    ("adapter_version 0.4.0 -> 0.5.0", A1_OLD, A1_NEW),
]

CHANGELOG_ENTRY = """## [0.42.0] - the Lux stage never hashed the program it runs

0.41.0 rewrote `assets/godot/run_lux_apply.gd`. The next run would have
CACHE-HIT, never executed it, kept the old `lux.quality.json`, and reported
success. The evidence run for 0.41.0 would have produced no evidence.

WHY, from `scheduler.py:414-437` rather than from assumption. The cache key is
`BuildFingerprint.digest()` over twelve components, and this change moves none
of them:

    adapter_id / adapter_version / schema_versions   unchanged
    tool_version / repository_commit                 LUX's repository --
                                                     `probe` reads
                                                     installation["repository"]
    normalized_arguments                             --scene/--preset/--out
    input_hashes                                     the scene, the lights
                                                     json, the scene's art
                                                     payload. Not the driver.
    everything else                                  unchanged

`tool_version` even carries a `+dirty.<hash>` suffix for uncommitted tool
edits, added because "an on-disk fix that has not been committed keeps
cache-hitting the pre-fix artifact". It tracks the Lux repository. This driver
is not in it.

This is the fault `adapter_version = "0.4.0"` was cut for, one level further
out. That one hashed the scene's bytes and not the art the scene names. This
one hashes the inputs and not the program that reads them.

WHY ONLY THIS ADAPTER

Lux is the only tool whose driver Level Factory ships. Laser Tag runs
`res://addons/laser_tag_tool/runners/run_map_eval.gd` out of its own
repository, so `repository_commit` covers it. `lot` and `walktest` fold `.gd`
files into their own input scans. Only the Lux adapter copies a GDScript out
of `level_factory/assets/godot/` while reporting a different repository's
commit -- and it does so in BOTH modes, under the same `driver_src` key.

THE FIX

`driver_src` is hashed in `fingerprint_inputs` ABOVE the fixture-gate branch,
so one statement covers `lux_apply` and `lux_fixture_gate`. `adapter_version`
goes to 0.5.0, which invalidates every existing Lux cache entry exactly once
-- which is what gives 0.41.0 an execution to be measured on.

`tests/unit/test_lux_driver_in_fingerprint.py` is a BEHAVIOURAL test, not a
source-shape one: it calls `fingerprint_inputs`, edits the driver on disk, and
asserts the fingerprint moved -- in both modes, and asserts the rest of the
fingerprint did not move with it.

"""

TEST_SOURCE = '''"""Editing the staged Godot driver must change the Lux stage's fingerprint.

It did not. `probe` reports LUX's repository commit -- that is the repository
this adapter is configured with -- while both drivers live in
`level_factory/assets/godot/`, so an edit to either moved no component of the
cache key and the stage cache-hit the artifact the OLD driver produced. 0.41.0
rewrote `run_lux_apply.gd`; without this, its evidence run would have measured
0.40.0's output and called it a pass.

Unlike `test_lux_preset_readback.py` next door, this is BEHAVIOURAL: it calls
`fingerprint_inputs`, mutates the file, and compares. No Godot required,
because the fingerprint is computed before anything is executed -- which is
the whole reason the defect was invisible.

Run:  python -m pytest tests/unit/test_lux_driver_in_fingerprint.py
"""
import pytest

from adapters.lux import LuxAdapter


@pytest.fixture()
def driver(tmp_path):
    p = tmp_path / "run_lux_apply.gd"
    p.write_text("extends SceneTree\\n# version one\\n", encoding="utf-8")
    return p


@pytest.fixture()
def apply_spec(tmp_path, driver):
    scene = tmp_path / "site.tscn"
    scene.write_text("[gd_scene load_steps=1 format=3]\\n", encoding="utf-8")
    return {"preset": "Blue Hour", "composed_scene": str(scene),
            "driver_src": str(driver)}


@pytest.fixture()
def gate_spec(tmp_path, driver):
    fdir = tmp_path / "fixtures"
    fdir.mkdir()
    (fdir / "a_fixtures.glb").write_bytes(b"glTF")
    return {"mode": "fixture_gate", "fixtures_dir": str(fdir),
            "driver_src": str(driver)}


def _fp(spec):
    return LuxAdapter().fingerprint_inputs(spec, {})


def test_the_apply_driver_is_in_the_fingerprint(apply_spec):
    assert "driver_src_hash" in _fp(apply_spec)


def test_the_fixture_gate_driver_is_in_the_fingerprint(gate_spec):
    """The gate branch returns EARLY, so a driver hash added after the branch
    would cover apply and silently miss the gate."""
    assert "driver_src_hash" in _fp(gate_spec)


@pytest.mark.parametrize("which", ["apply", "gate"])
def test_editing_the_driver_moves_the_fingerprint(which, apply_spec, gate_spec,
                                                  driver):
    spec = apply_spec if which == "apply" else gate_spec
    before = _fp(spec)
    driver.write_text("extends SceneTree\\n# version TWO\\n", encoding="utf-8")
    after = _fp(spec)
    assert before != after
    assert before["driver_src_hash"] != after["driver_src_hash"]


@pytest.mark.parametrize("which", ["apply", "gate"])
def test_editing_the_driver_moves_NOTHING_ELSE(which, apply_spec, gate_spec,
                                               driver):
    """A fingerprint that changes wholesale on a driver edit would invalidate
    correctly and tell you nothing about why."""
    spec = apply_spec if which == "apply" else gate_spec
    before = _fp(spec)
    driver.write_text("extends SceneTree\\n# version TWO\\n", encoding="utf-8")
    after = _fp(spec)
    moved = [k for k in set(before) | set(after)
             if before.get(k) != after.get(k)]
    assert moved == ["driver_src_hash"], moved


def test_a_missing_driver_is_not_an_exception(apply_spec, driver):
    """`plan_commands` raises FileNotFoundError for a missing driver, and that
    is the right place for it. The fingerprint runs FIRST and must not turn a
    missing file into a crash before the message that explains it."""
    driver.unlink()
    fp = _fp(apply_spec)
    assert "driver_src_hash" not in fp


def test_the_adapter_version_moved_so_existing_entries_invalidate():
    """Hashing a new input does not invalidate anything on its own: an entry
    written before the key existed still matches on every key it DID record.
    The version bump is what forces the one re-run."""
    assert LuxAdapter.adapter_version != "0.4.0"
'''


def _require_files() -> None:
    missing = [str(p) for p in TOUCHED if not p.is_file()]
    if missing:
        sys.exit("REFUSING: file(s) not found:\n  " + "\n  ".join(missing))


def _plan(text: str) -> tuple[str, list[str]]:
    notes = []
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times, expected 1.")
        text = text.replace(old, new, 1)
        notes.append(f"  ok  {label}")
    return text, notes


def cmd_check() -> int:
    _require_files()
    for p in TOUCHED:
        print("   ", _stamp(p))
    src = ADAPTER.read_text(encoding="utf-8")
    if "driver_src_hash" in src:
        print("\nALREADY APPLIED.")
        return 0
    _, notes = _plan(src)
    print()
    print("\n".join(notes))
    print(f"\nVERSION {VERSION.read_text(encoding='utf-8').strip()} -> {NEW_VERSION}")
    print(f"NEW FILE {TEST.relative_to(ROOT)}")
    return 0


def cmd_apply() -> int:
    _require_files()
    src = ADAPTER.read_text(encoding="utf-8")
    if "driver_src_hash" in src:
        print("ALREADY APPLIED; nothing to do.")
        return 0
    ver_old = VERSION.read_text(encoding="utf-8").strip()
    if ver_old == NEW_VERSION:
        raise SystemExit(f"REFUSING: VERSION already reads {NEW_VERSION}")
    log = CHANGELOG.read_text(encoding="utf-8")
    if f"[{NEW_VERSION}]" in log:
        raise SystemExit(f"REFUSING: CHANGELOG already has [{NEW_VERSION}]")

    new_src, notes = _plan(src)

    for p in TOUCHED:
        (p.parent / f"{p.name}.{TAG}").write_bytes(p.read_bytes())

    e = _eol(ADAPTER)
    ADAPTER.write_text(new_src if e == "\n" else new_src.replace("\n", "\r\n"),
                       encoding="utf-8", newline="")
    tail = "\n" if b"\n" in VERSION.read_bytes() else ""
    VERSION.write_text(NEW_VERSION + tail, encoding="utf-8", newline="")
    ec = _eol(CHANGELOG)
    entry = CHANGELOG_ENTRY if ec == "\n" else CHANGELOG_ENTRY.replace("\n", "\r\n")
    CHANGELOG.write_text(entry + log, encoding="utf-8", newline="")
    TEST.parent.mkdir(parents=True, exist_ok=True)
    TEST.write_text(TEST_SOURCE, encoding="utf-8", newline="")

    print("\n".join(notes))
    print(f"  ok  VERSION {ver_old} -> {NEW_VERSION}")
    print(f"  ok  CHANGELOG [{NEW_VERSION}] prepended")
    print(f"  ok  wrote {TEST.relative_to(ROOT)}")
    print("\nafter:")
    for p in TOUCHED + [TEST]:
        print("   ", _stamp(p))
    print(f"\nsidecars .{TAG}; `--revert` restores them.")
    return 0


def cmd_revert() -> int:
    n = 0
    for p in TOUCHED:
        side = p.parent / f"{p.name}.{TAG}"
        if side.is_file():
            p.write_bytes(side.read_bytes())
            side.unlink()
            print(f"  restored {p.name}")
            n += 1
    if TEST.is_file():
        TEST.unlink()
        print(f"  removed {TEST.name}")
        n += 1
    if not n:
        print("nothing to revert.")
    return 0


def _pytest(args: list[str]):
    return subprocess.run([sys.executable, "-m", "pytest"] + args,
                          cwd=str(LF), capture_output=True, text=True)


def _falsify(name: str, mutate) -> None:
    orig = ADAPTER.read_bytes()
    try:
        ADAPTER.write_bytes(mutate(orig.decode("utf-8")).encode("utf-8"))
        r = _pytest([str(TEST.relative_to(LF))])
        if r.returncode == 0:
            raise SystemExit(f"SELFTEST FAILED: mutation '{name}' did not fail "
                             f"the tests.\n" + r.stdout[-2000:])
        if r.returncode == 5:
            raise SystemExit(f"SELFTEST FAILED: mutation '{name}' -- pytest "
                             f"collected NOTHING (rc=5), which is a failure, "
                             f"not a pass.\n" + r.stdout[-2000:])
        print(f"  ok  falsified: {name}  (rc={r.returncode})")
    finally:
        ADAPTER.write_bytes(orig)


def cmd_selftest() -> int:
    _require_files()
    if "driver_src_hash" not in ADAPTER.read_text(encoding="utf-8"):
        raise SystemExit("SELFTEST: patch is not applied; run it first.")
    if not TEST.is_file():
        raise SystemExit(f"SELFTEST: {TEST} missing.")

    r = _pytest([str(TEST.relative_to(LF))])
    if r.returncode != 0:
        raise SystemExit("SELFTEST FAILED: new tests do not pass.\n"
                         + r.stdout[-3000:])
    print("  ok  new tests pass (rc=0)")

    _falsify("the driver hash removed",
             lambda t: t.replace('fp["driver_src_hash"] = hash_file',
                                 'fp["unused_hash"] = hash_file'))
    _falsify("the driver hashed BELOW the fixture-gate branch, missing the gate",
             lambda t: t.replace(
                 '        driver = job_spec.get("driver_src")\n'
                 '        if driver and Path(str(driver)).exists():\n'
                 '            fp["driver_src_hash"] = hash_file(Path(str(driver)))\n',
                 '')
             .replace('        for key in ("composed_scene", "lights_json"):',
                      '        driver = job_spec.get("driver_src")\n'
                      '        if driver and Path(str(driver)).exists():\n'
                      '            fp["driver_src_hash"] = hash_file(Path(str(driver)))\n'
                      '        for key in ("composed_scene", "lights_json"):'))
    _falsify("adapter_version put back to 0.4.0",
             lambda t: t.replace('adapter_version = "0.5.0"',
                                 'adapter_version = "0.4.0"'))

    r = _pytest([])
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
    if r.returncode == 5:
        raise SystemExit("SELFTEST FAILED: full suite collected NOTHING (rc=5)")
    if r.returncode != 0:
        raise SystemExit(f"SELFTEST FAILED: full suite rc={r.returncode}\n"
                         + r.stdout[-4000:])
    print(f"  ok  full suite rc=0 :: {tail[0] if tail else '(no summary)'}")
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
