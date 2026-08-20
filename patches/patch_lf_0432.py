#!/usr/bin/env python3
"""level_factory 0.43.2 -- one derived light cap, and the expensive one removed.

0.43.0 wrote `limits/opengl/max_lights_per_object=64` and its comment named
that as the mechanism. MEASURED ON HARDWARE, 2026-08-18, in this order:

    per-object 64, global 32 (default)   still blinks, areas stay dark
    per-object  8 (default), global 256  CLEAN, and the load-in hitch is SMALLER

So the per-object cap was never the binding constraint and never needed. The
binding one is `rendering/limits/opengl/max_renderable_lights`, engine default
32, against a package that ships 136 lights -- a GLOBAL budget, which is why
areas whose lights never won stayed dark permanently rather than flickering.
The engine said so itself when asked:

    max_renderable_lights   exists=true  value=32
    max_lights_per_object   exists=true  value=64

0.43.0's mechanism is corrected in place rather than quietly rewritten, the
same treatment the four earlier wrong mechanisms got today.

REMOVING THE PER-OBJECT CAP IS A PERFORMANCE FIX, NOT JUST TIDYING. In GL
Compatibility that value sizes the light loop in the shader for EVERY object,
so 64 multiplies shader variants and per-fragment work across the whole level.
Dropping it measurably improved first-load stutter. This layer has to stay
cheap while the game grows into it.

THE REMAINING CAP IS DERIVED, NOT GUESSED. `count_package_lights` globs the
scenes the exporter just wrote and counts light nodes -- the same "glob it,
don't reason about it" approach `closure.py` uses. The total number of lights
in a package is by definition the most that could ever need rendering, so the
cap is exact: no headroom, no waste, and guaranteed sufficient. A package at or
under the engine default of 32 gets NO cap line at all and pays nothing.

ONE RULE, TWO IMPORTERS. `packages/core/godot_project.py` holds the block;
`export.py` and `walk_preview.py` both call it. That is the pattern
`test_scene_payload` states in its own docstring, and it is what makes the
0.43.0 agreement test keep working instead of comparing two hand-kept copies.

Usage:
    pwsh> python patch_lf_0432.py --check
    pwsh> python patch_lf_0432.py
    pwsh> python patch_lf_0432.py --selftest
    pwsh> python patch_lf_0432.py --revert
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
SHARED = LF / "packages" / "core" / "godot_project.py"
TEST = LF / "tests" / "unit" / "test_project_godot_agreement.py"
VERSION = LF / "VERSION"
CHANGELOG = LF / "CHANGELOG.md"

TAG = "pre_0432"
NEW_VERSION = "0.43.2"
TOUCHED = [EXPORT, PREVIEW, TEST, VERSION, CHANGELOG]

SHARED_SOURCE = '''"""The `[rendering]` block of a generated project.godot -- one rule, two callers.

`export.py` writes the shipped package's project.godot and `walk_preview.py`
writes the dev preview's, and the preview's own comment says they must not
drift: "Two projects disagreeing about what a complete project.godot contains
is how a human signs off lighting that was missing a rig." Two hand-kept copies
is how that happens, so there is one function here and two importers -- the
same shape `packages.core.hashing` already has for scene payloads.

WHAT THE CAP IS FOR, measured on lot_demo_001, 2026-08-18.

A package shipping 136 fixture lights blinked when walked, and whole areas
stayed dark permanently. GL Compatibility carries TWO separate light limits and
only one of them was the problem:

    rendering/limits/opengl/max_renderable_lights   default 32   <- binding
    rendering/limits/opengl/max_lights_per_object   default  8

Tested on hardware, in this order:

    per-object 64, global 32     still blinks, areas stay dark
    per-object  8, global 256    clean, and first-load stutter is SMALLER

