#!/usr/bin/env python3
"""level_factory 0.41.0 -- ask Lux what it HAS, not what it was asked for.

`lux.quality.json["preset"]` is, and has always been, the `--preset` argument
written straight back out:

    var quality := {"preset": preset_name, ...}

Roadmap item 53 ranked FIRST a comparison of that field against Level
Factory's `_preset_for(model)`. Those are the same string. The check cannot
fail, in an item whose whole subject is checks that cannot fail. The item's
own status line says the file "already echoes the applied preset back"; it
echoes the REQUEST. That is the fourth mechanism this session published
before reading the source, and it is corrected here rather than shipped.

The observable does exist and it is one call. `LuxRoot.get_current_preset()`
returns `_current`, and `_current` is assigned in exactly one place --
`_apply_immediate`, from the LIBRARY resource -- so the string cannot be the
argument coming back round. Reading it also covers the failure the existing
dictionary check cannot:

    func apply_preset(preset, blend_time = 0.0) -> void:
        if not _initialized:
            active_preset = preset      # <-- and applies NOTHING
            return

The name is in the library, so `preset_known` is true, so no issue is
emitted, and the level ships with no look. The dictionary says the preset
exists; only LuxRoot says it arrived.

Three edits, each one a discarded truth:

  1. read `get_current_preset()` back after the blend and report it as
     `preset_applied`, alongside the unchanged `preset` (the request).
  2. `LUX_PRESET_NOT_APPLIED` when the two disagree. No Python changes:
     the driver already writes findings to `lux.validation.json` and the
     adapter's `normalize_validation` already passes arbitrary codes
     through, so this reaches the findings channel for free.
  3. `ResourceSaver.save(...)`'s return was discarded. `applied_ok` tracked
     only `pack()`, so a save that failed reported `applied: true` for a
     scene never written.

Usage:
    pwsh> python patch_lf_041.py --check
    pwsh> python patch_lf_041.py
    pwsh> python patch_lf_041.py --selftest
    pwsh> python patch_lf_041.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LF = ROOT / "level_factory"
DRIVER = LF / "assets" / "godot" / "run_lux_apply.gd"
VERSION = LF / "VERSION"
CHANGELOG = LF / "CHANGELOG.md"
TEST = LF / "tests" / "unit" / "test_lux_preset_readback.py"

TAG = "pre_041"
NEW_VERSION = "0.41.0"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8].upper()


def _eol(path: Path) -> str:
    """Keyed off the FILE, never off an anchor. An anchor that happens to be
    LF inside a CRLF file would rewrite the whole file's line endings."""
    raw = path.read_bytes()
    return "\r\n" if b"\r\n" in raw else "\n"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")


def _stamp(path: Path) -> str:
    t = _read(path)
    return f"{path.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


# --------------------------------------------------------------------------
# the edits
# --------------------------------------------------------------------------

# NOTE ON THE ANCHORS: this file is GDScript and indents with TABS. Every
# anchor below carries real tab characters. A patch that silently converted
# them to spaces would apply cleanly and produce a file Godot refuses to
# parse, which is the same class of failure as writing a BOM from
# powershell 5.1.

