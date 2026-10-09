"""Break a level's frames into their sources of light: shoot it with each source switched off in turn, and with all of them off.

    python tools/light_breakdown.py <walk project> [--out DIR] [--interiors N]
        [--station NAME:EX,EY,EZ,TX,TY,TZ ...] [--sources lightmap,live,...]
        [--also SOURCE+SOURCE ...] [--fills]

THE QUESTION (2026-10-09, the walker: "build that light breakdown
instrument"). A night frame is the bake, the live lamps, the sun or moon, the
environment's ambient and reflections, the rooms' probes, every glowing
surface, the sky's own pixels and the fog, all at once, through the night
grade. Nothing in this repo said which of them a frame is made of. Cold run
9213's airport terminal read near-black around its payphone at midnight, and
whether that room has no lamps of its own or loses them somewhere could not
be asked.

WHAT IT SHOOTS. `look_shots`' own cameras -- the derived ones, `--interiors N`
rooms, and any `--station` -- in one run per configuration, each a fresh load
of the level:
- `all`, twice: nothing switched off. The two must agree, or no difference
  below is evidence. That is the control.
- `-<source>`: that source alone off, for each source.
- `none`: every source off. What is left is light no switch reaches, such as
  a ShaderMaterial's glow or an unshaded surface, and each run's manifest
  counts those.
- `--also a+b`: those sources off together, repeatable. One source alone can
  hide what it does when another stands in for it, and the bake is the case
  that needs this. A lightmapped surface takes no ambient and no probe light,
  so clearing the lightmap lets both in. Measured on cold run 9213's walk
  copy: two concrete rooms read 1.7 and 2.5 with the bake, and 6.8 and 9.8
  without it. So the bake's own light is `-ambient+probes` less
  `-lightmap+ambient+probes`, not `all` less `-lightmap`.
The switches are look_shots.gd's SWITCHES. Each run's manifest says what each
switch found and turned off, and a switch that found nothing is printed so,
because "no drop" from a switch with nothing to turn off is not a finding.

WHAT IT CANNOT SPLIT AT RUN TIME, AND HOW `--fills` DOES.
- The room fills. They are baked into the lightmap and exist only while the
  lightmapper runs, so `-lightmap` removes them with the lamps. `--fills`
  re-bakes two copies of the project with Level Factory's own bake, exactly
  as the export runs it:
  - `rebake_fills_on`: no change, the control;
  - `rebake_fills_off`: the level's preset's `bake_room_fill` at 0, which
    makes `LuxLightLoader.add_bake_fills` lay none.
  Each copy has its bake files removed and its entry pointed back at the
  presentation scene first, the way `docs/findings/night_interiors/
  rebake_variant.py` does it, because `bake()` refuses a package already
  retargeted at bake.tscn and deletes its bake files when it does.
  - The fills' light is `rebake_fills_on` less `rebake_fills_off`.
  - How faithfully a re-bake reproduces the shipped lightmap is `all` less
    `rebake_fills_on`.
  - It needs a display: the editor shows for about a minute a bake.
  - The copies are deleted once shot.
- Addition. Luma comes after the night grade and the tonemapper, which are
  not linear, so the drops do not add up to the whole. Each drop is what the
  frame loses without that one source, not that source's share of the light.

FRAME AND UNITS: Rec.709 luma, 0-255, of the 8-bit frame as look_shots
reports it. "frame" is the whole frame's mean, "centre" the middle third's.

Writes under --out:
- `<config>/`: each configuration's PNGs, and `<config>.json`, its look_shots
  manifest;
- `breakdown.json`: the tables, the control, and what each switch found;
- `breakdown.txt`: the tables as printed;
- with Pillow installed, `sheets/<station>.png`: that station's frames side by
  side, one per configuration, each labelled with its frame mean.
Prints the tables and stops.
"""
import argparse
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look_shots                                    # noqa: E402
from godot_probe import ProbeFailed, require_godot   # noqa: E402

#: look_shots.gd's SWITCHES, in the order the table prints them.
SOURCES = ["lightmap", "live", "sun", "ambient", "probes", "emission", "sky", "fog"]
FACTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESENTATION = "presentation/lux.applied.tscn"


