#!/usr/bin/env python3
"""level_factory 0.43.3 -- the per-object cap is needed after all, and 40 is why.

0.43.2 removed `limits/opengl/max_lights_per_object` and said it "was never the
binding constraint". That was true of the symptom I had tested -- blinking --
and false of the one I had not. Standing still in an interior, adjacent floor
slabs each select their own lights and meet at a HARD BRIGHTNESS STEP. Same
limit, no camera motion, and it would have shipped.

MEASURED IN THE WALK PREVIEW, 2026-08-18, one room, three runs:

    per-object  8 (engine default)   a hard cut across the floor
    per-object 64                    seam gone, no blinking
    per-object 40                    seam gone, no blinking

40 rather than 64 because the value sizes the shader light loop for EVERY
object, so the smallest sufficient number is the right one -- and 40 is the
smallest the data supports: the worst mesh measured across all five buildings
sees 36 lights (`pvp_station_ref`'s roof).

BOTH CAPS ARE NOW DERIVED, NEITHER IS ROUND:

    max_renderable_lights = the package's own light count
        A package cannot render more lights than it contains. Exact upper
        bound, no headroom to pay for.

    max_lights_per_object = min(light count, 40)
        Also bounded by the package: a 20-light package cannot put more than
        20 on one mesh, so it gets 20, not 40. 40 is the measured ceiling and
        is the first number to raise if a denser mission shows seams.

Below the engine defaults, neither line is written and the package pays
nothing.

AND THE SEAM IS EVIDENCE FOR ROADMAP 54, NOT AGAINST IT. It exists because one
floor mesh spans a whole room. Room-sized meshes would each sit inside the
engine default and need no cap at all. This is a mitigation with a stated cost,
and the geometry is still the fix.

Usage:
    pwsh> python patch_lf_0433.py --check
    pwsh> python patch_lf_0433.py
    pwsh> python patch_lf_0433.py --selftest
    pwsh> python patch_lf_0433.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LF = ROOT / "level_factory"
SHARED = LF / "packages" / "core" / "godot_project.py"
TEST = LF / "tests" / "unit" / "test_project_godot_agreement.py"
VERSION = LF / "VERSION"
CHANGELOG = LF / "CHANGELOG.md"

TAG = "pre_0433"
NEW_VERSION = "0.43.3"
TOUCHED = [SHARED, TEST, VERSION, CHANGELOG]

SHARED_SOURCE = '''"""The `[rendering]` block of a generated project.godot -- one rule, two callers.

`export.py` writes the shipped package's project.godot and `walk_preview.py`
writes the dev preview's, and the preview's own comment says they must not
drift: "Two projects disagreeing about what a complete project.godot contains
is how a human signs off lighting that was missing a rig." Two hand-kept copies
is how that happens, so there is one function here and two importers -- the
same shape `packages.core.hashing` already has for scene payloads.

THE TWO LIGHT LIMITS, AND WHAT EACH ONE ACTUALLY DOES.

GL Compatibility carries two, they fail differently, and this file has been
wrong about them once already:

    rendering/limits/opengl/max_renderable_lights   default 32
        A GLOBAL budget. Above it, lights are simply not drawn -- so on a
        136-light package most were not, and whole areas stayed dark
        PERMANENTLY while which ones won changed as the camera moved.

    rendering/limits/opengl/max_lights_per_object   default 8
        A PER-MESH budget. Above it, a mesh drops lights. On building-sized
        floor and ceiling slabs this shows up standing still, as a hard
        brightness STEP where two slabs meet -- not as blinking.

level_factory 0.43.0 set the per-object cap and named it as the cause of the
blinking; it was not. 0.43.2 then removed it, having tested only for blinking,
and that reintroduced the seam. Measured in the walk preview, one interior,
three runs: default 8 -> hard cut across the floor; 64 -> gone; 40 -> gone.

