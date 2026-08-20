#!/usr/bin/env python3
"""level_factory 0.43.0 -- a per-object light cap, and a test that the two
project.godot writers agree.

MEASURED on lot_demo_001, 2026-08-18, 136 fixture lights across five buildings.
Counting lights whose range reaches each mesh's bounding box:

    building              meshes   >8   >16  >32  worst  worst mesh
    mansion_a02              163   26    11    0     26  roof_footprint
    pvp_station_ref          240   49    15    1     36  roof_footprint
    large_warehouse_a01      117    3     1    0     17  roof_footprint
    arena_a03                227   10     3    0     26  roof_footprint
    strip_club_a03           173   23     9    0     25  roof_footprint
    ---------------------------------------------------------------
    across all five          920  111    39    1

The compatibility renderer selects at most N lights per MESH and re-selects as
geometry moves through range, so a mesh over the cap drops lights and appears
to blink. Every offender is a building-wide roof or floor/ceiling plate 34-52 m
across, competing for the same slots as a 2 m wall segment -- and when one
loses, a whole room goes dark at once.

CONFIRMED ON HARDWARE, in the walk preview, in this order:
    engine default (8)   heavy blinking
    32                   mostly gone; "certain rooms" still drop  <- the 1 at 36
    forward_plus         none
The response tracks the NUMBER, not just the renderer, which is what pins the
mechanism. A renderer difference alone would not have improved at 32.

64 clears the measured worst case with headroom and keeps `gl_compatibility`,
which is the property the portable profile exists for.

THIS NUMBER IS A MITIGATION, NOT THE FIX. The fix is that one mesh should not
span a building. That is roadmap 54 and it is geometry work.

AND THE SECOND HALF. `walk_preview._PROJECT` carries this comment:

    ; Verbatim from export.py::_write_project_godot, and it must stay verbatim
    ...
    ; Two projects disagreeing about what a complete project.godot contains is
    ; how a human signs off lighting that was missing a rig.

That is an invariant stated in a comment with nothing enforcing it, in a file
whose own history records it being violated (2026-08-12,
`lux_area_light_rig.gd:61` failed to parse in a walk of the same package whose
portability test scored `parser_error_count 0`). The cap goes into BOTH
writers, and `tests/unit/test_project_godot_agreement.py` makes the agreement
a test instead of a hope.

Usage:
    pwsh> python patch_lf_043.py --check
    pwsh> python patch_lf_043.py
    pwsh> python patch_lf_043.py --selftest
    pwsh> python patch_lf_043.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LF = ROOT / "level_factory"
EXPORT = LF / "packages" / "exporting" / "export.py"
PREVIEW = LF / "packages" / "preview" / "walk_preview.py"
VERSION = LF / "VERSION"
CHANGELOG = LF / "CHANGELOG.md"
TEST = LF / "tests" / "unit" / "test_project_godot_agreement.py"

TAG = "pre_043"
NEW_VERSION = "0.43.0"
TOUCHED = [EXPORT, PREVIEW, VERSION, CHANGELOG]

CAP_COMMENT = (
    "; PER-OBJECT LIGHT CAP. The compatibility renderer selects at most N\n"
    "; lights per MESH and re-selects as geometry moves through range, so a\n"
    "; mesh over the cap drops lights and appears to blink. Measured on\n"
    "; lot_demo_001, 2026-08-18, 136 fixture lights over five buildings: 111\n"
    "; of 920 meshes exceed the engine default of 8, 39 exceed 16, and exactly\n"
    "; one -- pvp_station_ref's roof -- exceeds 32, at 36. Every offender is a\n"
    "; building-wide roof or floor/ceiling plate 34-52 m across, competing for\n"
    "; the same slots as a 2 m wall segment; when one loses, a whole room goes\n"
    "; dark at once. Confirmed in the walk preview: heavy blinking at the\n"
    "; default, mostly gone at 32 with certain rooms still dropping, none under\n"
    "; forward_plus -- the response tracks the NUMBER, which is what pins it.\n"
    "; 64 clears the measured worst case and keeps gl_compatibility, which is\n"
    "; the property this profile exists for. IT IS A MITIGATION. The fix is\n"
    "; that one mesh should not span a building -- roadmap 54.\n"
    "limits/opengl/max_lights_per_object=64\n"
)

E1_OLD = (
    '        "[rendering]\\n"\n'
    '        \'renderer/rendering_method="gl_compatibility"\\n\\n\'\n'
)
# CAP_COMMENT ends with the setting line itself; the comment lines and the
# setting are emitted separately here so the setting cannot be written twice.
# The first draft of this patch did exactly that -- and the agreement test
# still passed, because it parses settings into a dict and a duplicate key
# just overwrites. A test that cannot see a duplicated line is why the
# generated file gets read, not just asserted on.
_CAP_LINES = CAP_COMMENT.rstrip("\n").split("\n")
assert _CAP_LINES[-1].startswith("limits/opengl/max_lights_per_object=")
_CAP_ONLY_COMMENTS = _CAP_LINES[:-1]

E1_NEW = (
    '        "[rendering]\\n"\n'
    '        \'renderer/rendering_method="gl_compatibility"\\n\'\n'
    + "".join(f'        "{ln}\\n"\n' for ln in _CAP_ONLY_COMMENTS)
    + '        "limits/opengl/max_lights_per_object=64\\n\\n"\n'
)

E2_OLD = (
    "[rendering]\n"
    'renderer/rendering_method="gl_compatibility"\n'
    "\n"
    "[debug]\n"
)
E2_NEW = (
    "[rendering]\n"
    'renderer/rendering_method="gl_compatibility"\n'
    + CAP_COMMENT
    + "\n"
    "[debug]\n"
)

CHANGELOG_ENTRY = """## [0.43.0] - a per-object light cap, and a test that the two writers agree

