"""Level Factory 0.218.1: the z-fight gate says WARN, which is what the pipeline does with it (factory roadmap 177).

THE DECISION 177 OWED -- block, warn or delete -- made 2026-10-19 under the walker's standing instruction to make
decisions that can be changed later: WARN NOW, AND BLOCK ONCE THE LIBRARY COUNTS ZERO.

WHY WARN IS ALREADY TRUE. `run_presentation_compose.py` printed `z-fight gate [FAIL]` and `ERROR: coplanar surfaces
detected -- the package would flicker` and returned 3, under a comment saying a package that z-fights must not ship.
None of that held: the compose job is planned `exit_advisory` (`apps/cli/commands`), so the scheduler records it
SUCCEEDED, and the presentation adapter files the pairs as PRESENTATION_ZFIGHT, severity moderate, blocking False
(`adapters/presentation`, pinned by `test_presentation_gates_are_reported.py`). Cold run 9322 printed [FAIL] and
ERROR twice and shipped. A label that says FAIL over a job recorded SUCCEEDED is the shape this item is named for --
a gate printing FAIL on five consecutive cold runs that nobody read.

WHAT IS LEFT FOR "BLOCK". 9322's four pairs, all with an open side, all Deli Counter geometry: deli_a01's
`ext_0_E_seg10` against `int_0_1_seg18` (an exterior wall segment ending on a partition's two faces, 0.9 m2 each),
and the office's `base:VAULTLEDGE_0` against `reception_desk` (the ledge standing inside the desk, both 5 m long,
ends at +/-2.5 m, 0.2 m2 each). When the library counts zero, the adapter's finding becomes a blocker and this
label FAIL again -- one line each.

What it changes (anchored; the file pinned by hash; nothing written on a miss):
  * assets/scripts/run_presentation_compose.py -- `zfight_gate(z)` returns the gate's line and a warning, on the
    shape of `placement_gate`; the line says OK or WARN; the warning names the pairs and says where the verdict
    lives; the exit stays 3, which the scheduler treats as advisory; the comment above it says so.
  * tests/unit/test_zfight_gate_warns.py (new, 5; all fail on 0.218.0): the line, the named pairs, no FAIL and no
    ERROR, a clean check carries no warning, the advisory exit kept.
  * VERSION 0.218.0 -> 0.218.1, CHANGELOG.

    python patches/patch_lf_zfight_warns.py --tests   # the new test file only (prove it fails first)
    python patches/patch_lf_zfight_warns.py           # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
RUNNER = LF / "assets" / "scripts" / "run_presentation_compose.py"
SHA = "c902b0979a92c190"

HELPER_OLD = r'''    return line, err


def main() -> int:
'''
HELPER_NEW = r'''    return line, err


def zfight_gate(z: dict) -> tuple[str, str | None]:
    """The z-fight gate's log line, and a WARNING when it found pairs --
    `None` when it found none (0.218.1, factory roadmap 177).

    WARN, NOT FAIL, because that is what the pipeline does with it: the
    compose job is `exit_advisory`, so the scheduler records it SUCCEEDED, and
    the presentation adapter files the pairs as PRESENTATION_ZFIGHT, moderate
    and not blocking. This printed `[FAIL]` and `ERROR` over that from cold run
    9003 on; 9322 printed both twice and shipped. The call, made 2026-10-19 and
    meant to be changed: warn now, block once the library counts zero -- when
    the adapter's finding becomes a blocker and this label FAIL again.
    """
    ok = bool(z.get("ok"))
    line = (f"[compose] z-fight gate [{'OK' if ok else 'WARN'}]: "
            f"{z.get('pairs', '?')} coplanar pair(s) across "
            f"{z.get('solids', '?')} solids"
            + (f" ({z.get('error')})" if z.get("error") else ""))
    if ok:
        return line, None
    named = [f"{f.get('a')} / {f.get('b')}" for f in (z.get("findings") or [])[:6]]
    warn = ("[compose] WARNING: %s coplanar pair(s) the package may flicker on%s "
            "-- reported as PRESENTATION_ZFIGHT, moderate and not blocking; it "
            "blocks once the library counts zero (factory roadmap 177). See "
            "zfight_check in the manifest."
            % (z.get("pairs", "?"), (": " + "; ".join(named)) if named else ""))
    return line, warn


def main() -> int:
'''

LINE_OLD = r'''    z = man.get("zfight_check") or {}
    ztag = "OK" if z.get("ok") else "FAIL"
    print(f"[compose] z-fight gate [{ztag}]: {z.get('pairs', '?')} coplanar "
          f"pair(s) across {z.get('solids', '?')} solids"
          + (f" ({z.get('error')})" if z.get("error") else ""))
'''
LINE_NEW = r'''    z = man.get("zfight_check") or {}
    zline, zwarn = zfight_gate(z)
    print(zline)
'''

EXIT_OLD = r'''    # A package that z-fights must not ship: fail the compose job so the
    # pipeline (and its cache) records a red, not a flickering deliverable.
    if not z.get("ok"):
        print("[compose] ERROR: coplanar surfaces detected -- the package "
              "would flicker. See zfight_check in the manifest.",
              file=sys.stderr)
        return 3
'''
EXIT_NEW = r'''    # Z-FIGHTING WARNS (0.218.1, factory roadmap 177; see `zfight_gate`). The
    # exit stays 3 -- the job is `exit_advisory`, so the scheduler records it
    # SUCCEEDED either way, and the verdict lives in the adapter's
    # PRESENTATION_ZFIGHT finding, moderate and not blocking. The comment that
    # stood here said a package that z-fights must not ship; none ever was stopped.
    if zwarn:
        print(zwarn, file=sys.stderr)
        return 3
'''

TEST = r'''"""The z-fight gate says WARN, which is what the pipeline does with it (0.218.1, factory roadmap 177).