A1_OLD = (
    "\t\tlux.blend_to_preset(StringName(preset_name), 0.0)\n"
    "\tawait process_frame\n"
)
A1_NEW = (
    "\t\tlux.blend_to_preset(StringName(preset_name), 0.0)\n"
    "\tawait process_frame\n"
    "\n"
    "\t# WHAT LUX HAS, NOT WHAT IT WAS ASKED FOR.\n"
    "\t#\n"
    "\t# `_current` is assigned in exactly one place -- `_apply_immediate`,\n"
    "\t# from the library resource -- so this string cannot be the argument\n"
    "\t# arriving back round. The quality record's `preset` field always was\n"
    "\t# that argument, which made comparing it against Level Factory's\n"
    "\t# `_preset_for` a comparison of a string with itself.\n"
    "\t#\n"
    "\t# It also covers what the dictionary check above cannot. `apply_preset`\n"
    "\t# RETURNS EARLY when `_initialized` is false, assigning active_preset\n"
    "\t# and applying nothing. The name is in the library, so the request looks\n"
    "\t# honoured, no issue is raised, and the level ships with no look. The\n"
    "\t# dictionary says the preset exists; only LuxRoot says it arrived.\n"
    "\t#\n"
    "\t# `get`/`has_method` rather than a typed call: `lux` is a Node here and\n"
    "\t# LuxRoot's script is loaded BY PATH, so the class type does not exist\n"
    "\t# to the compiler. This is the same idiom the lines above already use\n"
    "\t# for `_preset_library` and `active_preset`.\n"
    "\tvar reported := \"\"\n"
    "\tif lux.has_method(\"get_current_preset\"):\n"
    "\t\tvar cur: Object = lux.get_current_preset()\n"
    "\t\tif cur != null:\n"
    "\t\t\treported = String(cur.get(\"preset_name\"))\n"
)

A2_OLD = "\tResourceSaver.save(applied, out_dir + \"/lux.applied.tscn\")\n"
A2_NEW = (
    "\t# The return was discarded. `applied_ok` tracked only pack(), so a save\n"
    "\t# that failed -- read-only dir, bad path, no space -- reported\n"
    "\t# `applied: true` for a scene that was never written.\n"
    "\tif ResourceSaver.save(applied, out_dir + \"/lux.applied.tscn\") != OK:\n"
    "\t\tapplied_ok = false\n"
)

A3_OLD = "\tvar quality := {\"preset\": preset_name, \"applied\": applied_ok,\n"
A3_NEW = (
    "\t# `preset` stays the REQUEST, unchanged, because that is what it has\n"
    "\t# always meant and nothing should have to guess which release it is\n"
    "\t# reading. `preset_applied` is the new one and is the one worth\n"
    "\t# comparing against anything.\n"
    "\tvar quality := {\"preset\": preset_name, \"preset_applied\": reported,\n"
    "\t\t\"applied\": applied_ok,\n"
)

A4_OLD = (
    "\t\t\t\"message\": \"preset '%s' is not in the registered library;"
    " look not applied\" % preset_name})\n"
)
A4_NEW = A4_OLD + (
    "\telif not preset_name.is_empty() and reported != String(preset_name):\n"
    "\t\t# The name resolved and the look still did not land. Moderate, not\n"
    "\t\t# blocker: a level with the wrong look is shippable and a level that\n"
    "\t\t# nobody was told about is not.\n"
    "\t\tissues.append({\"code\": \"LUX_PRESET_NOT_APPLIED\", \"severity\": \"moderate\",\n"
    "\t\t\t\"category\": \"presentation\",\n"
    "\t\t\t\"message\": \"requested preset '%s' but LuxRoot reports '%s'\""
    " % [preset_name, reported]})\n"
)

A5_OLD = "\tprint(\"[lux] applied preset '%s' -> %s\" % [preset_name, out_dir])\n"
A5_NEW = (
    "\tprint(\"[lux] requested '%s' applied '%s' -> %s\""
    " % [preset_name, reported, out_dir])\n"
)

DRIVER_EDITS = [
    ("read the applied preset back off LuxRoot", A1_OLD, A1_NEW),
    ("stop reporting a failed save as applied", A2_OLD, A2_NEW),
    ("report request and result as separate keys", A3_OLD, A3_NEW),
    ("raise LUX_PRESET_NOT_APPLIED when they disagree", A4_OLD, A4_NEW),
    ("say both strings on stdout", A5_OLD, A5_NEW),
]

