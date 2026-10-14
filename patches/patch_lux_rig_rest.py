"""Lux 0.77.0: a rig at rest before its scene is packed (factory roadmap 247, the applied scene's bytes).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  addons/lux/runtime/rigs/lux_fluorescent_rig.gd   `rest()` after `set_energy_scale`
  addons/lux/runtime/rigs/lux_streetlight_rig.gd   `rest()` before `_bind_lenses`
  addons/lux/runtime/rigs/lux_stage_light_rig.gd   `rest()` before `_cycles`
  tools/rig_rest_selftest.gd                       NEW (`lux_rig_rest/rig_rest_selftest.gd.txt`)
CHANGELOG and VERSION from `lux_rig_rest/CHANGELOG_0.77.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. `LUX_ROOT=<copy>` applies it to a draft.

The GDScript here is written with four spaces where the files have a tab; `_tabs` turns every leading group of four
into one, anchors and new text alike, so no tab is typed by hand.

Read before it was written, in this session: the three rigs' `_process` (each clock, what each writes: the
fluorescent and the streetlight `light_energy` and a failing lens's emission, the stage light `light_color`),
their `_rebuild` (what a lamp is given: `r.energy * energy_scale`, `r.energy`, `colour_at(colors, i, 0.0, ...)`),
`_bind_lenses` (the lens's own duplicate, its base emission at `[3]`), the streetlight's dusk-to-dawn switch
(`visible` and dark lens copies, not energy), `_cycles`; `tools/failing_fixtures_selftest.gd`, whose cases the new
self-test follows; and the factory's `level_factory/assets/godot/run_lux_apply.gd`, which awaits seven frames
before it packs. The measurements: the factory's docs/findings/roofprops_bytes/lux_energy_pairs*.out.txt. Every
file LF.

    LUX_ROOT=<copy> python patches/patch_lux_rig_rest.py --results-pending
    python patches/patch_lux_rig_rest.py --results-pending
    python patches/patch_lux_rig_rest.py --fill
"""
import hashlib
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_rig_rest"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SELFTESTS": "result_selftests.txt"}
VERSION_WAS, VERSION = b"Lux 0.76.1", b"Lux 0.77.0"
CHANGELOG_HEAD = ("# Changelog\n\n## [0.76.1] - a correction: the bake traces the sun's occlusion whatever its shadow "
                  "flag\n")
FLUO = "addons/lux/runtime/rigs/lux_fluorescent_rig.gd"
STREET = "addons/lux/runtime/rigs/lux_streetlight_rig.gd"
STAGE = "addons/lux/runtime/rigs/lux_stage_light_rig.gd"
SHA = {FLUO: "8ade2d6f473a103e", STREET: "4ae293611810165f", STAGE: "65173cb68cd26021"}
NEW = {"tools/rig_rest_selftest.gd": "rig_rest_selftest.gd.txt"}


def _tabs(text):
    return re.sub(r"^((?:    )+)", lambda m: "\t" * (len(m.group(1)) // 4), text, flags=re.M)


FLUO_OLD = '''            l.light_energy = r.energy * energy_scale


func _ready() -> void:
    add_to_group(&"lux_light_rig")
'''
FLUO_NEW = '''            l.light_energy = r.energy * energy_scale


## Every lamp at its steady energy, every failing lens at its steady glow, and
## the clocks at zero (0.77.0, the factory's roadmap 247): the state a scene
## should be SAVED in. The rig animates from its own clocks whenever it
## processes, and a scene packed after some frames of that -- the factory's
## Lux apply awaits seven -- kept whatever they had reached: across its cold
## runs 9295 to 9300 seven flickering pendants' energies moved by about one
## part in 10,000 a run, and a failing tube read 2.618 or 3.7. Called by the
## packer; at run time the clocks start from zero as they always did.
func rest() -> void:
    _fail_t = 0.0
    _flicker_phase = 0.0
    var r := rig if rig != null else _default_rig()
    for l in _lights:
        if is_instance_valid(l):
            l.light_energy = r.energy * energy_scale
    var root := _find_lux_root()
    if root == null or root.fixtures_powered():
        for e in _lenses:
            (e[2] as BaseMaterial3D).emission_energy_multiplier = float(e[3])


func _ready() -> void:
    add_to_group(&"lux_light_rig")
'''

STREET_OLD = '''        set_process(true)


## A cycling pole dims its own lens with its lamp (0.62.0): the nearest lit
'''
STREET_NEW = '''        set_process(true)


## Every lamp at its steady energy, every failing lens at its steady glow, and
## the clocks at zero (0.77.0): see LuxFluorescentRig.rest -- across the
## factory's cold runs 9295 to 9300 three poles' energies moved from run to
## run. A dark dusk-to-dawn rig stays dark: its switch is `visible` and its
## lenses' dark copies, which this does not touch.
func rest() -> void:
    _fail_t = 0.0
    _flicker_phase = 0.0
    var r := rig if rig != null else _default_rig()
    for l in _lights:
        if is_instance_valid(l):
            l.light_energy = r.energy
    var root := _find_lux_root()
    if root == null or root.fixtures_powered():
        for e in _lenses:
            (e[2] as BaseMaterial3D).emission_energy_multiplier = float(e[3])


## A cycling pole dims its own lens with its lamp (0.62.0): the nearest lit
'''

STAGE_OLD = '''


func _cycles() -> bool:
'''
STAGE_NEW = '''


## Every lamp at the colour its cycle starts in, and the clock at zero
## (0.77.0): see LuxFluorescentRig.rest. A cycling rig's colours are a
## function of its clock, so a scene packed after some frames kept wherever
## the clock had reached.
func rest() -> void:
    _t = 0.0
    var r := rig if rig != null else _default_rig()
    for i in _lights.size():
        if not is_instance_valid(_lights[i]):
            continue
        if colors.size() > 0:
            _lights[i].light_color = colour_at(colors, i, 0.0, cycle_period_s)
        else:
            _lights[i].light_color = r.light_color


func _cycles() -> bool:
'''

EDITS = [(FLUO, FLUO_OLD, FLUO_NEW), (STREET, STREET_OLD, STREET_NEW), (STAGE, STAGE_OLD, STAGE_NEW)]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LUX / "VERSION").read_bytes().strip() == VERSION, (LUX / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LUX / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.77.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lux 0.77.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LUX / "VERSION").read_bytes().strip() == VERSION_WAS, (LUX / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.77.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.77.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LUX / rel).exists(), ("already applied", rel)
    out = {}
    for rel, old, new in EDITS:
        raw = (LUX / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        old, new = _tabs(old), _tabs(new)
        assert text.count(old) == 1, (rel, "anchor", text.count(old))
        assert not any(ln.startswith(" ") for ln in new.splitlines()), (rel, "a space indent left")
        out[rel] = (text.replace(old, new), eol)
    news = {r: _tabs((SRC / s).read_bytes().decode("utf-8").replace("\r\n", "\n")) for r, s in NEW.items()}
    cl = LUX / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    for rel, (text, eol) in out.items():
        (LUX / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, text in news.items():
        (LUX / r).write_bytes(text.encode("utf-8"))
    head = "# Changelog\n\n"
    cl.write_bytes((head + entry.rstrip("\n") + "\n\n" + cl_text[len(head):]).encode("utf-8").replace(b"\n", cl_eol))
    (LUX / "VERSION").write_bytes(VERSION)
    print("Lux 0.76.1 -> 0.77.0")


if __name__ == "__main__":
    main()
