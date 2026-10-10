"""Re-bake a copy of a baked level with Level Factory's own bake, under another Lux preset or without its room fills.

    python tools/lux_rebake.py <walk project> <dest> [--preset NAME] [--no-fills] [--set FIELD=VALUE ...]
                               [--bake-environment none|scene] [--bake-quality 0|1|2|3]

WHAT IT DOES, in order, on a copy (the source is only read):
1. Copies the project to `dest`.
2. Un-bakes the copy: its bake files go and its entry is pointed back at the
   presentation scene, the way `docs/findings/night_interiors/
   rebake_variant.py` does it. Level Factory's `light_bake.bake()` refuses a
   package already retargeted at bake.tscn, and deletes its bake files when
   it does.
3. `--preset NAME`: the presentation scene's LuxRoot takes
   `runtime/lux/presets/NAME.tres` as its `active_preset`. Every package
   carries every preset Lux ships.
4. `--no-fills`: the preset in force gets `bake_room_fill = 0.0`, so
   `LuxLightLoader.add_bake_fills` lays none. `--set FIELD=VALUE` sets any
   field on the preset in force the same way: `street_lamps_lit=true` bakes
   a day level with its street lamps on, the way every one was before Lux
   0.71.0.
5. Bakes with `light_bake.bake()`, exactly as the export runs it. It passes
   the shipped bake's `spawned` set, the responders' cars, which the
   package's own `light_bake.json` records.
6. `--bake-environment none|scene`: the bake's `LightmapGI` takes
   `environment_mode = 0` (none) or `1` (the scene's environment, which
   LuxRoot builds in the editor too) in place of Level Factory's own.
   Everything else in the bake scene is Level Factory's own text.
   - **Level Factory 0.131.0 to 0.163.1 baked `0`,** so their lightmaps
     hold no sky light, and a lightmapped surface takes no ambient at run
     time either (`docs/findings/light_breakdown/`).
   - **Since 0.164.0 it bakes `1`,** the walker's call after
     `docs/findings/lighting_spec_vs_lux/` measured it with this option.
   - `none` is the control against a package from before.
7. `--bake-quality 0|1|2|3`: the bake's `LightmapGI` `quality`, Low to Ultra, in
   place of Level Factory's `QUALITY` (0, Low: "baked the lot in 22 s and is what
   was priced"). Roadmap 224 asks what a higher one buys the blotches a large pale
   face takes from a bounce-only bake, and what it costs in the editor's seconds.

MEASURED. A re-bake with no change reproduces the shipped frames exactly,
0.0 at every camera, on cold run 9213's walk copy
(`docs/findings/light_breakdown/`).

WHAT A PRESET RE-BAKE IS. A level is set at one time of day and baked for it
(`docs/LEVEL_STANDARD.md` section 17). The Lux preset is what that slot
changes today -- the sun or moon, the sky, the ambient, the fixtures' night
scale and the room fills -- so a re-bake under another slot's preset is the
level as it would ship at that slot. If the pipeline ever varies more than
the preset by slot, it stops being that.

The editor shows for about a minute a bake: Godot 4.7 bakes lightmaps only in
the editor, with a display. Prints the bake's report line and stops.
"""
import argparse
import json
import os
import re
import shutil
import sys

FACTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESENTATION = "presentation/lux.applied.tscn"
PRESETS = "runtime/lux/presets"


def _light_bake():
    lf = os.path.join(FACTORY, "level_factory")
    if lf not in sys.path:
        sys.path.insert(0, lf)
    from packages.exporting import light_bake
    return light_bake


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def unbake(dest):
    """Remove a copy's bake and point its entry back at the presentation
    scene, so `bake()` takes it for an unbaked package."""
    lb = _light_bake()
    for f in lb.BAKE_FILES:
        p = os.path.join(dest, f)
        if os.path.exists(p):
            os.remove(p)
    entry = os.path.join(dest, "mission.tscn")
    t = _read(entry)
    old, new = "load('res://bake.tscn')", "load('res://%s')" % lb.PRESENTATION
    if t.count(old) != 1:
        raise SystemExit("%s: loads bake.tscn %d times, not once" % (entry, t.count(old)))
    _write(entry, t.replace(old, new))


def _preset_line(pres):
    """The LuxRoot's `active_preset` ext_resource: (its whole line, its path)."""
    m = re.search(r'^\[node name="LuxRoot"[^\]]*\]\n(?:[^\[\n].*\n)*?active_preset = ExtResource\("([^"]+)"\)',
                  pres, re.M)
    if not m:
        raise SystemExit("no LuxRoot with an active_preset in " + PRESENTATION)
    r = re.search(r'^\[ext_resource [^\]]*id="%s"\]$' % re.escape(m.group(1)), pres, re.M)
    if not r:
        raise SystemExit("the active preset's ext_resource is not in " + PRESENTATION)
    p = re.search(r'path="res://([^"]+)"', r.group(0))
    if not p:
        raise SystemExit("the active preset's ext_resource has no res:// path: " + r.group(0))
    return r.group(0), p.group(1)


def active_preset(project):
    """The package-relative path of the preset a level runs under."""
    return _preset_line(_read(os.path.join(project, PRESENTATION)))[1]