A package with 136 fixture lights blinks when you walk it. The compatibility
renderer selects at most N lights per MESH and re-selects as geometry moves
through range; a mesh over the cap drops lights.

Measured on lot_demo_001, 2026-08-18, counting lights whose range reaches each
mesh's bounding box:

    building              meshes   >8   >16  >32  worst  worst mesh
    mansion_a02              163   26    11    0     26  roof_footprint
    pvp_station_ref          240   49    15    1     36  roof_footprint
    large_warehouse_a01      117    3     1    0     17  roof_footprint
    arena_a03                227   10     3    0     26  roof_footprint
    strip_club_a03           173   23     9    0     25  roof_footprint
    across all five          920  111    39    1

Every offender is a building-wide roof or floor/ceiling plate 34-52 m across,
competing for the same slots as a 2 m wall segment. When one loses, a whole
room goes dark at once -- which is what a human reported before any of this was
measured: "lights still blink a bit, or just turn off in certain rooms".

Confirmed in the walk preview, in this order: heavy blinking at the engine
default of 8; mostly gone at 32, with certain rooms still dropping -- which is
the single mesh at 36; none at all under forward_plus. The response tracks the
NUMBER, not just the renderer, and that is what pins the mechanism. A renderer
difference alone would not have improved at 32.

`max_lights_per_object=64` clears the measured worst case with headroom and
keeps `gl_compatibility`, which is the property the portable profile exists
for. IT IS A MITIGATION AND THE CHANGELOG SHOULD SAY SO: the fix is that one
mesh should not span a building, and that is roadmap 54.

THE SECOND HALF, WHICH IS THE MORE IMPORTANT ONE

`walk_preview._PROJECT` already carried this, in a comment:

    ; Verbatim from export.py::_write_project_godot, and it must stay verbatim
    ; Two projects disagreeing about what a complete project.godot contains is
    ; how a human signs off lighting that was missing a rig.

An invariant asserted in prose with nothing enforcing it -- in a file whose own
history records it being broken: on 2026-08-12 the preview lacked the debug
block and `lux_area_light_rig.gd:61` failed to parse in a walk of the same
package whose portability test had scored `parser_error_count 0`.

So the cap lands in BOTH writers, and `tests/unit/test_project_godot_agreement.py`
asserts that every setting the exporter writes under `[rendering]` and
`[debug]` also appears in the preview. The comment stops being a promise.

"""

TEST_SOURCE = '''"""The two project.godot writers must not drift apart.

`walk_preview._PROJECT` says so itself -- "Verbatim from
export.py::_write_project_godot, and it must stay verbatim" -- and then explains
the cost: "Two projects disagreeing about what a complete project.godot contains
is how a human signs off lighting that was missing a rig." On 2026-08-12 that is
exactly what happened; the preview lacked the debug block and
`lux_area_light_rig.gd:61` failed to parse in a walk of the same package whose
portability test had scored `parser_error_count 0`.

That invariant lived in a comment. This makes it a test.

It is deliberately ONE-DIRECTIONAL: everything the exporter writes must appear
in the preview, but the preview may add things (it has a player, a main scene of
its own, and `config/features`). A two-directional test would fail on the
preview's legitimate extras and would get deleted the first time it did.