def unbake(dest):
    """Remove a copy's bake and point its entry back at the presentation
    scene, so Level Factory's `bake()` takes it for an unbaked package."""
    from packages.exporting import light_bake
    for f in light_bake.BAKE_FILES:
        p = os.path.join(dest, f)
        if os.path.exists(p):
            os.remove(p)
    entry = os.path.join(dest, "mission.tscn")
    with open(entry, encoding="utf-8") as fh:
        t = fh.read()
    old, new = "load('res://bake.tscn')", "load('res://%s')" % light_bake.PRESENTATION
    if t.count(old) != 1:
        raise SystemExit("%s: loads bake.tscn %d times, not once" % (entry, t.count(old)))
    with open(entry, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(t.replace(old, new))


def zero_fills(dest):
    """Set the level's preset's `bake_room_fill` to 0 in a copy. The preset is
    the one the presentation scene's LuxRoot names as `active_preset`.
    Returns the preset's path and the value it had (None when it had no
    line, which is the preset class's default)."""
    with open(os.path.join(dest, PRESENTATION), encoding="utf-8") as fh:
        pres = fh.read()
    m = re.search(r'^\[node name="LuxRoot"[^\]]*\]\n(?:[^\[\n].*\n)*?active_preset = ExtResource\("([^"]+)"\)',
                  pres, re.M)
    if not m:
        raise SystemExit("no LuxRoot with an active_preset in " + PRESENTATION)
    r = re.search(r'^\[ext_resource [^\]]*path="res://([^"]+)" id="%s"\]' % re.escape(m.group(1)), pres, re.M)
    if not r:
        raise SystemExit("the active preset's ext_resource is not in " + PRESENTATION)
    path = os.path.join(dest, r.group(1))
    with open(path, encoding="utf-8") as fh:
        t = fh.read()
    had = re.search(r"^bake_room_fill = (.+)$", t, re.M)
    if had:
        t = re.sub(r"^bake_room_fill = .+$", "bake_room_fill = 0.0", t, flags=re.M)
    else:
        head = re.search(r"^\[resource\]\n(script = .+\n)", t, re.M)
        if not head:
            raise SystemExit(path + ": no [resource] section opening with its script")
        t = t[:head.end()] + "bake_room_fill = 0.0\n" + t[head.end():]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(t)
    return r.group(1), (had.group(1) if had else None)


def rebake(project, dest, fills, godot):
    """Copy `project` to `dest` and bake it with Level Factory's own `bake()`,
    the room fills on or off. Returns the bake's report, with what was done."""
    sys.path.insert(0, os.path.join(FACTORY, "level_factory"))
    from packages.exporting import light_bake
    # THE SAME MODELS SET DYNAMIC AS THE SHIPPED BAKE: the export passes the
    # responders' cars as `spawned` (Level Factory 0.162.1), and the package's
    # own `light_bake.json` records which they were
    spawned = []
    shipped = os.path.join(project, light_bake.REPORT)
    if os.path.isfile(shipped):
        with open(shipped, encoding="utf-8") as fh:
            spawned = list((json.load(fh).get("imports") or {}).get("spawned") or [])
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(project, dest)
    unbake(dest)
    note = {"fills": fills, "spawned": spawned}
    if not fills:
        note["preset"], note["bake_room_fill_was"] = zero_fills(dest)
    report = light_bake.bake(dest, godot, log=lambda s: print("    " + s), spawned=spawned)
    report["breakdown"] = note
    return report


def configs(sources, also=()):
    out = [("all", []), ("all_control", [])]
    out += [("off_" + s, [s]) for s in sources]
    out += [("off_" + "+".join(c), list(c)) for c in also]
    out.append(("none", list(sources)))
    return out


def label(cfg):
    return "-" + cfg[4:] if cfg.startswith("off_") else cfg


def run(project, out, cfg, switch_off, interiors, stations, timeout):
    shots_dir = os.path.join(out, cfg)
    try:
        r = look_shots.shoot(project, shots_dir, interiors=interiors, stations=stations,
                             switch_off=switch_off, timeout=timeout)
    except ProbeFailed as e:
        r = {"error": "NOT MEASURED: " + str(e)}
    r["project"] = os.path.abspath(project)
    r["config"] = cfg
    r["switch_off_asked"] = switch_off
    with open(os.path.join(out, cfg + ".json"), "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1)
    return r


def table(rows, cols, key):
    """Lines of a table: one row a station, one column a configuration, each
    column as wide as its label."""
    sw = max([18] + [len(st) + 1 for st in rows])
    widths = [max(8, len(label(c)) + 2) for c in cols]
    head = "  " + "station".ljust(sw) + "".join(label(c).rjust(w) for c, w in zip(cols, widths))
    lines = [head]
    for st in rows:
        cells = []
        for c, w in zip(cols, widths):
            v = key(c, st)
            cells.append(("-" if v is None else "%.1f" % v).rjust(w))
        lines.append("  " + st.ljust(sw) + "".join(cells))
    return lines


def sheets(out, stations, cols, results):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return "no Pillow: no sheets"
    os.makedirs(os.path.join(out, "sheets"), exist_ok=True)
    tw, th, per_row = 400, 225, 4
    for st in stations:
        tiles = []
        for c in cols:
            shot = results[c]["shots"].get(st)
            if not shot or not os.path.isfile(shot.get("png", "")):
                continue
            im = Image.open(shot["png"]).convert("RGB").resize((tw, th))
            tiles.append((c, shot["mean"], im))
        if not tiles:
            continue
        nrows = (len(tiles) + per_row - 1) // per_row
        sheet = Image.new("RGB", (tw * per_row, (th + 20) * nrows), (0, 0, 0))
        d = ImageDraw.Draw(sheet)
        for i, (c, mean, im) in enumerate(tiles):
            x, y = (i % per_row) * tw, (i // per_row) * (th + 20)
            sheet.paste(im, (x, y + 20))
            d.text((x + 6, y + 4), "%s  (frame %.1f)" % (label(c), mean), fill=(255, 255, 255))
        sheet.save(os.path.join(out, "sheets", st + ".png"))
    return "sheets in " + os.path.join(out, "sheets")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="the walk project to photograph")
    ap.add_argument("--out", default="light_breakdown")
    ap.add_argument("--interiors", type=int, default=0, metavar="N",
                    help="also stand inside N rooms facing a wall (look_shots' own)")
    ap.add_argument("--station", action="append", default=[], metavar="NAME:EX,EY,EZ,TX,TY,TZ",
                    help="a given camera, repeatable (look_shots' own)")
    ap.add_argument("--sources", default=",".join(SOURCES),
                    help="the sources to switch, in this order (default: all of them)")
    ap.add_argument("--also", action="append", default=[], metavar="SOURCE+SOURCE",
                    help="those sources off together, repeatable")
    ap.add_argument("--fills", action="store_true",
                    help="also re-bake two copies, the room fills on and off, and shoot both "
                         "(the editor shows for about a minute a bake)")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args(argv)
    sources = [s.strip() for s in a.sources.split(",") if s.strip()]
    also = [[s.strip() for s in c.split("+") if s.strip()] for c in a.also]
    bad = [s for s in sources + [x for c in also for x in c] if s not in SOURCES]
    if bad:
        print("[light_breakdown] no such source: %s; the sources are %s" % (", ".join(bad), ", ".join(SOURCES)))
        return 2
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    results = {}
    for cfg, off in configs(sources, also):
        print("[light_breakdown] %-14s %s" % (cfg, ",".join(off) or "(nothing off)"), flush=True)
        r = run(a.project, out, cfg, off, a.interiors, a.station, a.timeout)
        if "error" in r:
            print("    REFUSED: %s" % r["error"])
        results[cfg] = {"error": r.get("error"),
                        "switched_off": r.get("switched_off", {}),
                        "shots": {s["name"]: s for s in r.get("shots", []) if s.get("pixels")}}
    rebakes = {}
    if a.fills:
        godot = require_godot()
        for cfg, fills in (("rebake_fills_on", True), ("rebake_fills_off", False)):
            dest = os.path.join(out, cfg + "_project")
            print("[light_breakdown] %-16s re-baking a copy, the room fills %s" % (cfg, "on" if fills else "off"),
                  flush=True)
            rep = rebake(a.project, dest, fills, godot)
            rebakes[cfg] = {k: rep.get(k) for k in ("ok", "reason", "editor_s", "room_fills", "rigs", "breakdown")}
            if rep.get("ok"):
                r = run(dest, out, cfg, [], a.interiors, a.station, a.timeout)
                results[cfg] = {"error": r.get("error"), "switched_off": {},
                                "shots": {s["name"]: s for s in r.get("shots", []) if s.get("pixels")}}
            else:
                results[cfg] = {"error": "the re-bake failed: %s" % rep.get("reason"), "switched_off": {}, "shots": {}}
                print("    RE-BAKE FAILED: %s" % rep.get("reason"))
            shutil.rmtree(dest, ignore_errors=True)
            shutil.rmtree(dest + ".lightbake", ignore_errors=True)
    base = results["all"]
    if base["error"] or not base["shots"]:
        print("[light_breakdown] the baseline run measured nothing; no table")
        return 1
    stations = list(base["shots"].keys())
    cols = [c for c, _ in configs(sources, also) if not results[c]["error"]]
    cols += [c for c in rebakes if not results[c]["error"]]

    def frame(c, st):
        s = results[c]["shots"].get(st)
        return None if s is None else s["mean"]

    def centre(c, st):
        s = results[c]["shots"].get(st)
        return None if s is None else s["centre"]["mean"]

    ctl = results["all_control"]["shots"]
    moved = [(abs(base["shots"][st]["mean"] - ctl[st]["mean"]),
              abs(base["shots"][st]["centre"]["mean"] - ctl[st]["centre"]["mean"]))
             for st in stations if st in ctl]
    lines = ["light breakdown: %s" % os.path.abspath(a.project),
             "luma 0-255 after the grade; each column one configuration, `-x` with x alone off",
             "",
             "the control, `all` against `all_control`: frame means differ by at most %.2f, centre by %.2f"
             % (max(m[0] for m in moved) if moved else float("nan"),
                max(m[1] for m in moved) if moved else float("nan")),
             "",
             "what each switch found and turned off (the first run that used it):"]
    for s in sources:
        got = results.get("off_" + s, {}).get("switched_off", {}).get(s)
        lines.append("  %-9s %s" % (s, json.dumps(got) if got is not None else "NOT REPORTED"))
    left = results.get("none", {}).get("switched_off", {}).get("emission")
    if left:
        lines.append("  left on by every switch: %d ShaderMaterial(s) and %d unshaded material(s)"
                     % (left.get("shader_materials_left", 0), left.get("unshaded_materials_left", 0)))
    lines += ["", "FRAME MEAN"] + table(stations, cols, frame)
    lines += ["", "CENTRE MEAN"] + table(stations, cols, centre)
    lines += ["", "THE DROP, frame mean: `all` less each configuration"]
    lines += table(stations, [c for c in cols if c not in ("all", "all_control") and not c.startswith("rebake_")],
                   lambda c, st: (None if frame(c, st) is None else frame("all", st) - frame(c, st)))
    if rebakes:
        lines += ["", "THE RE-BAKES (Level Factory's own bake on a copy):"]
        for c, rep in rebakes.items():
            lines.append("  %-17s ok %s, %s room fill(s), %s s in the editor%s"
                         % (c, rep.get("ok"), rep.get("room_fills"), rep.get("editor_s"),
                            "" if rep.get("ok") else ", " + str(rep.get("reason"))))
        if all(not results[c]["error"] for c in rebakes):
            pairs = (("the fills, frame", frame, "rebake_fills_on", "rebake_fills_off"),
                     ("the fills, centre", centre, "rebake_fills_on", "rebake_fills_off"),
                     ("the re-bake against the shipped bake, frame", frame, "all", "rebake_fills_on"))
            for title, key, a_cfg, b_cfg in pairs:
                lines.append("")
                lines.append("%s: %s less %s" % (title.upper(), label(a_cfg), label(b_cfg)))
                for st in stations:
                    va, vb = key(a_cfg, st), key(b_cfg, st)
                    lines.append("  %-30s %s" % (st, "-" if va is None or vb is None else "%+.1f" % (va - vb)))
    lines.append("")
    lines.append(sheets(out, stations, cols, results))
    text = "\n".join(lines)
    print(text)
    with open(os.path.join(out, "breakdown.txt"), "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    manifest = None
    lf = os.path.join(a.project, "LF_MANIFEST.json")
    if os.path.isfile(lf):
        with open(lf, encoding="utf-8") as fh:
            m = json.load(fh)
        manifest = {k: m.get(k) for k in ("mission", "candidate", "built_utc", "factory_version")}
    with open(os.path.join(out, "breakdown.json"), "w", encoding="utf-8") as fh:
        json.dump({"project": os.path.abspath(a.project), "package": manifest, "sources": sources,
                   "control_max_moved": {"frame": max((m[0] for m in moved), default=None),
                                         "centre": max((m[1] for m in moved), default=None)},
                   "switched_off": {c: results[c]["switched_off"] for c in results},
                   "rebakes": rebakes,
                   "refused": {c: results[c]["error"] for c in results if results[c]["error"]},
                   "frame": {c: {st: frame(c, st) for st in stations} for c in cols},
                   "centre": {c: {st: centre(c, st) for st in stations} for c in cols}},
                  fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