BOTH VALUES ARE DERIVED FROM THE PACKAGE. Neither is a round number picked to
make a symptom go away:

  * The global cap is the package's own light count, counted by globbing the
    scenes (`closure.py`'s approach). A package cannot render more lights than
    it contains, so its total is a true upper bound -- sufficient by
    construction, with no headroom to pay for.

  * The per-object cap is `min(light count, PER_OBJECT_CEILING)`. Also bounded
    by the package: a 20-light package cannot put more than 20 on one mesh and
    gets 20. The ceiling is the measured worst case across lot_demo_001's five
    buildings -- one mesh at 36 lights -- plus a small margin.

Below the engine defaults neither line is written, and an unlit package carries
no rendering override at all.

THE PER-OBJECT CAP COSTS SOMETHING. It sizes the light loop in the shader for
every object, so the smallest sufficient value is the correct one, and this is
a MITIGATION. The seam only exists because a single floor mesh spans a whole
room; room-sized meshes would sit inside the engine default and need no cap.
That is roadmap 54, and it is the actual fix.
"""
from __future__ import annotations

import re
from pathlib import Path

# Every node type that consumes a slot in the light budgets.
_LIGHT_TYPES = ("OmniLight3D", "SpotLight3D", "DirectionalLight3D")

#: The engine's own defaults. At or below these, a package needs no override.
ENGINE_DEFAULT_RENDERABLE_LIGHTS = 32
ENGINE_DEFAULT_LIGHTS_PER_OBJECT = 8

#: Measured ceiling for the per-mesh cap. The worst mesh across lot_demo_001's
#: five buildings sees 36 lights (pvp_station_ref's roof); 40 leaves margin and
#: was confirmed seam-free in the walk preview. RAISE THIS FIRST if a denser
#: mission shows a brightness step between adjacent slabs.
PER_OBJECT_CEILING = 40

_LIGHT_RE = re.compile(r'type="(?:' + "|".join(_LIGHT_TYPES) + r')"')


def count_package_lights(root: Path) -> int:
    """Light nodes across every `.tscn` under `root`.

    Globbed, not walked: a scene-graph traversal would need every instanced
    sub-scene resolved, and this only has to be an upper bound.
    """
    total = 0
    for scene in sorted(Path(root).rglob("*.tscn")):
        try:
            text = scene.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        total += len(_LIGHT_RE.findall(text))
    return total


def per_object_cap(light_count: int) -> int:
    """The per-mesh cap this package needs, bounded by what it contains."""
    return min(light_count, PER_OBJECT_CEILING)


def rendering_block(light_count: int) -> str:
    """The `[rendering]` section, ending with a blank line.

    Each cap is written only when the package exceeds the engine's own default
    for it, so a small or unlit package carries no override.
    """
    out = ['[rendering]', 'renderer/rendering_method="gl_compatibility"']

    if light_count > ENGINE_DEFAULT_RENDERABLE_LIGHTS:
        out += [
            "; RENDERABLE-LIGHTS BUDGET -- a GLOBAL cap, engine default 32.",
            "; Above it lights are not drawn at all, so on a package this size",
            f"; most were not: measured on lot_demo_001 2026-08-18 with {light_count}",
            "; lights as areas that stay dark permanently, plus blinking as",
            "; which lights win changes with the camera. The value is this",
            "; package's own light count -- a true upper bound, sufficient by",
            "; construction, with no headroom to pay for.",
            f"limits/opengl/max_renderable_lights={light_count}",
        ]

    cap = per_object_cap(light_count)
    if cap > ENGINE_DEFAULT_LIGHTS_PER_OBJECT:
        out += [
            "; PER-MESH BUDGET -- engine default 8. A mesh over it drops",
            "; lights, and on building-sized floor and ceiling slabs that shows",
            "; STANDING STILL, as a hard brightness step where two slabs meet.",
            "; 0.43.2 removed this cap having tested only for blinking, and the",
            "; seam came back. Measured in the walk preview, one interior:",
            "; default 8 -> hard cut; 64 -> gone; 40 -> gone. The worst mesh",
            "; across five buildings sees 36 lights, so 40 is the smallest",
            "; value the data supports -- and this one COSTS: it sizes the",
            "; shader light loop for every object. It is a mitigation; the fix",
            "; is that one mesh should not span a room. Roadmap 54.",
            f"limits/opengl/max_lights_per_object={cap}",
        ]

    return "\\n".join(out) + "\\n\\n"
'''

TEST_SOURCE = '''"""Both light caps are derived from the package, and neither is a round number.

`walk_preview._PROJECT` says the two project.godot writers "must stay verbatim"
and gives the cost of drift: "Two projects disagreeing about what a complete
project.godot contains is how a human signs off lighting that was missing a
rig." 0.43.2 removed the possibility by giving both one shared `rendering_block`;
these tests hold the rest.

The caps have been wrong in both directions inside one day -- 0.43.0 wrote the
per-object cap for the wrong reason, 0.43.2 removed it for a reason that only
covered half the symptoms -- so each property below is pinned rather than left
to a comment.

Run:  python -m pytest tests/unit/test_project_godot_agreement.py
"""
import pytest

from packages.core.godot_project import (ENGINE_DEFAULT_LIGHTS_PER_OBJECT,
                                         ENGINE_DEFAULT_RENDERABLE_LIGHTS,
                                         PER_OBJECT_CEILING,
                                         count_package_lights, rendering_block)
from packages.exporting.export import _write_project_godot
from packages.preview.walk_preview import _PROJECT

_SCENE = '[gd_scene format=3]\\n[node name="R" type="Node3D"]\\n'
_LIGHT = '[node name="L{i}" type="OmniLight3D" parent="."]\\n'


def _package(root, lights: int):
    (root / "presentation").mkdir(parents=True, exist_ok=True)
    (root / "presentation" / "lit.tscn").write_text(
        _SCENE + "".join(_LIGHT.format(i=i) for i in range(lights)),
        encoding="utf-8")
    return root


def _settings(text: str, section: str) -> dict:
    out, cur = {}, None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            cur = s[1:-1]; continue
        if not s or s.startswith(";") or "=" not in s:
            continue
        if cur == section:
            k, v = s.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def _exported(tmp_path, lights):
    _package(tmp_path, lights)
    _write_project_godot(tmp_path, "mission.tscn", "m")
    return (tmp_path / "project.godot").read_text(encoding="utf-8")


def _preview(tmp_path, lights):
    _package(tmp_path, lights)
    return _PROJECT.format(name="m", level="mission.tscn",
                           rendering=rendering_block(count_package_lights(tmp_path)))


# --- the count is real -----------------------------------------------------

def test_the_counter_sees_lights_in_the_package(tmp_path):
    _package(tmp_path, 7)
    assert count_package_lights(tmp_path) == 7


def test_the_counter_is_zero_on_an_unlit_package(tmp_path):
    (tmp_path / "a.tscn").write_text(_SCENE, encoding="utf-8")
    assert count_package_lights(tmp_path) == 0


# --- nothing is written until it is earned --------------------------------

def test_an_unlit_package_carries_no_cap_at_all(tmp_path):
    t = _exported(tmp_path, 0)
    assert "max_renderable_lights" not in t
    assert "max_lights_per_object" not in t


def test_a_small_package_carries_neither_cap(tmp_path):
    """8 lights cannot exceed either engine default, so it pays nothing."""
    t = _exported(tmp_path, ENGINE_DEFAULT_LIGHTS_PER_OBJECT)
    assert "max_renderable_lights" not in t
    assert "max_lights_per_object" not in t


# --- the global cap is the package's own count ----------------------------

def test_the_global_cap_is_the_exact_light_count(tmp_path):
    n = ENGINE_DEFAULT_RENDERABLE_LIGHTS + 9
    v = _settings(_exported(tmp_path, n), "rendering")["limits/opengl/max_renderable_lights"]
    assert int(v) == n


# --- the per-object cap is bounded BOTH ways ------------------------------

def test_the_per_object_cap_is_bounded_by_the_measured_ceiling(tmp_path):
    """A 136-light package gets the ceiling, not 136: the value sizes the
    shader light loop for every object, so it must not track the count up."""
    v = _settings(_exported(tmp_path, 136), "rendering")["limits/opengl/max_lights_per_object"]
    assert int(v) == PER_OBJECT_CEILING


def test_the_per_object_cap_is_bounded_by_the_package_too(tmp_path):
    """A 20-light package cannot put more than 20 on one mesh, so it gets 20
    rather than paying for the ceiling."""
    n = 20
    assert n < PER_OBJECT_CEILING
    v = _settings(_exported(tmp_path, n), "rendering")["limits/opengl/max_lights_per_object"]
    assert int(v) == n


def test_the_ceiling_covers_the_worst_measured_mesh():
    """36 lights on pvp_station_ref's roof, measured 2026-08-18. If this
    ceiling ever drops below that, the seam this cap exists for comes back."""
    assert PER_OBJECT_CEILING >= 36


# --- and the two writers still agree --------------------------------------

@pytest.mark.parametrize("lights", [0, 40, 136])
@pytest.mark.parametrize("section", ["rendering", "debug"])
def test_every_exported_setting_appears_in_the_preview(section, lights, tmp_path):
    e = _settings(_exported(tmp_path, lights), section)
    p = _settings(_preview(tmp_path, lights), section)
    missing = {k: v for k, v in e.items() if p.get(k) != v}
    assert missing == {}, f"[{section}] drifted: {missing} (preview has {p})"


def test_the_sections_being_compared_are_not_empty(tmp_path):
    t = _exported(tmp_path, 0)
    assert _settings(t, "rendering"), "no [rendering] settings parsed"
    assert _settings(t, "debug"), "no [debug] settings parsed"


@pytest.mark.parametrize("which", ["exported", "preview"])
def test_no_setting_is_written_twice(which, tmp_path):
    """`_settings` returns a dict, so a duplicated line is invisible to every
    other test here. 0.43.0's first draft emitted its cap twice and the suite
    stayed green. Read the LINES."""
    text = _exported(tmp_path, 136) if which == "exported" else _preview(tmp_path, 136)
    keys = [l.split("=", 1)[0].strip() for l in text.splitlines()
            if "=" in l and not l.strip().startswith((";", "["))]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    assert dupes == [], f"{which} writes these more than once: {dupes}"


def test_the_package_stays_plugin_free_and_autoload_free(tmp_path):
    t = _exported(tmp_path, 136)
    assert "[autoload]" not in t
    assert "[editor_plugins]" not in t
    assert "enabled=" not in t
'''

CHANGELOG_ENTRY = """## [0.43.3] - the per-object cap is needed after all, and 40 is why

0.43.2 removed `limits/opengl/max_lights_per_object` on the grounds that it
"was never the binding constraint". True of the symptom that had been tested --
blinking -- and false of the one that had not. Standing still in an interior,
adjacent floor slabs each select their own lights and meet at a HARD BRIGHTNESS
STEP. Same limit, no camera motion, and it would have shipped.

Measured in the walk preview, one room, three runs:

    per-object  8 (engine default)   a hard cut across the floor
    per-object 64                    seam gone, no blinking
    per-object 40                    seam gone, no blinking

40 rather than 64 because that value sizes the shader light loop for EVERY
object, so the smallest sufficient number is the correct one -- and 40 is the
smallest the data supports. The worst mesh measured across lot_demo_001's five
buildings sees 36 lights (`pvp_station_ref`'s roof).

BOTH CAPS ARE NOW DERIVED FROM THE PACKAGE

    max_renderable_lights  = light count
    max_lights_per_object  = min(light count, 40)

The second bound matters: a 20-light package cannot put more than 20 lights on
one mesh, so it gets 20 rather than paying for the ceiling. Below the engine
defaults -- 32 and 8 -- neither line is written and an unlit package carries no
rendering override at all.

THE SEAM IS EVIDENCE FOR ROADMAP 54, NOT AGAINST IT

It exists because one floor mesh spans a whole room. Room-sized meshes would
each sit inside the engine default and need no cap. This release ships a
mitigation with a stated cost; the geometry is still the fix.

THE PROCESS NOTE. Three releases in a row set this cap on an unisolated
mechanism -- 0.43.0 wrote it for blinking (wrong), 0.43.2 removed it having
tested only blinking (wrong the other way), 0.43.3 tested both symptoms
separately. The tests now pin each property rather than leaving it to a
comment, because a comment is what was wrong twice.

"""


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


def _eol(p: Path) -> str:
    return "\r\n" if b"\r\n" in p.read_bytes() else "\n"


def _require() -> None:
    missing = [str(p) for p in TOUCHED if not p.is_file()]
    if missing:
        sys.exit("REFUSING: not found (is 0.43.2 applied?):\n  "
                 + "\n  ".join(missing))
    if "PER_OBJECT_CEILING" in SHARED.read_text(encoding="utf-8"):
        return


def cmd_check() -> int:
    _require()
    for p in TOUCHED:
        print("   ", _stamp(p))
    if "PER_OBJECT_CEILING" in SHARED.read_text(encoding="utf-8"):
        print("\nALREADY APPLIED.")
        return 0
    print(f"\n  ok  REWRITE {SHARED.relative_to(ROOT)}  (per-object cap returns at 40)")
    print(f"  ok  REWRITE {TEST.relative_to(ROOT)}")
    print(f"\nVERSION {VERSION.read_text(encoding='utf-8').strip()} -> {NEW_VERSION}")
    return 0


def cmd_apply() -> int:
    _require()
    if "PER_OBJECT_CEILING" in SHARED.read_text(encoding="utf-8"):
        print("ALREADY APPLIED; nothing to do.")
        return 0
    ver = VERSION.read_text(encoding="utf-8").strip()
    log = CHANGELOG.read_text(encoding="utf-8")
    if f"[{NEW_VERSION}]" in log:
        raise SystemExit(f"REFUSING: CHANGELOG already has [{NEW_VERSION}]")

    for p in TOUCHED:
        (p.parent / f"{p.name}.{TAG}").write_bytes(p.read_bytes())
    SHARED.write_text(SHARED_SOURCE, encoding="utf-8", newline="")
    TEST.write_text(TEST_SOURCE, encoding="utf-8", newline="")
    tail = "\n" if b"\n" in VERSION.read_bytes() else ""
    VERSION.write_text(NEW_VERSION + tail, encoding="utf-8", newline="")
    ec = _eol(CHANGELOG)
    entry = CHANGELOG_ENTRY if ec == "\n" else CHANGELOG_ENTRY.replace("\n", "\r\n")
    CHANGELOG.write_text(entry + log, encoding="utf-8", newline="")

    print(f"  ok  rewrote {SHARED.relative_to(ROOT)}")
    print(f"  ok  rewrote {TEST.relative_to(ROOT)}")
    print(f"  ok  VERSION {ver} -> {NEW_VERSION}")
    print("\nafter:")
    for p in TOUCHED:
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
    if not n:
        print("nothing to revert.")
    return 0


def _pytest(args):
    return subprocess.run([sys.executable, "-m", "pytest"] + args,
                          cwd=str(LF), capture_output=True, text=True)


def _falsify(name, mutate):
    orig = SHARED.read_bytes()
    try:
        SHARED.write_bytes(mutate(orig.decode("utf-8")).encode("utf-8"))
        r = _pytest([str(TEST.relative_to(LF))])
        if r.returncode == 0:
            raise SystemExit(f"SELFTEST FAILED: '{name}' did not fail.\n"
                             + r.stdout[-2000:])
        if r.returncode == 5:
            raise SystemExit(f"SELFTEST FAILED: '{name}' collected NOTHING")
        print(f"  ok  falsified: {name}  (rc={r.returncode})")
    finally:
        SHARED.write_bytes(orig)


def cmd_selftest() -> int:
    _require()
    r = _pytest([str(TEST.relative_to(LF))])
    if r.returncode != 0:
        raise SystemExit("SELFTEST FAILED: new tests do not pass.\n"
                         + r.stdout[-3000:])
    print("  ok  new tests pass (rc=0)")

    _falsify("the per-object cap is removed again (0.43.2's mistake)",
             lambda t: t.replace("    cap = per_object_cap(light_count)",
                                 "    cap = 0"))
    _falsify("the ceiling drops below the measured worst mesh",
             lambda t: t.replace("PER_OBJECT_CEILING = 40",
                                 "PER_OBJECT_CEILING = 32"))
    _falsify("the per-object cap tracks the light count upward",
             lambda t: t.replace("return min(light_count, PER_OBJECT_CEILING)",
                                 "return light_count"))
    _falsify("a small package is charged for a cap it cannot need",
             lambda t: t.replace("if cap > ENGINE_DEFAULT_LIGHTS_PER_OBJECT:",
                                 "if True:"))

    r = _pytest([])
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if r.returncode == 5:
        raise SystemExit("SELFTEST FAILED: full suite collected NOTHING")
    if r.returncode != 0:
        raise SystemExit(f"SELFTEST FAILED: full suite rc={r.returncode}\n"
                         + r.stdout[-4000:])
    print(f"  ok  FULL SUITE GREEN :: {lines[-1] if lines else '(no summary)'}")
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
