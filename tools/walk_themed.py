"""Assemble a Godot project you can open and WALK the themed site in.

WHAT THIS IS FOR. The pipeline's outputs are not openable as they stand. Lot
writes the themed site with the composed building referenced by an ABSOLUTE
path -- `res://C:/Projects/.../presentation_compose/out/presentation/site.tscn`
-- which Godot cannot load, and the building's own `res://art/zoo/*.glb` refs
resolve against a project root that only exists inside the compose job. The
portable export is a different thing again: it ships a mission shell for a
consumer runtime, with the walk scene stripped by contract, so it has no player
in it.

So there was no way to stand in the themed level and look at it, which is the
one check no instrument in this repo replaces.

    python tools\\walk_themed.py <workspace>\\.level_factory <mission-id> [--out DIR]

Then open DIR in Godot and press F5. The main scene is Lot's walk scene: its
player, its ladders, its spawn.

WHAT IT ASSEMBLES, and why each piece is here:

  * the composed themed BUILDING as `building.tscn`, plus its siblings --
    `site_base.glb` and `art/` -- because the building names them at the
    project root and nothing else brings them;
  * the themed SITE, with that absolute reference rewritten to
    `res://building.tscn`;
  * Lot's walk scene as the entry, and `addons/lot` for the player and site
    scripts it names;
  * a `project.godot` whose main scene is the walk scene, so F5 works with no
    further clicking.

WHAT IT IS NOT. Not an export, not a deliverable, and deliberately not written
anywhere the pipeline reads. It is scratch you can throw away and rebuild from
one command, which is the only safe kind of copy: roadmap 33 is a day spent on
artifacts that outlived the run that made them.

WHAT A NONZERO EXIT MEANS. The project was not assembled. It never leaves a
half-built directory reporting success -- a project that opens to an empty
scene is worse than one that refused to be built.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

_ABS_REF = re.compile(r'path="res://((?:[A-Za-z]:[\\/]|/)[^"]+)"')

_PROJECT = """; Scratch walk project, assembled by tools/walk_themed.py.
; Throw it away and rebuild it; nothing reads it back.
config_version=5

[application]
config/name="{name} (walk)"
run/main_scene="res://{entry}"
config/features=PackedStringArray("4.7")

[debug]
gdscript/warnings/inference_on_variant=1

; MUST match the shipped export's project.godot, which sets
; gl_compatibility. Without this Godot defaults to forward_plus, and the walk
; renders under a different renderer than the deliverable: different lighting,
; different materials, and any shot taken here is not comparable with one taken
; from the export. Found when shot_diff refused a pair whose renderer had
; silently changed from gl_compatibility to forward_plus between runs.
[rendering]
renderer/rendering_method="gl_compatibility"

