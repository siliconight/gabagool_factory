"""Make one arm of the pole line's cost attribution on a COPY of a package.

    python docs/findings/pole_line/pole_cost_arms.py <package copy under _scratch/> shadows_off|poles_hidden

The pole line (9262) priced +170 draws a heading against 9261's lamps (`price_9261_9262/`), where the
light-pair census reads FEWER live pairs (1,950 -> 1,272) and the site scene's own meshes are the
same. Two things that differ and could submit more: the street lights' shadow maps (12 shadowed
street lights in both runs, but a cobra-head hangs at 7.5 m) and the poles themselves. One arm each:

  shadows_off    `shadow_caster_budget = 0` on the LuxRoot node of the scene the package loads,
                 `presentation/lux.applied.tscn`: Lux's own pricing dial (roadmap 60, "the same
                 package at 0, 4 and 24 casters"), which overrides the quality tier's 12 and leaves
                 every positional light unshadowed at runtime
  poles_hidden   `visible = false` on every node that instances a `utility_pole` module, in every
                 scene that stands one
  budget_N       `shadow_caster_budget = N` on the LuxRoot node: the same dial at the tiers'
                 other figures (Medium 8, Low and Compatibility 4)
  rigfade_M      Godot's own `distance_fade_*` on every street light, set where the light is made:
                 the package's vendored `lux_streetlight_rig.gd`, right after `_rebuild()` sets a
                 lamp's shadow -- the light kept to 500 m, its SHADOW cut beyond M m from the camera
                 over 5 m (`distance_fade_shadow`). The draws moving is the proof the engine reads it

REFUTED, KEPT: `fade_M`, the same four properties written on the `Street_*` nodes in the scene,
moved the draws by exactly 0. `lux_streetlight_rig.gd`'s `_rebuild()` frees every saved SpotLight3D
at runtime and builds its lamps anew, so the scene's lights never ran. Kept as an arm so the record
can be re-read; not a measurement of distance fade.

Refuses a path not under `_scratch/`, and refuses when the arm finds nothing to change. Draw counts
repeat exactly between passes (the controls' spread is 0), so one pass of an arm attributes draws;
frame time it does not.

REFUTED, KEPT: the first `shadows_off` set `shadow_enabled = false` on the 12 street lights' nodes
in the scene and moved the draws by exactly 0 at all 53 headings. Not a measurement: Lux's
`apply_shadow_policy` (lux_lighting.gd) sets `shadow_enabled` at runtime on the quality's
`max_shadow_casters` best-ranked lights, street lights first, so the scene's value was never read.
A knob with no effect is evidence about the wiring.
"""
import pathlib
import re
import sys


def _blocks(text):
    return re.split(r"\n(?=\[)", text)


def shadows_off(copy, budget=0):
    scene = copy / "presentation" / "lux.applied.tscn"
    text = scene.read_text(encoding="utf-8")
    ids = re.findall(r'^\[ext_resource type="Script"[^\]]*path="[^"]*/lux_root\.gd" id="([^"]+)"\]', text, re.M)
    if len(ids) != 1:
        sys.exit("UNKNOWN SHAPE: %d lux_root.gd scripts in %s" % (len(ids), scene))
    out, n = [], 0
    for b in _blocks(text):
        head = b.split("\n", 1)[0]
        if head.startswith("[node ") and ('\nscript = ExtResource("%s")' % ids[0]) in b:
            if "shadow_caster_budget" in b:
                sys.exit("ALREADY SET: %s" % head)
            b = b.replace('\nscript = ExtResource("%s")' % ids[0],
                          '\nscript = ExtResource("%s")\nshadow_caster_budget = %d' % (ids[0], budget), 1)
            n += 1
        out.append(b)
    if n != 1:
        sys.exit("UNKNOWN SHAPE: %d LuxRoot nodes in %s" % (n, scene))
    scene.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print("shadow_caster_budget = %d on LuxRoot in %s" % (budget, scene.relative_to(copy).as_posix()))


