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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lf_dir", help="the workspace's .level_factory directory")
    ap.add_argument("mission_id")
    ap.add_argument("--out", default=None,
                    help="where to assemble (default <lf_dir>/walk/<mission>)")
    ap.add_argument("--lot-repo", default=None,
                    help="Lot checkout, for addons/lot (default: read "
                         "tools.local.json beside the workspace)")
    ap.add_argument("--godot", default=None,
                    help="Godot executable, to run an import pass at the end")
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

    out = args.out or os.path.join(args.lf_dir, "walk", args.mission_id)
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
        shutil.rmtree(out)
    os.makedirs(out)

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

    # 3. The walk scene and Lot's addon.
    shutil.copy2(walk, os.path.join(out, "site_walk.tscn"))
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