; Lux is an EDITOR plugin as well as a runtime script. Without this its @tool
; side never registers, so the editor viewport shows the level unlit and you
; have to tick a box in Project Settings before the thing you came to look at
; appears. A scratch project that needs a manual step before it is correct is
; a scratch project that will be looked at wrong.
[editor_plugins]
enabled=PackedStringArray("res://addons/lux/plugin.cfg")
"""


class Failed(Exception):
    """Assembly could not complete. Never a partial success."""


def newest(root, name):
    """The newest file called `name` anywhere under `root`."""
    best = None
    for dirpath, _dirs, files in os.walk(root):
        if name in files:
            p = os.path.join(dirpath, name)
            if best is None or os.path.getmtime(p) > os.path.getmtime(best):
                best = p
    return best


def copy_into(src_dir, dst_dir, skip_names=(), skip_dirs=(".godot", "addons")):
    for dirpath, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel = os.path.relpath(dirpath, src_dir)
        target = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        os.makedirs(target, exist_ok=True)
        for f in files:
            if f in skip_names:
                continue
            shutil.copy2(os.path.join(dirpath, f), os.path.join(target, f))


#: Lux's NATIVE layout, not the export's.
#:
#: The export puts Lux at `runtime/lux/` and its localize step REWRITES the
#: `res://addons/lux/...` paths baked into the addon to match. Copying to
#: `runtime/lux` without that rewrite reproduces the layout and not the
#: relocation, and Godot then reports a wall of `Cannot open file
#: 'res://addons/lux/presets/*.tres'` plus a cascade ending in
#: `lux_root.gd:202 - Nonexistent function 'new'`. A scratch project has no
#: reason to relocate anything: left where the addon expects to be, every
#: internal path resolves with no rewriting at all.
_LUX_DEST = os.path.join("addons", "lux")

_LUX_NODE = """
[node name="LuxRoot" type="Node3D" parent="."]
script = ExtResource("lux_root")
"""

#: Written into the scratch project and attached to the walk scene. The walk
#: is assembled from themed_site_assemble's scene, NOT from lux.applied.tscn,
#: so it does not inherit run_lux_apply's fixture spawn -- measured on
#: category5_baie_dore_001: lux.quality.json said 152 fixture lights and
#: light_census on the preview said OmniLight3D 0.
_SPAWN_GD_NAME = "walk_fixtures.gd"
_SPAWN_GD = 'extends Node\n## Spawn Zoo\'s marked fixture lights in the scratch walk project.\n##\n## The shipped level gets these from `run_lux_apply.gd`, which calls\n## LuxFixtureSpawner and packs the result into lux.applied.tscn. The walk\n## project is assembled from themed_site_assemble\'s scene instead, with its\n## own grafted LuxRoot, so it does not inherit that spawn -- measured with\n## tools/light_census.py: lux.quality.json reported 152 fixture lights while\n## the preview ran OmniLight3D 0. A preview that is lit differently from the\n## level is worse than no preview, because it gets believed.\n\n\nfunc _ready() -> void:\n\tvar script_res: GDScript = load("res://addons/lux/runtime/lux_fixture_spawner.gd")\n\tif script_res == null:\n\t\tpush_warning("walk_fixtures: lux fixture spawner missing")\n\t\treturn\n\tvar root: Node = get_parent()\n\tif root == null:\n\t\treturn\n\t# WAIT A FRAME BEFORE SPAWNING. _ready runs while the parent is still\n\t# setting up its children, and Godot refuses add_child() on a node in that\n\t# state ("parent node is busy setting up children"). LuxFixtureSpawner does\n\t# not check the return, so it parents every rig into a container that never\n\t# entered the tree and reports "Spawned 152 fixture light(s)" -- measured:\n\t# containers=0 in the same breath as 152 successes.\n\tawait get_tree().process_frame\n\tvar res: Dictionary = script_res.spawn(root)\n\tprint("[walk_fixtures] %s" % String(res.get("msg", "")))\n\t# A spawn that reports 152 successes and leaves nothing in the tree is\n\t# either parenting somewhere that is not the running scene, or having its\n\t# container freed inside the same frame. Those need different fixes, and\n\t# one report at one instant cannot tell them apart -- so take the reading\n\t# twice, immediately and after the frame settles.\n\t_report("immediately", root)\n\tawait get_tree().process_frame\n\tawait get_tree().process_frame\n\t_report("two frames later", root)\n\n\nfunc _report(when: String, root: Node) -> void:\n\tvar kids: Array = []\n\tfor c in root.get_children():\n\t\tkids.append("%s(%s)" % [c.name, c.get_class()])\n\tvar omni: Array = root.find_children("*", "OmniLight3D", true, false)\n\tvar cons: Array = root.find_children("LuxFixtureLights", "", true, false)\n\tprint("[walk_fixtures] %s: root=%s(%s) in_tree=%s omni=%d containers=%d"\n\t\t% [when, root.name, root.get_class(), root.is_inside_tree(), omni.size(), cons.size()])\n\tprint("[walk_fixtures] %s: root children = %s" % [when, ", ".join(kids)])\n\tfor c in cons:\n\t\tprint("[walk_fixtures] %s: container %s rigs=%d"\n\t\t\t% [when, root.get_path_to(c), c.get_child_count()])\n\t\tif c.get_child_count() > 0:\n\t\t\tvar f: Node = c.get_child(0)\n\t\t\tvar fk: Array = []\n\t\t\tfor k in f.get_children():\n\t\t\t\tfk.append("%s(%s)" % [k.name, k.get_class()])\n\t\t\tprint("[walk_fixtures] %s: first rig %s(%s) kids = %s"\n\t\t\t\t% [when, f.name, f.get_class(), ", ".join(fk)])\n'

_SPAWN_NODE = """
[node name="WalkFixtures" type="Node" parent="."]
script = ExtResource("walk_fixtures")
"""

#: The preset line, when the mission's own lighting choice is known.
_LUX_PRESET_NODE = '''active_preset = ExtResource("lux_preset")
'''

_ACTIVE_PRESET = re.compile(r'active_preset\s*=\s*ExtResource\("([^"]+)"\)')


def applied_preset(applied_tscn):
    """The preset resource path ``lux_apply`` actually chose, or None.

    WHY THIS IS READ RATHER THAN DEFAULTED. ``graft_lux`` removes Lot's sun
    and environment and installs a bare LuxRoot, so before this the preview
    was lit by whatever the Lux script defaults to. Measured on
    ``category5_baie_dore_001``: ``lux.applied.tscn`` loads
    ``res://addons/lux/presets/blue_hour.tres`` and sets ``active_preset`` to
    it, and ``lux.quality.json`` says ``"preset": "Blue Hour"`` -- while the
    walk project's LuxRoot carried no ``active_preset`` line at all. Every
    walkthrough was therefore judging lighting the shipped level does not use,
    which is worse than walking unlit: unlit looks broken and gets fixed,
    wrong-but-plausible gets believed.
    """
    if not applied_tscn or not os.path.exists(applied_tscn):
        return None
    with open(applied_tscn, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    m = _ACTIVE_PRESET.search(text)
    if not m:
        return None
    ext = re.search(r'\[ext_resource[^\]]*path="([^"]+)"[^\]]*id="%s"\]'
                    % re.escape(m.group(1)), text)
    return ext.group(1) if ext else None


def graft_lux(tscn_text, drop_walk_lighting=True, preset=None,
              spawn_fixtures=True):
    """Add a LuxRoot to a walk scene, and take Lot's own lighting out.

    WHY THE SECOND HALF. Lot's walk scene ships a `WorldEnvironment` and a
    `Sun`, and Lux supplies both itself -- the shipped `lux.applied.tscn` has
    a LuxRoot and no environment or light of its own. Leaving Lot's in place
    lights the level twice, and that is not hypothetical: `look_shots.py`
    already recorded the difference on this project.

        no Lux        mean 108.6   p95 254   near-clip 18.62%
        Lux, 2 suns   mean 151.7   p95 248   near-clip  3.17%
        Lux, 1 sun    mean 147.0   p95 222   near-clip  1.13%

    Two suns is measurably worse than one and was already known. Returns the
    rewritten text; raises nothing, because a walk scene without a
    WorldEnvironment to remove is fine.
    """
    out = tscn_text
    if drop_walk_lighting:
        for name in ("WorldEnvironment", "Sun"):
            start = out.find('[node name="%s"' % name)
            if start < 0:
                continue
            nxt = out.find("\n[node ", start + 1)
            out = out[:start] + (out[nxt + 1:] if nxt >= 0 else "")
    ext = ('[ext_resource type="Script" '
           'path="res://%s/runtime/lux_root.gd" id="lux_root"]\n'
           % _LUX_DEST.replace(os.sep, "/"))
    node = _LUX_NODE
    extra = 1
    if preset:
        ext += ('[ext_resource type="Resource" path="%s" id="lux_preset"]\n'
                % preset)
        node = node.rstrip("\n") + "\n" + _LUX_PRESET_NODE
        extra += 1
    if spawn_fixtures:
        ext += ('[ext_resource type="Script" path="res://%s" '
                'id="walk_fixtures"]\n' % _SPAWN_GD_NAME)
        node = node.rstrip("\n") + "\n" + _SPAWN_NODE
        extra += 1
    marker = "\n\n[sub_resource"
    at = out.find(marker)
    if at < 0:
        at = out.find("\n\n[node ")
    out = out[:at] + "\n" + ext + out[at:] if at >= 0 else ext + out
    # load_steps is a preallocation hint; leaving it short makes Godot warn.
    m = re.search(r"load_steps=(\d+)", out)
    if m:
        out = out.replace("load_steps=%s" % m.group(1),
                          "load_steps=%d" % (int(m.group(1)) + extra), 1)
    return out.rstrip("\n") + "\n" + node


def clear_out(out):
    """Empty the scratch project, keeping Godot's `.godot` cache. Returns the
    paths that could not be removed.

    A plain `shutil.rmtree` dies with `WinError 32` and a traceback whose top
    frame is `shutil`, which names the mechanism and not the cause: Godot holds
    files under `.godot` for as long as the editor has the project open, and
    rebuilding a walk project you are currently walking is the normal thing to
    want to do. That cache is regenerated on import and is not part of what
    this assembles, so it is left alone; anything ELSE still locked is a real
    obstacle and is reported by name.
    """
    stuck = []
    for entry in os.listdir(out):
        if entry == ".godot":
            continue
        path = os.path.join(out, entry)
        try:
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except OSError:
            stuck.append(path)
    return stuck


def default_out(mission_id):
    """`<factory-root>/_runs/walk_<mission>` -- the repo's scratch convention.

    `_runs/` is gitignored and already holds every throwaway project in this
    workspace (`lux_0801`, `themed_site_probe`, `portable_*_walk`). Deriving it
    from this file's own location rather than the cwd means the command works
    from any directory, and keeps assembled projects out of both the user's
    Projects folder and the mission workspace.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "_runs", "walk_%s" % mission_id)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lf_dir", help="the workspace's .level_factory directory")
    ap.add_argument("mission_id")
    ap.add_argument("--out", default=None,
                    help="where to assemble (default <factory>/_runs/"
                         "walk_<mission>; must be outside the workspace)")
    ap.add_argument("--lux-repo", default=None,
                    help="Lux checkout; its addons/lux becomes runtime/lux so "
                         "the walk is lit like the export (default: a sibling "
                         "'lux' next to this tools/ directory)")
    ap.add_argument("--keep-walk-lighting", action="store_true",
                    help="keep Lot's WorldEnvironment and Sun alongside Lux "
                         "(two suns; measurably worse -- see graft_lux)")
    ap.add_argument("--lot-repo", default=None,
                    help="Lot checkout, for addons/lot (default: read "
                         "tools.local.json beside the workspace)")
    ap.add_argument("--godot", default=None,
                    help="Godot executable, to run an import pass at the end")
    ap.add_argument("--no-fixture-lights", action="store_true",
                    help="assemble WITHOUT spawning Zoo's fixture lights. The "
                         "B side of an A/B: emissive lenses glow under the "
                         "WorldEnvironment's glow pass whether or not any "
                         "light is cast, so the eye cannot separate a working "
                         "fixture from a decorative one. Two builds and a "
                         "pixel diff can.")
    args = ap.parse_args(argv)

    jobs = os.path.join(args.lf_dir, "jobs")
    themed = os.path.join(jobs, f"{args.mission_id}.themed_site_assemble")
    compose = os.path.join(jobs, f"{args.mission_id}.presentation_compose")
    if not os.path.isdir(themed):
        sys.stderr.write(
            f"no themed_site_assemble job for {args.mission_id}. Run the "
            f"mission with --art first.\n")
        return 2

    site = newest(themed, "site.tscn")
    walk = newest(themed, "site_walk.tscn")
    building = newest(compose, "site.tscn")
    if not site or not walk:
        sys.stderr.write("themed site is missing site.tscn or site_walk.tscn; "
                         "the job did not produce a walkable site.\n")
        return 2
    if not building:
        sys.stderr.write("no composed building found; run presentation_compose.\n")
        return 2

    out = args.out or default_out(args.mission_id)
    # The promise in this module's docstring -- "deliberately not written
    # anywhere the pipeline reads" -- needs teeth, because the first default
    # broke it. It put the scratch project at `<lf_dir>/walk/<mission>`, INSIDE
    # the workspace, and the pipeline duly stamped provenance records onto it:
    # site.tscn.provenance.json, project.godot.provenance.json, even
    # site_main.tscn.provenance.json for a file that was never there. Scratch
    # inside the workspace also shows up in every instrument that scans it --
    # `orphan_artifacts.py` reported .themed.tscn / .fit.tscn / .m90.tscn /
    # .p90.tscn as produced-and-unread, and they were this directory.
    real_out = os.path.abspath(out)
    if os.path.abspath(args.lf_dir) + os.sep in real_out + os.sep:
        sys.stderr.write(
            "refusing to assemble inside the workspace (%s).\n"
            "This is throwaway scratch; the pipeline treats anything under\n"
            ".level_factory as job output and stamps provenance on it. Pass\n"
            "--out somewhere outside, e.g. _runs\\walk_<mission>.\n" % out)
        return 2
    lot_repo = args.lot_repo
    if not lot_repo:
        local = os.path.join(os.path.dirname(args.lf_dir.rstrip("\\/")),
                             ".level_factory", "tools.local.json")
        for cand in (local, os.path.join(args.lf_dir, "tools.local.json")):
            if os.path.exists(cand):
                try:
                    with open(cand, encoding="utf-8") as fh:
                        lot_repo = (json.load(fh).get("repositories") or {}
                                    ).get("lot")
                except (OSError, json.JSONDecodeError):
                    pass
                if lot_repo:
                    break
    lux_repo = args.lux_repo or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lux")
    lux_src = os.path.join(str(lux_repo), "addons", "lux")

    addons_src = os.path.join(str(lot_repo), "godot", "addons", "lot") \
        if lot_repo else None
    if not addons_src or not os.path.isdir(addons_src):
        sys.stderr.write(
            "cannot find Lot's addons/lot -- pass --lot-repo <lot checkout>. "
            "Without the player script the walk scene has nothing to walk "
            "with, and a project that opens to a frozen camera would look "
            "like a level defect.\n")
        return 2

    if os.path.isdir(out):
        stuck = clear_out(out)
        if stuck:
            sys.stderr.write(
                "cannot rebuild %s -- these are locked by another process:\n"
                % out)
            for f in stuck[:8]:
                sys.stderr.write("   " + f + "\n")
            sys.stderr.write(
                "Godot holds a project's files while it has it open. Close the "
                "editor\nand run this again, or pass --out somewhere else.\n")
            return 2
    os.makedirs(out, exist_ok=True)

    # 1. The composed building and everything it names at ITS project root.
    copy_into(os.path.dirname(building), out,
              skip_names={"project.godot", "site.tscn", "site_main.tscn",
                          "HANDOFF.md", "compose.summary.json",
                          "portable_resource_manifest.json"})
    shutil.copy2(building, os.path.join(out, "building.tscn"))

    # 2. The themed site, with the absolute reference made local. Lot writes
    #    `res://<absolute path>` in non-portable mode; the file it names is the
    #    building copied above, and nothing else in the scene is absolute.
    with open(site, encoding="utf-8") as fh:
        text = fh.read()
    hits = _ABS_REF.findall(text)
    text = _ABS_REF.sub('path="res://building.tscn"', text)
    with open(os.path.join(out, "site.tscn"), "w", encoding="utf-8") as fh:
        fh.write(text)

    # 3. The walk scene, Lot's addon, and Lux -- because a walk lit by
    #    nothing is not a review of the level. The scratch project shipped
    #    with no Lux at all until now, so every walkthrough was judging
    #    untextured, unlit geometry against a level that ships lit.
    with open(walk, "r", encoding="utf-8") as fh:
        walk_text = fh.read()
    lux_note = "no --lux-repo: walking WITHOUT Lux (not what ships)"
    preset = applied_preset(newest(os.path.join(
        jobs, f"{args.mission_id}.lux_apply"), "lux.applied.tscn"))
    if lux_src and os.path.isdir(lux_src):
        shutil.copytree(lux_src, os.path.join(out, _LUX_DEST))
        walk_text = graft_lux(walk_text,
                              drop_walk_lighting=not args.keep_walk_lighting,
                              preset=preset,
                              spawn_fixtures=not args.no_fixture_lights)
        if not args.no_fixture_lights:
            with open(os.path.join(out, _SPAWN_GD_NAME), "w",
                      encoding="utf-8") as fh:
                fh.write(_SPAWN_GD)
        lux_note = os.path.abspath(lux_src) + (
            "" if args.keep_walk_lighting else "  (Lot's own sun/env removed)")
        if args.no_fixture_lights:
            lux_note += "\n             fixtures : NOT SPAWNED (--no-fixture-lights)"
        lux_note += "\n             preset   : " + (
            preset if preset else
            "NONE FOUND -- walking on Lux's DEFAULT, not this mission's "
            "choice; run lux_apply or the preview lights the wrong level")
    else:
        sys.stderr.write("[walk_themed] " + lux_note + "\n")
    with open(os.path.join(out, "site_walk.tscn"), "w", encoding="utf-8") as fh:
        fh.write(walk_text)
    for extra in ("site.site.gameplay.json", "site.site.lights.json"):
        src = os.path.join(os.path.dirname(walk), extra)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out, extra))
    os.makedirs(os.path.join(out, "addons"), exist_ok=True)
    shutil.copytree(addons_src, os.path.join(out, "addons", "lot"))

    with open(os.path.join(out, "project.godot"), "w", encoding="utf-8") as fh:
        fh.write(_PROJECT.format(name=args.mission_id, entry="site_walk.tscn"))

    # 4. An import pass, if Godot is available. Reported, not swallowed: a
    #    silently failed import is how 13 modules lost their sidecars and
    #    nobody noticed for a week (roadmap 33).
    imported = None
    if args.godot:
        try:
            proc = subprocess.run(
                [args.godot, "--headless", "--path", out, "--import"],
                capture_output=True, timeout=600)
            imported = proc.returncode
            if imported != 0:
                sys.stderr.write(
                    "import pass exited %d; open the project once in the "
                    "editor before walking.\n" % imported)
        except (OSError, subprocess.SubprocessError) as exc:
            sys.stderr.write("import pass did not run: %s\n" % exc)

    print("assembled: %s" % out)
    print("  building : %s" % building)
    print("  site     : %s  (%d absolute reference(s) made local)"
          % (site, len(hits)))
    print("  walk     : %s" % walk)
    print("  addons   : %s" % addons_src)
    print("  lux      : %s" % lux_note)
    if imported is not None:
        print("  import   : exit %d" % imported)
    print()
    print("open it and press F5:")
    print("  godot --path \"%s\"" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failed as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(2)