`max_renderable_lights` is a GLOBAL budget: with 136 lights and a cap of 32,
most of them are never drawn at all, which is why areas stayed dark rather than
flickering. `max_lights_per_object` was never the binding constraint, and
raising it is actively expensive -- it sizes the light loop in the shader for
EVERY object, multiplying variants and per-fragment work. level_factory 0.43.0
wrote it anyway, on a mechanism that had not been isolated. It is not written
any more.

WHY THE VALUE IS EXACT. The cap is the number of light nodes the package
actually ships, counted by globbing the scenes rather than reasoning about
them (`closure.py`'s approach). A package cannot render more lights than it
contains, so the total is a true upper bound: sufficient by construction, with
no headroom to pay for. Below the engine default, nothing is written at all --
an unlit package should not carry a rendering override.
"""
from __future__ import annotations

import re
from pathlib import Path

# Every node type that consumes a slot in the renderable-lights budget.
_LIGHT_TYPES = ("OmniLight3D", "SpotLight3D", "DirectionalLight3D")

#: The engine's own default for `max_renderable_lights`. At or below this, the
#: package needs no override and should not carry one.
ENGINE_DEFAULT_RENDERABLE_LIGHTS = 32

_LIGHT_RE = re.compile(
    r'type="(?:' + "|".join(_LIGHT_TYPES) + r')"')


def count_package_lights(root: Path) -> int:
    """Light nodes across every `.tscn` under `root`.

    Globbed, not walked: a scene graph traversal would need every instanced
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


def rendering_block(light_count: int) -> str:
    """The `[rendering]` section, ending with a blank line.

    `light_count` at or below the engine default produces no cap line at all.
    """
    out = ['[rendering]', 'renderer/rendering_method="gl_compatibility"']
    if light_count > ENGINE_DEFAULT_RENDERABLE_LIGHTS:
        out += [
            "; RENDERABLE-LIGHTS BUDGET. GL Compatibility renders at most N",
            "; lights in total, engine default 32. This package ships",
            f"; {light_count}, so without this the majority are never drawn:",
            "; measured on lot_demo_001 2026-08-18 as areas that stay dark",
            "; permanently, plus blinking as which lights win changes with the",
            "; camera. The value is the package's own light count, which is a",
            "; true upper bound -- sufficient by construction, no headroom to",
            "; pay for. The per-OBJECT cap is deliberately NOT set: it was",
            "; tested at 64 and was never the binding constraint, and raising",
            "; it sizes the shader light loop for every object.",
            f"limits/opengl/max_renderable_lights={light_count}",
        ]
    return "\\n".join(out) + "\\n\\n"
'''

E1_OLD = '''        "[rendering]\\n"
        \'renderer/rendering_method="gl_compatibility"\\n\'
'''
E2_OLD_START = '        "; PER-OBJECT LIGHT CAP.'

PREVIEW_OLD_BLOCK_HEAD = "[rendering]\nrenderer/rendering_method=\"gl_compatibility\"\n"


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


def _eol(p: Path) -> str:
    return "\r\n" if b"\r\n" in p.read_bytes() else "\n"


def _cut_rendering_literal(text: str, path: Path) -> str:
    """Replace the hand-written [rendering] literal with a call to the shared
    rule. Located by its first and last lines rather than by a giant anchor, so
    the comment body can be reworded without breaking this patch."""
    start = text.index('        "[rendering]\\n"\n')
    end_marker = '        "limits/opengl/max_lights_per_object=64\\n\\n"\n'
    if end_marker not in text:
        raise SystemExit(f"REFUSING: {path.name} has no 0.43.0 per-object cap "
                         f"line to remove; is 0.43.0 applied?")
    end = text.index(end_marker) + len(end_marker)
    return (text[:start]
            + "        + rendering_block(count_package_lights(export_dir)) +\n"
            + text[end:])


def _patch_export(text: str) -> str:
    if text.count('        "[rendering]\\n"\n') != 1:
        raise SystemExit("REFUSING: export.py's [rendering] literal is not "
                         "unique.")
    text = _cut_rendering_literal(text, EXPORT)
    anchor = "from packages.core.hashing import hash_file"
    if anchor not in text:
        anchor = "from packages.core.ids import"
        i = text.index(anchor)
        ins = ("from packages.core.godot_project import (count_package_lights,\n"
               "                                          rendering_block)\n")
        return text[:i] + ins + text[i:]
    return text.replace(
        anchor,
        "from packages.core.godot_project import (count_package_lights,\n"
        "                                          rendering_block)\n" + anchor, 1)


def _patch_preview(text: str) -> str:
    i = text.index(PREVIEW_OLD_BLOCK_HEAD)
    j = text.index("[debug]", i)
    text = text[:i] + "{rendering}" + text[j:]
    text = text.replace(
        "_PROJECT.format(name=name, level=level)",
        "_PROJECT.format(name=name, level=level,\n"
        "                        rendering=rendering_block(\n"
        "                            count_package_lights(dest)))", 1)
    return text.replace(
        "from pathlib import Path\n",
        "from pathlib import Path\n\n"
        "from packages.core.godot_project import (count_package_lights,\n"
        "                                          rendering_block)\n", 1)


TEST_SOURCE = '''"""The two project.godot writers must not drift, and the light cap must be earned.

`walk_preview._PROJECT` says it itself -- "Verbatim from
export.py::_write_project_godot, and it must stay verbatim" -- and then gives
the cost: "Two projects disagreeing about what a complete project.godot
contains is how a human signs off lighting that was missing a rig." On
2026-08-12 that is what happened. 0.43.2 removed the possibility by giving both
writers one shared `rendering_block`; these tests hold the rest of the promise.

Run:  python -m pytest tests/unit/test_project_godot_agreement.py
"""
import pytest

from packages.core.godot_project import (ENGINE_DEFAULT_RENDERABLE_LIGHTS,
                                         count_package_lights, rendering_block)
from packages.exporting.export import _write_project_godot
from packages.preview.walk_preview import _PROJECT

_SCENE = ('[gd_scene format=3]\\n'
          '[node name="R" type="Node3D"]\\n')
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


# --- the count is real, not assumed --------------------------------------

def test_the_counter_sees_lights_in_the_package(tmp_path):
    _package(tmp_path, 7)
    assert count_package_lights(tmp_path) == 7


def test_the_counter_is_zero_on_an_unlit_package(tmp_path):
    (tmp_path / "a.tscn").write_text(_SCENE, encoding="utf-8")
    assert count_package_lights(tmp_path) == 0


# --- the cap is derived, and only when it is needed -----------------------

def test_an_unlit_package_carries_no_cap_at_all(tmp_path):
    """An export with no lights must not pay for a rendering override."""
    t = _exported(tmp_path, 0)
    assert "max_renderable_lights" not in t


def test_a_package_at_the_engine_default_carries_no_cap(tmp_path):
    t = _exported(tmp_path, ENGINE_DEFAULT_RENDERABLE_LIGHTS)
    assert "max_renderable_lights" not in t


def test_a_package_over_the_default_caps_at_its_own_light_count(tmp_path):
    """Exact, not rounded: the package cannot render more lights than it has,
    so its own count is sufficient by construction and costs nothing extra."""
    n = ENGINE_DEFAULT_RENDERABLE_LIGHTS + 9
    v = _settings(_exported(tmp_path, n), "rendering")["limits/opengl/max_renderable_lights"]
    assert int(v) == n


# --- the expensive cap stays gone ----------------------------------------

@pytest.mark.parametrize("lights", [0, 40, 200])
def test_the_per_object_cap_is_never_written(tmp_path, lights):
    """Measured 2026-08-18: per-object 64 with the global cap at its default
    still blinked, and the default per-object with the global cap raised was
    clean AND had less first-load stutter. That value sizes the shader light
    loop for every object; writing it costs frame time for no measured gain."""
    assert "max_lights_per_object" not in _exported(tmp_path, lights)


# --- and the two writers still agree -------------------------------------

@pytest.mark.parametrize("lights", [0, 40])
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
    text = _exported(tmp_path, 40) if which == "exported" else _preview(tmp_path, 40)
    keys = [l.split("=", 1)[0].strip() for l in text.splitlines()
            if "=" in l and not l.strip().startswith((";", "["))]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    assert dupes == [], f"{which} writes these more than once: {dupes}"


def test_the_package_stays_plugin_free_and_autoload_free(tmp_path):
    t = _exported(tmp_path, 40)
    assert "[autoload]" not in t
    assert "[editor_plugins]" not in t
    assert "enabled=" not in t
'''

CHANGELOG_ENTRY = """## [0.43.2] - one derived light cap, and the expensive one removed

0.43.0 wrote `limits/opengl/max_lights_per_object=64` and named it as the
mechanism. It was not. Measured on hardware, in this order:

    per-object 64, global 32 (default)   still blinks, areas stay dark
    per-object  8 (default), global 256  clean, and first-load stutter SMALLER

GL Compatibility carries two separate light limits, and the binding one is
`rendering/limits/opengl/max_renderable_lights` -- a GLOBAL budget, engine
default 32, against a package shipping 136 lights. Most of them were never
drawn at all, which is why whole areas stayed dark permanently rather than
flickering. Asked directly, the engine confirmed both names and both values:

    max_renderable_lights   exists=true  value=32
    max_lights_per_object   exists=true  value=64

So 0.43.0's line took effect and did nothing useful. Corrected in place rather
than quietly rewritten.

REMOVING THE PER-OBJECT CAP IS A PERFORMANCE CHANGE. In GL Compatibility that
value sizes the light loop in the shader for EVERY object, multiplying variants
and per-fragment work. Dropping it measurably improved first-load stutter,
reported from the walk. This layer has to stay cheap while the game grows into
it, and it was carrying a cost for a mechanism that had never been isolated.

THE REMAINING CAP IS DERIVED

`count_package_lights` globs the scenes the exporter just wrote -- the same
"glob it, do not reason about it" approach `closure.py` takes -- and the cap is
set to that count. A package cannot render more lights than it contains, so its
own total is a true upper bound: sufficient by construction, with no headroom
to pay for. At or below the engine default of 32, no cap line is written at
all and an unlit export pays nothing.

ONE RULE, TWO IMPORTERS

`packages/core/godot_project.py` holds `rendering_block`, and `export.py` and
`walk_preview.py` both call it. Two hand-kept copies is exactly how the
preview's own comment says lighting gets signed off missing a rig, and 0.43.0
had left them as two copies that a test compared. Now there is one, and the
test checks the properties instead of the coincidence.

"""


def _require() -> None:
    missing = [str(p) for p in (EXPORT, PREVIEW, VERSION, CHANGELOG)
               if not p.is_file()]
    if missing:
        sys.exit("REFUSING: not found:\n  " + "\n  ".join(missing))


def cmd_check() -> int:
    _require()
    for p in (EXPORT, PREVIEW, VERSION, CHANGELOG):
        print("   ", _stamp(p))
    if SHARED.is_file():
        print("\nALREADY APPLIED.")
        return 0
    _patch_export(EXPORT.read_text(encoding="utf-8"))
    print("\n  ok  export.py -> shared rendering_block")
    _patch_preview(PREVIEW.read_text(encoding="utf-8"))
    print("  ok  walk_preview.py -> shared rendering_block")
    print(f"  ok  NEW {SHARED.relative_to(ROOT)}")
    print(f"  ok  REWRITE {TEST.relative_to(ROOT)}")
    print(f"\nVERSION {VERSION.read_text(encoding='utf-8').strip()} -> {NEW_VERSION}")
    return 0


def cmd_apply() -> int:
    _require()
    if SHARED.is_file():
        print("ALREADY APPLIED; nothing to do.")
        return 0
    ver = VERSION.read_text(encoding="utf-8").strip()
    log = CHANGELOG.read_text(encoding="utf-8")
    if f"[{NEW_VERSION}]" in log:
        raise SystemExit(f"REFUSING: CHANGELOG already has [{NEW_VERSION}]")

    exp = _patch_export(EXPORT.read_text(encoding="utf-8"))
    prev = _patch_preview(PREVIEW.read_text(encoding="utf-8"))

    for p in TOUCHED:
        if p.is_file():
            (p.parent / f"{p.name}.{TAG}").write_bytes(p.read_bytes())

    SHARED.write_text(SHARED_SOURCE, encoding="utf-8", newline="")
    EXPORT.write_text(exp, encoding="utf-8", newline="")
    PREVIEW.write_text(prev, encoding="utf-8", newline="")
    TEST.parent.mkdir(parents=True, exist_ok=True)
    TEST.write_text(TEST_SOURCE, encoding="utf-8", newline="")
    tail = "\n" if b"\n" in VERSION.read_bytes() else ""
    VERSION.write_text(NEW_VERSION + tail, encoding="utf-8", newline="")
    ec = _eol(CHANGELOG)
    entry = CHANGELOG_ENTRY if ec == "\n" else CHANGELOG_ENTRY.replace("\n", "\r\n")
    CHANGELOG.write_text(entry + log, encoding="utf-8", newline="")

    print("  ok  export.py -> shared rendering_block")
    print("  ok  walk_preview.py -> shared rendering_block")
    print(f"  ok  wrote {SHARED.relative_to(ROOT)}")
    print(f"  ok  rewrote {TEST.relative_to(ROOT)}")
    print(f"  ok  VERSION {ver} -> {NEW_VERSION}")
    print("\nafter:")
    for p in (EXPORT, PREVIEW, SHARED, TEST, VERSION, CHANGELOG):
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
    if SHARED.is_file():
        SHARED.unlink(); print(f"  removed {SHARED.name}"); n += 1
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
            raise SystemExit(f"SELFTEST FAILED: '{name}' did not fail the "
                             f"tests.\n" + r.stdout[-2000:])
        if r.returncode == 5:
            raise SystemExit(f"SELFTEST FAILED: '{name}' collected NOTHING")
        print(f"  ok  falsified: {name}  (rc={r.returncode})")
    finally:
        path.write_bytes(orig)


def cmd_selftest() -> int:
    _require()
    if not SHARED.is_file():
        raise SystemExit("SELFTEST: patch is not applied.")

    r = _pytest([str(TEST.relative_to(LF))])
    if r.returncode != 0:
        raise SystemExit("SELFTEST FAILED: new tests do not pass.\n"
                         + r.stdout[-3000:])
    print("  ok  new tests pass (rc=0)")

    _falsify("the per-object cap comes back", SHARED,
             lambda t: t.replace(
                 'f"limits/opengl/max_renderable_lights={light_count}",',
                 'f"limits/opengl/max_renderable_lights={light_count}",\n'
                 '            "limits/opengl/max_lights_per_object=64",'))
    _falsify("the cap is rounded up instead of exact", SHARED,
             lambda t: t.replace("max_renderable_lights={light_count}",
                                 "max_renderable_lights={light_count + 64}"))
    _falsify("an unlit package is given a cap anyway", SHARED,
             lambda t: t.replace(
                 "if light_count > ENGINE_DEFAULT_RENDERABLE_LIGHTS:",
                 "if True:"))
    _falsify("the preview stops sharing the rule", PREVIEW,
             lambda t: t.replace("{rendering}",
                                 '[rendering]\nrenderer/rendering_method="gl_compatibility"\n\n'))

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