CHANGELOG_ENTRY = """## [0.41.0] - the applied preset is read off Lux, not echoed from the request

`lux.quality.json["preset"]` was the `--preset` argument written straight back
out:

    var quality := {"preset": preset_name, ...}

Roadmap item 53 ranked FIRST a comparison of that field against Level
Factory's `_preset_for(model)`, and its status line said the file "already
echoes the applied preset back". It echoed the REQUEST. The two strings are
the same string; the check could not fail. That is a check that cannot fail,
proposed inside an item about checks that cannot fail, and it was caught by
reading `run_lux_apply.gd` rather than by running it.

WHAT LUX ACTUALLY OFFERS

`LuxRoot.get_current_preset()` returns `_current`, assigned in exactly one
place -- `_apply_immediate`, from the library resource. Reading it back after
the blend also covers the failure the driver's existing library-dictionary
check cannot see:

    func apply_preset(preset, blend_time = 0.0) -> void:
        if not _initialized:
            active_preset = preset      # and applies NOTHING
            return

The name is in the library, so `preset_known` is true, so no issue is raised,
and the level ships with no look. The dictionary says the preset exists; only
LuxRoot says it arrived.

THE CHANGES

    lux.quality.json   "preset"          the REQUEST, unchanged meaning
                       "preset_applied"  NEW -- LuxRoot.get_current_preset()

    lux.validation.json  LUX_PRESET_NOT_APPLIED (moderate) when the name
                         resolved and the look still did not land

No Python changed. The driver already writes findings to
`lux.validation.json` and the Lux adapter's `normalize_validation` already
passes arbitrary codes through, so the new finding reaches the findings
channel without touching the adapter.

Third edit, same file, same shape of defect: `ResourceSaver.save(...)`'s
return was discarded and `applied_ok` tracked only `pack()`, so a save that
failed reported `applied: true` for a scene never written.

`tests/unit/test_lux_preset_readback.py` is a SOURCE-SHAPE test and says so
in its own docstring: applying a preset needs a Godot process and unit CI has
no headless-Godot harness. It cannot prove the driver works. It pins the one
regression that would restore the tautology without changing an output key --
re-pointing `preset_applied` at `preset_name`.

Roadmap item 53, first ranked fix. The item's premise is corrected in place
rather than quietly dropped.

"""

TEST_SOURCE = '''"""The applied preset must be READ OFF LuxRoot, never the argument echoed back.

`lux.quality.json["preset"]` has always been the `--preset` argument written
straight back out, so comparing it against Level Factory's `_preset_for` -- the
comparison roadmap item 53 ranked first -- compares a string with itself. The
item said the file "already echoes the applied preset back". It echoed the
REQUEST. `preset_applied` is read from `LuxRoot.get_current_preset()`, whose
`_current` is assigned only by `_apply_immediate`, from the library resource.

THIS IS A SOURCE-SHAPE TEST AND IT IS ONE ON PURPOSE. Applying a preset needs a
Godot process and unit CI has no headless-Godot harness, so nothing here can
prove the driver works -- the hardware evidence is a run, not a test. What it
can prove is that nobody quietly re-points `preset_applied` back at
`preset_name`, which is the one regression that would restore the tautology
without changing a single output key or failing anything else.

Run:  python -m pytest tests/unit/test_lux_preset_readback.py
"""
import re
from pathlib import Path

import pytest

DRIVER = (Path(__file__).resolve().parents[2]
          / "assets" / "godot" / "run_lux_apply.gd")

# `preset_name` as a WHOLE word, not reached through a member access and not
# inside quotes -- so `cur.get("preset_name")`, which is the correct source,
# does not read as the argument.
_ARG = re.compile(r'(?<![.\\w"])preset_name\\b')
_ASSIGN = re.compile(r"^(?:var\\s+)?reported\\s*:?=[^=]")


@pytest.fixture(scope="module")
def src() -> str:
    assert DRIVER.is_file(), f"driver missing at {DRIVER}"
    return DRIVER.read_text(encoding="utf-8")


def test_the_applied_preset_comes_from_lux(src):
    assert "get_current_preset" in src


def test_the_applied_preset_is_never_assigned_from_the_argument(src):
    """An assignment is the bug. A comparison is the entire point of the fix,
    so `reported != String(preset_name)` must not trip this."""
    bad = []
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("#") or "reported" not in s:
            continue
        if not _ASSIGN.match(s):
            continue
        if _ARG.search(s):
            bad.append(s)
    assert bad == [], bad


def test_the_comparison_this_test_protects_is_actually_present(src):
    """Without this, the test above passes trivially on a file that dropped
    the comparison altogether."""
    assert _ARG.search(src) is not None
    assert any("reported" in l and "!=" in l for l in src.splitlines())


def test_quality_json_reports_the_request_and_the_result_separately(src):
    assert '"preset": preset_name' in src
    assert '"preset_applied": reported' in src


def test_a_preset_that_did_not_apply_is_a_finding(src):
    assert "LUX_PRESET_NOT_APPLIED" in src


def test_a_failed_save_is_not_reported_as_applied(src):
    saves = [l for l in src.splitlines() if "ResourceSaver.save(" in l]
    assert saves, "driver no longer saves the applied scene"
    for line in saves:
        assert "!= OK" in line or "== OK" in line, line.strip()
'''