Run:  python -m pytest tests/unit/test_project_godot_agreement.py
"""
import re

import pytest

from packages.exporting.export import _write_project_godot
from packages.preview.walk_preview import _PROJECT


@pytest.fixture()
def exported(tmp_path) -> str:
    _write_project_godot(tmp_path, "mission.tscn", "m")
    return (tmp_path / "project.godot").read_text(encoding="utf-8")


@pytest.fixture()
def preview() -> str:
    return _PROJECT.format(level="mission.tscn", name="m")


def _settings(text: str, section: str) -> dict:
    """key=value pairs under one [section], comments and blanks dropped."""
    out, cur = {}, None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            cur = s[1:-1]
            continue
        if not s or s.startswith(";") or "=" not in s:
            continue
        if cur == section:
            k, v = s.split("=", 1)
            out[k.strip()] = v.strip()
    return out


@pytest.mark.parametrize("section", ["rendering", "debug"])
def test_every_exported_setting_appears_in_the_preview(section, exported, preview):
    e, p = _settings(exported, section), _settings(preview, section)
    missing = {k: v for k, v in e.items() if p.get(k) != v}
    assert missing == {}, f"[{section}] drifted: {missing} (preview has {p})"


def test_the_sections_being_compared_are_not_empty(exported):
    """Without this, the test above passes trivially if a section is renamed
    and _settings silently returns {} for both."""
    assert _settings(exported, "rendering"), "no [rendering] settings parsed"
    assert _settings(exported, "debug"), "no [debug] settings parsed"


def test_the_light_cap_is_written_by_both(exported, preview):
    for name, text in (("export", exported), ("preview", preview)):
        v = _settings(text, "rendering").get("limits/opengl/max_lights_per_object")
        assert v is not None, f"{name} writes no per-object light cap"
        assert int(v) >= 64, f"{name} caps at {v}; measured worst case is 36"


def test_the_cap_is_only_meaningful_on_the_compatibility_renderer(exported):
    """If the profile ever moves to forward_plus the cap is dead weight and
    this test should be the thing that says so out loud."""
    assert _settings(exported, "rendering")["renderer/rendering_method"] == \\
        '"gl_compatibility"'


@pytest.mark.parametrize("which", ["exported", "preview"])
def test_no_setting_is_written_twice(which, exported, preview):
    """`_settings` returns a dict, so a duplicated line is invisible to every
    other test in this file. The first draft of 0.43.0 emitted the light cap
    twice and the suite stayed green. Read the LINES, not the dict."""
    text = exported if which == "exported" else preview
    keys = [l.split("=", 1)[0].strip() for l in text.splitlines()
            if "=" in l and not l.strip().startswith(";")
            and not l.strip().startswith("[")]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    assert dupes == [], f"{which} writes these settings more than once: {dupes}"


def test_the_package_stays_plugin_free_and_autoload_free(exported):
    """The portable profile's whole claim. A light cap must not smuggle in a
    dependency."""
    assert "[autoload]" not in exported
    assert "[editor_plugins]" not in exported
    assert "enabled=" not in exported
'''


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


def _eol(p: Path) -> str:
    return "\r\n" if b"\r\n" in p.read_bytes() else "\n"


EDITS = [(EXPORT, "export.py writes the cap", E1_OLD, E1_NEW),
         (PREVIEW, "walk_preview writes the same cap", E2_OLD, E2_NEW)]


def _require() -> None:
    missing = [str(p) for p in TOUCHED if not p.is_file()]
    if missing:
        sys.exit("REFUSING: not found:\n  " + "\n  ".join(missing))


def _plan(texts: dict) -> tuple[dict, list]:
    notes = []
    for path, label, old, new in EDITS:
        t = texts[path]
        n = t.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times in "
                f"{path.name}, expected 1.")
        texts[path] = t.replace(old, new, 1)
        notes.append(f"  ok  {label}")
    return texts, notes


def cmd_check() -> int:
    _require()
    for p in TOUCHED:
        print("   ", _stamp(p))
    if "max_lights_per_object" in EXPORT.read_text(encoding="utf-8"):
        print("\nALREADY APPLIED.")
        return 0
    _, notes = _plan({p: p.read_text(encoding="utf-8") for p in (EXPORT, PREVIEW)})
    print()
    print("\n".join(notes))
    print(f"\nVERSION {VERSION.read_text(encoding='utf-8').strip()} -> {NEW_VERSION}")
    print(f"NEW FILE {TEST.relative_to(ROOT)}")
    return 0


def cmd_apply() -> int:
    _require()
    if "max_lights_per_object" in EXPORT.read_text(encoding="utf-8"):
        print("ALREADY APPLIED; nothing to do.")
        return 0
    ver = VERSION.read_text(encoding="utf-8").strip()
    if ver == NEW_VERSION:
        raise SystemExit(f"REFUSING: VERSION already {NEW_VERSION}")
    log = CHANGELOG.read_text(encoding="utf-8")
    if f"[{NEW_VERSION}]" in log:
        raise SystemExit(f"REFUSING: CHANGELOG already has [{NEW_VERSION}]")

    texts, notes = _plan({p: p.read_text(encoding="utf-8") for p in (EXPORT, PREVIEW)})

    for p in TOUCHED:
        (p.parent / f"{p.name}.{TAG}").write_bytes(p.read_bytes())
    for p, t in texts.items():
        e = _eol(p)
        p.write_text(t if e == "\n" else t.replace("\n", "\r\n"),
                     encoding="utf-8", newline="")
    tail = "\n" if b"\n" in VERSION.read_bytes() else ""
    VERSION.write_text(NEW_VERSION + tail, encoding="utf-8", newline="")
    ec = _eol(CHANGELOG)
    entry = CHANGELOG_ENTRY if ec == "\n" else CHANGELOG_ENTRY.replace("\n", "\r\n")
    CHANGELOG.write_text(entry + log, encoding="utf-8", newline="")
    TEST.parent.mkdir(parents=True, exist_ok=True)
    TEST.write_text(TEST_SOURCE, encoding="utf-8", newline="")

    print("\n".join(notes))
    print(f"  ok  VERSION {ver} -> {NEW_VERSION}")
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
        s = p.parent / f"{p.name}.{TAG}"
        if s.is_file():
            p.write_bytes(s.read_bytes()); s.unlink()
            print(f"  restored {p.name}"); n += 1
    if TEST.is_file():
        TEST.unlink(); print(f"  removed {TEST.name}"); n += 1
    if not n:
        print("nothing to revert.")
    return 0


def _pytest(args):
    return subprocess.run([sys.executable, "-m", "pytest"] + args,
                          cwd=str(LF), capture_output=True, text=True)


def _falsify(name, path, mutate):
    orig = path.read_bytes()
    try:
        path.write_bytes(mutate(orig.decode("utf-8")).encode("utf-8"))
        r = _pytest([str(TEST.relative_to(LF))])
        if r.returncode == 0:
            raise SystemExit(f"SELFTEST FAILED: mutation '{name}' did not fail "
                             f"the tests.\n" + r.stdout[-2000:])
        if r.returncode == 5:
            raise SystemExit(f"SELFTEST FAILED: '{name}' collected NOTHING "
                             f"(rc=5), which is a failure.\n" + r.stdout[-2000:])
        print(f"  ok  falsified: {name}  (rc={r.returncode})")
    finally:
        path.write_bytes(orig)


def cmd_selftest() -> int:
    _require()
    if "max_lights_per_object" not in EXPORT.read_text(encoding="utf-8"):
        raise SystemExit("SELFTEST: patch is not applied.")
    if not TEST.is_file():
        raise SystemExit(f"SELFTEST: {TEST} missing.")

    r = _pytest([str(TEST.relative_to(LF))])
    if r.returncode != 0:
        raise SystemExit("SELFTEST FAILED: new tests do not pass.\n"
                         + r.stdout[-3000:])
    print("  ok  new tests pass (rc=0)")

    _falsify("the preview loses the cap (the exact 2026-08-12 drift)", PREVIEW,
             lambda t: t.replace("limits/opengl/max_lights_per_object=64\n", ""))
    _falsify("the preview loses the debug block", PREVIEW,
             lambda t: t.replace("gdscript/warnings/inference_on_variant=1\n", ""))
    _falsify("the export caps too low", EXPORT,
             lambda t: t.replace("max_lights_per_object=64", "max_lights_per_object=8"))
    _falsify("the cap line is emitted twice", EXPORT,
             lambda s: s.replace(
                 '        "limits/opengl/max_lights_per_object=64\\n\\n"\n',
                 '        "limits/opengl/max_lights_per_object=64\\n"\n'
                 '        "limits/opengl/max_lights_per_object=64\\n\\n"\n'))
    _falsify("an autoload is smuggled into the package", EXPORT,
             lambda t: t.replace('"[debug]\\n"', '"[autoload]\\nX=1\\n\\n[debug]\\n"'))

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