`run_presentation_compose.py` printed `z-fight gate [FAIL]` and `ERROR: coplanar surfaces detected` over a job the
scheduler records SUCCEEDED (the compose job is `exit_advisory`) and a finding the presentation adapter files as
moderate and not blocking. The decision 177 owed -- block, warn or delete -- was made 2026-10-19, meant to be
changed: warn now, block once the library counts zero.

Run: python -m pytest -q tests/unit/test_zfight_gate_warns.py
"""
import importlib.util
import sys
from pathlib import Path

_SCRIPT = (Path(__file__).resolve().parents[2] / "assets" / "scripts"
           / "run_presentation_compose.py")


def _driver():
    spec = importlib.util.spec_from_file_location("run_presentation_compose", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


#: cold run 9322's office, as its compose summary read it
OFFICE_9322 = {"ok": False, "pairs": 2, "solids": 425, "scene": "site.tscn", "buried_pairs": 129,
               "greybox_internal_pairs": 0,
               "findings": [{"a": "base:VAULTLEDGE_0", "b": "reception_desk", "axis": 0, "plane": 2.5,
                             "side": "max", "area": 0.2},
                            {"a": "base:VAULTLEDGE_0", "b": "reception_desk", "axis": 0, "plane": -2.5,
                             "side": "min", "area": 0.2}]}


def test_pairs_are_a_warning_line():
    line, warn = _driver().zfight_gate(OFFICE_9322)
    assert line == "[compose] z-fight gate [WARN]: 2 coplanar pair(s) across 425 solids", line
    assert "[FAIL]" not in line


def test_the_warning_names_the_pairs_and_where_the_verdict_lives():
    _line, warn = _driver().zfight_gate(OFFICE_9322)
    assert warn.startswith("[compose] WARNING: 2 coplanar pair(s)"), warn
    assert "base:VAULTLEDGE_0 / reception_desk" in warn
    assert "PRESENTATION_ZFIGHT, moderate and not blocking" in warn
    assert "ERROR" not in warn


def test_a_clean_check_carries_no_warning():
    line, warn = _driver().zfight_gate({"ok": True, "pairs": 0, "solids": 233})
    assert line == "[compose] z-fight gate [OK]: 0 coplanar pair(s) across 233 solids"
    assert warn is None


def test_the_runner_prints_no_zfight_error_and_keeps_its_advisory_exit():
    src = _SCRIPT.read_text(encoding="utf-8")
    assert "coplanar surfaces detected -- the package would flicker" not in src
    assert '"OK" if z.get("ok") else "FAIL"' not in src
    assert "if zwarn:" in src and src.count("return 3") == 1


def test_the_call_is_recorded_as_one_that_can_change():
    src = _SCRIPT.read_text(encoding="utf-8")
    assert "block once the library counts zero" in src and "meant to be changed" in src
'''

CHANGELOG = '''## [0.218.1] - the z-fight gate says WARN, which is what the pipeline does with it

**Factory roadmap 177's decision, made 2026-10-19 and meant to be changed: warn now, block once the library
counts zero.** `run_presentation_compose.py` printed `z-fight gate [FAIL]` and `ERROR: coplanar surfaces detected
-- the package would flicker`, under a comment saying a package that z-fights must not ship. None of it held. The
compose job is `exit_advisory`, so the scheduler records it SUCCEEDED, and the presentation adapter files the pairs
as PRESENTATION_ZFIGHT, moderate and not blocking. Cold run 9322 printed both twice and shipped.

### Changed
- `zfight_gate(z)` returns the gate's line, OK or WARN, and a warning naming the pairs and saying where the verdict
  lives, on the shape of `placement_gate`. The exit stays 3, advisory; the comment above it says so.

### Left for "block"
Cold run 9322's four pairs, all Deli Counter geometry: deli_a01's `ext_0_E_seg10` against `int_0_1_seg18`, an
exterior wall segment ending on a partition's faces, and the office's `base:VAULTLEDGE_0` against `reception_desk`,
the ledge standing inside the desk. When the library counts zero, the finding becomes a blocker and the label FAIL.

### Added
- `tests/unit/test_zfight_gate_warns.py` (5, all fail on 0.218.0).

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def write_tests():
    p = LF / "tests" / "unit" / "test_zfight_gate_warns.py"
    assert not p.exists(), f"{p.name} exists"
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote level_factory/tests/unit/test_zfight_gate_warns.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = RUNNER.read_bytes()
    assert b"\r\n" not in raw, "run_presentation_compose.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA, ("run_presentation_compose.py is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert "def zfight_gate" not in text, "already applied"
    text = _once(text, HELPER_OLD, HELPER_NEW, "placement_gate's return and main")
    text = _once(text, LINE_OLD, LINE_NEW, "the z-fight line")
    text = _once(text, EXIT_OLD, EXIT_NEW, "the z-fight exit")
    v = LF / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.218.0", v.read_text(encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    rawc = cl.read_bytes()
    assert b"\r\n" not in rawc, "CHANGELOG.md is LF"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.218.0]"), ctext[:40]
    RUNNER.write_bytes(text.encode("utf-8"))
    v.write_text("0.218.1", encoding="utf-8")
    cl.write_bytes((CHANGELOG + ctext).encode("utf-8"))
    write_tests()
    print("Level Factory 0.218.1 applied: the z-fight gate warns; test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