def shadow_fade(copy, metres):
    scene = copy / "presentation" / "lux.applied.tscn"
    text = scene.read_text(encoding="utf-8")
    out, n = [], 0
    for b in _blocks(text):
        head = b.split("\n", 1)[0]
        if (head.startswith("[node ") and 'type="SpotLight3D"' in head and 'name="Street_' in head
                and re.search(r'parent="[^"]*LuxClub/site_(pole|lamp)_\d+"', head)):
            if "distance_fade" in b:
                sys.exit("ALREADY SET: %s" % head)
            lines = b.rstrip("\n").split("\n")
            lines += ["distance_fade_enabled = true", "distance_fade_begin = 500.0",
                      "distance_fade_shadow = %.1f" % metres, "distance_fade_length = 5.0"]
            b = "\n".join(lines) + ("\n" if b.endswith("\n") else "")
            n += 1
        out.append(b)
    if not n:
        sys.exit("NOTHING CHANGED: no street light in %s" % scene)
    scene.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print("shadows cut beyond %g m on %d street light(s) in %s" % (metres, n, scene.relative_to(copy).as_posix()))


def poles_hidden(copy):
    total = 0
    for scene in sorted(copy.rglob("*.tscn")):
        text = scene.read_text(encoding="utf-8")
        ids = set(re.findall(r'^\[ext_resource type="PackedScene" path="[^"]*utility_pole[^"]*" id="([^"]+)"\]',
                             text, re.M))
        if not ids:
            continue
        out, n = [], 0
        for b in _blocks(text):
            head = b.split("\n", 1)[0]
            m = re.search(r'instance=ExtResource\("([^"]+)"\)', head)
            if head.startswith("[node ") and m and m.group(1) in ids:
                if "\nvisible = false" in b:
                    sys.exit("ALREADY HIDDEN: %s" % head)
                lines = b.split("\n")
                b = "\n".join([lines[0], "visible = false"] + lines[1:])
                n += 1
            out.append(b)
        if n:
            scene.write_text("\n".join(out), encoding="utf-8", newline="\n")
            print("hidden %d pole instance(s) in %s" % (n, scene.relative_to(copy).as_posix()))
            total += n
    if not total:
        sys.exit("NOTHING CHANGED: no utility_pole instance in %s" % copy)


def rig_fade(copy, metres):
    rig = copy / "runtime" / "lux" / "runtime" / "rigs" / "lux_streetlight_rig.gd"
    raw = rig.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    anchor = "\t\tlamp.shadow_enabled = r.shadows_enabled\n"
    if text.count(anchor) != 1:
        sys.exit("UNKNOWN SHAPE: %d of the rig's shadow line in %s" % (text.count(anchor), rig))
    if "distance_fade" in text:
        sys.exit("ALREADY SET: %s" % rig)
    text = text.replace(anchor, anchor + "\t\tlamp.distance_fade_enabled = true\n"
                                         "\t\tlamp.distance_fade_begin = 500.0\n"
                                         "\t\tlamp.distance_fade_shadow = %.1f\n"
                                         "\t\tlamp.distance_fade_length = 5.0\n" % metres)
    rig.write_bytes(text.replace("\n", eol).encode("utf-8"))
    print("every street light's shadow cut beyond %g m, set in %s" % (metres, rig.relative_to(copy).as_posix()))


def main():
    copy = pathlib.Path(sys.argv[1]).resolve()
    if "_scratch" not in copy.parts:
        sys.exit("refusing: %s is not a copy under _scratch/" % copy)
    arm = sys.argv[2]
    if arm.startswith("budget_"):
        return shadows_off(copy, int(arm.split("_", 1)[1]))
    if arm.startswith("fade_"):
        return shadow_fade(copy, float(arm.split("_", 1)[1]))
    if arm.startswith("rigfade_"):
        return rig_fade(copy, float(arm.split("_", 1)[1]))
    {"shadows_off": shadows_off, "poles_hidden": poles_hidden}[arm](copy)


if __name__ == "__main__":
    main()