def set_preset(dest, name):
    """Point the copy's LuxRoot at `runtime/lux/presets/<name>.tres`. A uid on
    the line goes with the old path: Godot would resolve the uid first."""
    rel = "%s/%s.tres" % (PRESETS, name)
    if not os.path.isfile(os.path.join(dest, rel)):
        have = sorted(f[:-5] for f in os.listdir(os.path.join(dest, PRESETS)) if f.endswith(".tres"))
        raise SystemExit("no preset %s in the package; it carries %s" % (name, ", ".join(have)))
    path = os.path.join(dest, PRESENTATION)
    pres = _read(path)
    line, was = _preset_line(pres)
    new = re.sub(r'path="res://[^"]+"', 'path="res://%s"' % rel, line)
    new = re.sub(r'\s+uid="[^"]*"', "", new)
    if pres.count(line) != 1:
        raise SystemExit("the preset's ext_resource line is not unique in " + PRESENTATION)
    _write(path, pres.replace(line, new))
    return was, rel


def set_preset_field(dest, key, value):
    """`key = value` (GDScript literal text) in the copy's preset in force.
    Returns the preset's path and the text the field had (None: no line, the
    class default)."""
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", key):
        raise SystemExit("not a preset field name: %r" % key)
    rel = active_preset(dest)
    path = os.path.join(dest, rel)
    t = _read(path)
    line = re.compile(r"^%s = (.+)$" % re.escape(key), re.M)
    had = line.search(t)
    if had:
        t = line.sub(lambda _m: "%s = %s" % (key, value), t, count=1)
    else:
        head = re.search(r"^\[resource\]\n(script = .+\n)", t, re.M)
        if not head:
            raise SystemExit(path + ": no [resource] section opening with its script")
        t = t[:head.end()] + "%s = %s\n" % (key, value) + t[head.end():]
    _write(path, t)
    return rel, (had.group(1) if had else None)


def zero_fills(dest):
    """`bake_room_fill = 0.0` in the copy's preset in force."""
    return set_preset_field(dest, "bake_room_fill", "0.0")


#: `--bake-environment`: the LightmapGI `environment_mode` each name sets.
BAKE_ENVIRONMENTS = {"none": 0, "scene": 1}


def _bake_environment(lb, mode):
    """Level Factory's bake scene text with `environment_mode` set to `mode`.
    Refuses unless its template carries the line exactly once."""
    line = re.compile(r"^environment_mode = \d+$", re.M)
    if len(line.findall(lb.BAKE_TSCN)) != 1:
        raise SystemExit("Level Factory's BAKE_TSCN does not carry one environment_mode line")
    return line.sub("environment_mode = %d" % mode, lb.BAKE_TSCN)


def rebake(project, dest, godot, preset=None, fills=True, log=print, fields=None,
           environment=None, quality=None):
    """Copy `project` to `dest` and bake it with Level Factory's own `bake()`,
    under `preset` (a name in runtime/lux/presets, None for the level's own),
    with the room fills on or off, with `fields` ({name: GDScript literal})
    set on the preset in force, and with the bake's `environment_mode` taken
    from `BAKE_ENVIRONMENTS[environment]` (None: Level Factory's own). Returns
    the bake's report, with what was done under "rebake"."""
    lb = _light_bake()
    spawned = []
    shipped = os.path.join(project, lb.REPORT)
    if os.path.isfile(shipped):
        with open(shipped, encoding="utf-8") as fh:
            spawned = list((json.load(fh).get("imports") or {}).get("spawned") or [])
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(project, dest)
    unbake(dest)
    note = {"spawned": spawned, "preset_was": active_preset(dest), "fills": fills}
    if preset:
        note["preset_was"], note["preset"] = set_preset(dest, preset)
    if not fills:
        note["fill_preset"], note["bake_room_fill_was"] = zero_fills(dest)
    for key, value in (fields or {}).items():
        note.setdefault("fields", {})[key] = {"set": value, "was": set_preset_field(dest, key, value)[1]}
    template, quality_was = lb.BAKE_TSCN, lb.QUALITY
    if environment is not None:
        lb.BAKE_TSCN = _bake_environment(lb, BAKE_ENVIRONMENTS[environment])
        note["bake_environment"] = environment
    if quality is not None:
        lb.QUALITY = int(quality)
        note["bake_quality"] = {"set": int(quality), "was": quality_was}
    try:
        report = lb.bake(dest, godot, log=log, spawned=spawned)
    finally:
        lb.BAKE_TSCN, lb.QUALITY = template, quality_was
    report["rebake"] = note
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project")
    ap.add_argument("dest")
    ap.add_argument("--preset", default=None, help="a preset's name in runtime/lux/presets")
    ap.add_argument("--no-fills", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="FIELD=VALUE",
                    help="a field on the preset in force, as GDScript literal text, repeatable "
                         "(street_lamps_lit=true)")
    ap.add_argument("--bake-environment", choices=sorted(BAKE_ENVIRONMENTS), default=None,
                    help="the bake's LightmapGI environment_mode (default: Level Factory's own)")
    ap.add_argument("--bake-quality", type=int, choices=(0, 1, 2, 3), default=None,
                    help="the bake's LightmapGI quality, Low (0) to Ultra (3) (default: Level "
                         "Factory's QUALITY)")
    ap.add_argument("--godot", default=None)
    a = ap.parse_args(argv)
    fields = {}
    for s in a.set:
        k, sep, v = s.partition("=")
        if not sep or not v.strip():
            raise SystemExit("--set wants FIELD=VALUE, got %r" % s)
        fields[k.strip()] = v.strip()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from godot_probe import require_godot
    rep = rebake(a.project, a.dest, a.godot or require_godot(), a.preset, not a.no_fills, fields=fields,
                 environment=a.bake_environment, quality=a.bake_quality)
    print(json.dumps({k: rep.get(k) for k in ("ok", "reason", "editor_s", "room_fills", "rebake")}, indent=1))
    return 0 if rep.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