# --------------------------------------------------------------------------
# apply / check / revert
# --------------------------------------------------------------------------

TOUCHED = [DRIVER, VERSION, CHANGELOG]


def _require_files() -> None:
    """Every file this patch touches, checked BEFORE anything is written. A
    half-applied patch that then raised on a missing CHANGELOG is a thing
    that has already happened here once."""
    missing = [str(p) for p in TOUCHED if not p.is_file()]
    if missing:
        sys.exit("REFUSING: file(s) not found:\n  " + "\n  ".join(missing))


def _plan_driver(text: str) -> tuple[str, list[str]]:
    notes = []
    for label, old, new in DRIVER_EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times, expected 1.\n"
                f"anchor:\n{old!r}")
        text = text.replace(old, new, 1)
        notes.append(f"  ok  {label}")
    return text, notes


def cmd_check() -> int:
    _require_files()
    for p in TOUCHED:
        print("   ", _stamp(p))
    src = _read(DRIVER)
    if "preset_applied" in src:
        print("\nALREADY APPLIED (driver already reports preset_applied).")
        return 0
    _, notes = _plan_driver(src)
    print("\nall driver anchors resolve, exactly once each:")
    print("\n".join(notes))
    ver = _read(VERSION).strip()
    print(f"\nVERSION {ver} -> {NEW_VERSION}")
    print(f"CHANGELOG gains a [{NEW_VERSION}] section at the top")
    print(f"NEW FILE {TEST.relative_to(ROOT)}"
          + ("  (EXISTS -- will be overwritten)" if TEST.is_file() else ""))
    return 0


def cmd_apply() -> int:
    _require_files()
    src = _read(DRIVER)
    if "preset_applied" in src:
        print("ALREADY APPLIED; nothing to do.")
        return 0

    ver_old = _read(VERSION).strip()
    if ver_old == NEW_VERSION:
        raise SystemExit(f"REFUSING: VERSION already reads {NEW_VERSION}")
    log = _read(CHANGELOG)
    if f"[{NEW_VERSION}]" in log:
        raise SystemExit(f"REFUSING: CHANGELOG already has [{NEW_VERSION}]")

    new_src, notes = _plan_driver(src)          # may raise; nothing written yet

    # sidecars first
    for p in TOUCHED:
        (p.parent / f"{p.name}.{TAG}").write_bytes(p.read_bytes())

    eol_d = _eol(DRIVER)
    _write(DRIVER, new_src if eol_d == "\n"
           else new_src.replace("\n", "\r\n"))

    eol_v = _eol(VERSION) if b"\n" in VERSION.read_bytes() else ""
    _write(VERSION, NEW_VERSION + eol_v)

    eol_c = _eol(CHANGELOG)
    entry = CHANGELOG_ENTRY if eol_c == "\n" else CHANGELOG_ENTRY.replace("\n", "\r\n")
    _write(CHANGELOG, entry + log)

    TEST.parent.mkdir(parents=True, exist_ok=True)
    _write(TEST, TEST_SOURCE)

    print("\n".join(notes))
    print(f"  ok  VERSION {ver_old} -> {NEW_VERSION}")
    print(f"  ok  CHANGELOG [{NEW_VERSION}] prepended")
    print(f"  ok  wrote {TEST.relative_to(ROOT)}")
    print("\nafter:")
    for p in TOUCHED + [TEST]:
        print("   ", _stamp(p))
    print(f"\nsidecars written with suffix .{TAG}; `--revert` restores them.")
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


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

def _falsify(name: str, mutate) -> None:
    """Run the new test file against a MUTATED driver and require a failure.
    A check that passes on the broken input is not a check."""
    orig = DRIVER.read_bytes()
    try:
        DRIVER.write_bytes(mutate(orig.decode("utf-8")).encode("utf-8"))
        r = subprocess.run([sys.executable, "-m", "pytest",
                            str(TEST.relative_to(LF))],
                           cwd=str(LF), capture_output=True, text=True)
        if r.returncode == 0:
            raise SystemExit(
                f"SELFTEST FAILED: mutation '{name}' did not fail the tests.\n"
                + r.stdout[-2000:])
        if r.returncode == 5:
            raise SystemExit(
                f"SELFTEST FAILED: mutation '{name}' -- pytest collected "
                f"NOTHING (rc=5). That is a failure, not a pass.\n"
                + r.stdout[-2000:])
        print(f"  ok  falsified: {name}  (rc={r.returncode})")
    finally:
        DRIVER.write_bytes(orig)


def cmd_selftest() -> int:
    _require_files()
    src = _read(DRIVER)
    if "preset_applied" not in src:
        raise SystemExit("SELFTEST: patch is not applied; run it first.")
    if not TEST.is_file():
        raise SystemExit(f"SELFTEST: {TEST} missing.")

    # 1. TABS survived. A space-indented GDScript file parses as garbage.
    body = [l for l in src.splitlines() if l.startswith(" ") and l.strip()]
    if body:
        raise SystemExit("SELFTEST FAILED: space-indented line(s) in a "
                         f"tab-indented GDScript file, e.g.\n{body[0]!r}")
    print("  ok  driver is still tab-indented throughout")

    # 2. no BOM, no CRLF drift
    raw = DRIVER.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("SELFTEST FAILED: BOM written into the driver.")
    print("  ok  no BOM")

    # 3. the tests pass as shipped
    r = subprocess.run([sys.executable, "-m", "pytest",
                        str(TEST.relative_to(LF))],
                       cwd=str(LF), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("SELFTEST FAILED: new tests do not pass.\n"
                         + r.stdout[-3000:])
    print(f"  ok  new tests pass (rc=0)")

    # 4. and they FAIL on each way of putting the defect back
    _falsify("preset_applied re-pointed at the argument",
             lambda t: t.replace(
                 "\t\t\treported = String(cur.get(\"preset_name\"))",
                 "\t\t\treported = preset_name"))
    _falsify("the readback deleted",
             lambda t: t.replace("get_current_preset", "get_nothing_at_all"))
    _falsify("the save return discarded again",
             lambda t: t.replace(
                 "\tif ResourceSaver.save(applied, out_dir + \"/lux.applied.tscn\") != OK:\n"
                 "\t\tapplied_ok = false\n",
                 "\tResourceSaver.save(applied, out_dir + \"/lux.applied.tscn\")\n"))
    _falsify("the finding removed",
             lambda t: t.replace("LUX_PRESET_NOT_APPLIED", "LUX_SOMETHING_ELSE"))

    # 5. the WHOLE level_factory suite. pyproject sets addopts = "-q"; passing
    #    -q again makes it -qq and drops the count line.
    r = subprocess.run([sys.executable, "-m", "pytest"],
                       cwd=str(LF), capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
    if r.returncode == 5:
        raise SystemExit("SELFTEST FAILED: full suite collected NOTHING "
                         "(rc=5).\n" + r.stdout[-3000:])
    if r.returncode != 0:
        raise SystemExit("SELFTEST FAILED: full suite rc="
                         f"{r.returncode}\n" + r.stdout[-4000:])
    print(f"  ok  full suite rc=0 :: {tail[0] if tail else '(no summary line)'}")
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
