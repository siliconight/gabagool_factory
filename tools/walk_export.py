"""Put a body in the EXPORTED package and walk it, in a copy of the package.

    python tools\\walk_export.py <workspace>\\.level_factory <mission-id> [--out DIR]

Then open DIR in Godot and press F5.

WHY THIS EXISTS, and why it is not the same as the other two walkers.
`walk_greybox.py` walks what Deli Counter built; `walk_themed.py` walks the
site after Zoo has dressed it. Both run inside the factory's own scratch, with
Lot's harness scene and the tool repos on disk. **Neither of them is the
deliverable.** The portable export is: a self-contained Godot project with no
addons, gl_compatibility, its own renderable-lights budget, and the Lux-applied
scene as its content. If the shipped package behaves differently from the walk
harness -- collision that only exists in Lot's scene, a light budget that hides
half the fixtures, a corner that reads solid in the greybox and is not -- this
is the walk that finds it and the other two cannot.

THE PACKAGE HAS NO PLAYER, ON PURPOSE. `mission.tscn` loads the content and
stops; the walk scene is stripped by contract because the consumer's runtime
brings its own character. So F5 on the export gives a static camera. This
copies the package and adds the smallest possible body to it.

WHAT IT ADDS, all underscore-prefixed so nothing added here can be mistaken
for part of the package:

  * `_walk_player.gd`  -- Lot's `lot_player.gd`, copied verbatim
  * `_walk.tscn`       -- instances `mission.tscn` and puts a CharacterBody3D
                          at the package's OWN `player_start` anchor
  * `project.godot`    -- only `run/main_scene` is changed. Everything else is
                          the package's: the renderer, the lights budget, the
                          warning config. Changing those would make this a
                          walk of a different project.

THE PLAYER RIG IS LOT'S, NUMBER FOR NUMBER: capsule radius 0.35, height 1.8,
`body_height` 1.8, `max_step_height` **0.5**. That last one is the walk
scene's value, not the script's 0.45 default -- `lot_player.gd` says why: "a
default here and a number in the contract are two values for one quantity and
they had already diverged". Using 0.5 here means a corner that catches you in
this walk catches you in the harness walk too, and the comparison is about the
package rather than about two step heights.

WHERE THE SPAWN COMES FROM. `gameplay_anchors.json`, `anchor_type:
player_start` -- the package's own statement of where a player begins, which
is the thing under test. It is NOT Lot's `LT_PlayerSpawn`; those two disagree
(measured on bank_block_001: the anchor says [2.77, 0, -1.29], the walk scene
says [8, 1, 12]) and only one of them ships. `--at x,y,z` overrides.

WHAT THIS IS NOT. Not a deliverable, not shippable, and not written anywhere
the pipeline reads. The copy is contaminated the moment it gains a player;
that is the point, and it is why it is a copy.

WHAT A NONZERO EXIT MEANS. Nothing was assembled.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

_WALK_SCENE = """[gd_scene load_steps={steps} format=3]

[ext_resource type="PackedScene" path="res://mission.tscn" id="mission"]
[ext_resource type="Script" path="res://_walk_player.gd" id="player"]
[ext_resource type="Script" path="res://debug_overlay.gd" id="debug_overlay"]
[ext_resource type="Script" path="res://_walk_ladders.gd" id="walk_ladders"]
{drip_res}
[sub_resource type="CapsuleShape3D" id="PlayerCol"]
radius = 0.35
height = 1.8

[node name="_walk" type="Node3D"]

[node name="Mission" parent="." instance=ExtResource("mission")]

[node name="Player" type="CharacterBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})
script = ExtResource("player")
max_step_height = 0.5
body_height = 1.8

[node name="col" type="CollisionShape3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.9, 0)
shape = SubResource("PlayerCol")

[node name="Camera" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)
{headlamp}
[node name="DebugOverlay" type="Node" parent="."]
script = ExtResource("debug_overlay")

[node name="WalkLadders" type="Node" parent="."]
script = ExtResource("walk_ladders")
{drip_node}"""

#: LADDER CLIMB VOLUMES for the walk copy (`tools/walk_ladders.gd`). The
#: package carries ladder MARKERS; the Area3D a body climbs is the consumer's
#: to build, Lot's walk scene builds it, and this tool never did -- so every
#: ladder in every walk copy was scenery until the walker could not climb one
#: on 2026-09-13.
_LADDERS_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "walk_ladders.gd")

#: LEVEL FACTORY'S debug overlay -- position, the building under the
#: crosshair, the collider looked at and its distance; F3 toggles, on by
#: default. Read from LF rather than copied into this file, the way
#: `walk_themed.py` carries it, so the two walk tools cannot show different
#: things. This tool shipped without it until 2026-09-13, when the walker's
#: first in-game feedback round asked "didnt we have a debug overlay that
#: showed coordinates" -- every defect that round arrived as a picture that
#: had to be located by hand. It rides in the walk copy only; the package is
#: never touched.
_OVERLAY_SRC = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "level_factory", "assets", "godot",
    "debug_overlay.gd")

#: RAIN RUNNING DOWN THE WALLS, staged into the walk copy only.
#:
#: The fragment was priced before this flag existed (LF 0.116.0): +1.85 ms at
#: the worst of six stations for 19 wall material resources -- all of them
#: brick on the package that was measured (0.117.0) -- with draw calls up at
#: 6 of 6 and the frame's luminance CHANGED at 5 of 6. The walker's
#: call on that number was that it is affordable enough to walk, which is what
#: this is -- a look, not an approval. No package the factory builds carries
#: drips; when the look is approved the attachment belongs in the presentation
#: compose step, gated on the brief's weather the way the wet ground is.
#:
#: Its shader and atlas come from `level_factory/tools/drip_assets.py`, the
#: same stager the MEASUREMENT uses, so this walk shows the fragment that was
#: measured rather than a second copy of it.
_DRIP_RES = ('[ext_resource type="Script" path="res://rain_drip.gd" '
             'id="rain_drip"]\n')
_DRIP_NODE = """
[node name="RainDrip" type="Node" parent="."]
script = ExtResource("rain_drip")
"""

_DRIP_STAGER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "level_factory", "tools")

_HEADLAMP = """
[node name="Headlamp" type="SpotLight3D" parent="Player/Camera"]
light_energy = 2.0
spot_range = 18.0
spot_angle = 55.0
"""

_MAIN_SCENE = re.compile(r'\s*run/main_scene\s*=')

#: WHY THE IMPORT PASS IS NOT OPTIONAL, and why it used to be.
#:
#: A Godot project keeps two things in `.godot/` that a copied tree does not
#: carry: the imported form of every asset, keyed by UID, and the global
#: `class_name` registry. Without it the copy does not merely look wrong --
#: it does not load at all, and it says so in a way that names the wrong
#: culprit. Walked on 2026-09-16 (cold run 9061's card block), an unimported
#: copy printed 20+ parse errors of the shape `Could not find type
#: "LuxLightRig"` from Lux's own runtime rigs, then `[ext_resource]
#: referenced non-existent resource at: res://skins/asphalt_delco_albedo.png`
#: -- a file that WAS on disk, beside the scene that could not find it --
#: then `Failed loading resource: res://presentation/lux.applied.tscn`, and
#: the walker dropped through an empty scene to y = -94.8 with "nothing
#: within 60 m". Every one of those reads as a broken package. The package
#: was fine.
#:
#: This tool has always known: `--godot` ran exactly this pass. It was
#: opt-in, defaulted to None, and the copy is unusable without it -- so the
#: flag was the whole feature wearing a switch. It is the default now, and
#: `--no-import` is the deliberate act, which is the arrangement the rest of
#: this repo uses for a step an artefact cannot be correct without.
_NO_GODOT = """
[walk_export] NO GODOT BINARY FOUND, so the copy was NOT imported.
  It will not load as it stands: every class_name type parses as unknown and
  every texture reads as a non-existent resource until .godot is built.
  Set DC_GODOT, or pass --godot, or run this once yourself:
      godot --headless --path %s --import
"""


def _find_godot(explicit):
    """The Godot binary and where it came from, or (None, "").

    Same order the rest of the toolchain uses: an explicit flag, then
    DC_GODOT (which `check.py` and the nav gate already read), then GODOT,
    then whatever is on PATH. Returns the source too, because "which Godot
    imported this" is the first question when a walk behaves oddly.
    """
    if explicit:
        return explicit, "--godot"
    for var in ("DC_GODOT", "GODOT"):
        val = os.environ.get(var)
        if val and os.path.exists(val):
            return val, var
    for name in ("godot", "Godot_v4.7-stable_win64_console.exe"):
        found = shutil.which(name)
        if found:
            return found, "PATH"
    return None, ""


def player_start(export_dir):
    """The package's own player_start anchor, or None."""
    path = os.path.join(export_dir, "gameplay_anchors.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    for a in data.get("anchors", []):
        if a.get("anchor_type") == "player_start":
            pos = (a.get("transform") or {}).get("pos")
            if isinstance(pos, list) and len(pos) == 3:
                return [float(v) for v in pos], str(a.get("node", ""))
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="walk the exported package with a body in it")
    ap.add_argument("lf_dir", help="the workspace's .level_factory directory")
    ap.add_argument("mission_id")
    ap.add_argument("--mode", default="portable-godot")
    ap.add_argument("--out", default=None, help="where to assemble (scratch)")
    ap.add_argument("--at", default=None,
                    help="spawn as x,y,z -- overrides the package's anchor")
    ap.add_argument("--lift", type=float, default=1.0,
                    help="metres added to the ANCHOR's Y so the capsule is not "
                         "half in the floor (anchors sit at grade). Ignored "
                         "with --at: if you named a point, that is the point")
    ap.add_argument("--headlamp", action="store_true",
                    help="add a spotlight to the camera. OFF by default: the "
                         "package's own lighting is part of what you are here "
                         "to judge, and a headlamp hides a level that ships dark")
    ap.add_argument("--drip", action="store_true",
                    help="run rain down the walls. OFF by default and NOT "
                         "part of any package: this stages Level Factory's "
                         "rain_drip.gd, its shader and Pixelcoat's drop atlas "
                         "into the copy so the look can be judged. Priced at "
                         "+1.85 ms worst-station for 19 wall material "
                         "resources, all brick on the package measured "
                         "(LF 0.117.0); adding patterns is a performance "
                         "change, not a setting")
    ap.add_argument("--pixelcoat", default=None,
                    help="pixelcoat checkout the drop atlas is generated "
                         "from. Only read with --drip")
    ap.add_argument("--lot-repo", default=None)
    ap.add_argument("--godot", default=None,
                    help="the Godot binary to run the import pass with. "
                         "Found from DC_GODOT / GODOT / PATH when not given")
    ap.add_argument("--no-import", action="store_true",
                    help="skip the import pass. The copy will NOT load: every "
                         "class_name type parses as unknown and every texture "
                         "reads as a non-existent resource until .godot exists")
    args = ap.parse_args(argv)

    export_dir = os.path.join(args.lf_dir, "exports",
                              f"LF_{args.mission_id}.{args.mode}")
    if not os.path.isdir(export_dir):
        sys.stderr.write(
            f"no export at {export_dir}\nRun: level-factory export "
            f"{args.mission_id} --mode {args.mode}\n")
        return 2
    if not os.path.exists(os.path.join(export_dir, "mission.tscn")):
        sys.stderr.write(f"{export_dir} has no mission.tscn -- not a portable "
                         f"export.\n")
        return 2

    # Lot's player, from the repo. The package deliberately does not ship one.
    lot_repo = args.lot_repo
    if not lot_repo:
        ws_root = os.path.dirname(os.path.abspath(args.lf_dir.rstrip("\\/")))
        for cand in (os.path.join(ws_root, "tools.local.json"),
                     os.path.join(args.lf_dir, "tools.local.json")):
            if os.path.exists(cand):
                try:
                    with open(cand, encoding="utf-8") as fh:
                        lot_repo = (json.load(fh).get("repositories") or {}
                                    ).get("lot")
                except (OSError, ValueError):
                    pass
                if lot_repo:
                    break
    player_src = os.path.join(str(lot_repo), "godot", "addons", "lot",
                              "lot_player.gd") if lot_repo else None
    if not player_src or not os.path.exists(player_src):
        sys.stderr.write(
            "cannot find Lot's lot_player.gd -- pass --lot-repo <lot checkout>. "
            "The package ships no player by contract, so without one this walk "
            "would open on a frozen camera and look like a level defect.\n")
        return 2

    if args.at:
        try:
            pos = [float(v) for v in args.at.split(",")]
            assert len(pos) == 3
        except (ValueError, AssertionError):
            sys.stderr.write("--at wants x,y,z\n")
            return 2
        origin = "--at"
        args.lift = 0.0          # you named a point; that is the point
    else:
        found = player_start(export_dir)
        if not found:
            sys.stderr.write(
                "the package has no player_start anchor in "
                "gameplay_anchors.json, so there is nowhere it says a player "
                "begins. Pass --at x,y,z.\n")
            return 2
        pos, node = found
        origin = node or "player_start"
    pos = [pos[0], pos[1] + args.lift, pos[2]]

    out = args.out or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "_runs", f"walk_export_{args.mission_id}")
    real_out = os.path.abspath(out)
    if os.path.abspath(args.lf_dir) + os.sep in real_out + os.sep:
        sys.stderr.write(
            "refusing to assemble inside the workspace (%s).\nThis copy gets a "
            "player added to it and is no longer the package; keep it out of\n"
            "anywhere the pipeline reads. Try _runs\\walk_export.\n" % out)
        return 2
    if os.path.abspath(export_dir) == real_out:
        sys.stderr.write("refusing to write into the export itself -- that "
                         "would contaminate the deliverable.\n")
        return 2

    if os.path.isdir(out):
        try:
            shutil.rmtree(out)
        except OSError as exc:
            sys.stderr.write("cannot rebuild %s: %s\nClose Godot and retry.\n"
                             % (out, exc))
            return 2
    shutil.copytree(export_dir, out)
    shutil.copy2(player_src, os.path.join(out, "_walk_player.gd"))
    if not os.path.isfile(_OVERLAY_SRC):
        sys.stderr.write("Level Factory's debug overlay is not at %s -- refusing "
                         "to assemble a walk copy that cannot say where a defect "
                         "is.%s" % (_OVERLAY_SRC, os.linesep))
        return 2
    shutil.copy2(_OVERLAY_SRC, os.path.join(out, "debug_overlay.gd"))
    shutil.copy2(_LADDERS_SRC, os.path.join(out, "_walk_ladders.gd"))

    drip_staged = []
    if args.drip:
        # STAGED THROUGH LEVEL FACTORY'S OWN STAGER, not copied here. It owns
        # the atlas size and seed, and a walk judging a different texture from
        # the one that was measured would be judging an unpriced look.
        sys.path.insert(0, _DRIP_STAGER)
        try:
            import drip_assets
            drip_staged = drip_assets.stage(out, args.pixelcoat, node=True)
        except (ImportError, OSError, SystemExit) as exc:
            sys.stderr.write(
                "--drip could not stage its assets: %s\nThe copy is "
                "assembled WITHOUT drips rather than with a shader that "
                "samples nothing.%s" % (exc, os.linesep))
            args.drip = False

    # ONLY the main scene changes, and the file's LINE ENDINGS are preserved
    # byte for byte. The export ships CRLF; reading and rewriting through
    # Python's default translation turned all 24 lines into LF -- which on
    # Windows would have round-tripped by accident (os.linesep) and hidden
    # itself until someone ran this against an LF package. Rewriting a
    # deliverable's whole file to change one line is not a one-line change.
    pg = os.path.join(out, "project.godot")
    with open(pg, encoding="utf-8", newline="") as fh:
        lines = fh.readlines()
    eol = "\r\n" if any(l.endswith("\r\n") for l in lines) else "\n"
    replaced = False
    for i, line in enumerate(lines):
        if _MAIN_SCENE.match(line.rstrip("\r\n")):
            lines[i] = 'run/main_scene="res://_walk.tscn"' + eol
            replaced = True
            break
    if not replaced:
        for i, line in enumerate(lines):
            if line.strip() == "[application]":
                lines.insert(i + 1,
                             'run/main_scene="res://_walk.tscn"' + eol)
                replaced = True
                break
    if not replaced:
        sys.stderr.write("project.godot has no [application] section and no "
                         "run/main_scene -- not a Godot project.\n")
        return 2
    with open(pg, "w", encoding="utf-8", newline="") as fh:
        fh.writelines(lines)
    text = "".join(lines)

    # The walk scene takes the package's line endings too, so a diff of this
    # directory against the export shows content and not whitespace.
    # `load_steps` counts the resources the scene loads: 4 ext + 1 sub, and
    # one more ext when the drip rides along. It is a progress hint rather
    # than a contract, which is exactly why a stale one goes unnoticed.
    scene = _WALK_SCENE.format(x=pos[0], y=pos[1], z=pos[2],
                               steps=7 if args.drip else 6,
                               drip_res=_DRIP_RES if args.drip else "",
                               drip_node=_DRIP_NODE if args.drip else "",
                               headlamp=_HEADLAMP if args.headlamp else "")
    if eol == "\r\n":
        scene = scene.replace("\n", "\r\n")
    with open(os.path.join(out, "_walk.tscn"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write(scene)

    imported = None
    godot, how = (None, "") if args.no_import else _find_godot(args.godot)
    if godot:
        try:
            proc = subprocess.run(
                [godot, "--headless", "--path", out, "--import"],
                capture_output=True, timeout=900)
            imported = proc.returncode
            if imported != 0:
                sys.stderr.write("import pass exited %d; open the project once "
                                 "in the editor before walking.\n" % imported)
        except (OSError, subprocess.SubprocessError) as exc:
            sys.stderr.write("import pass did not run: %s\n" % exc)
    elif not args.no_import:
        sys.stderr.write(_NO_GODOT % out)

    budget = ""
    m = re.search(r"max_renderable_lights\s*=\s*(\d+)", text)
    if m:
        budget = "  lights   : package budget %s (its own, not raised)\n" % m.group(1)
    print("[walk_export] assembled " + os.path.abspath(out))
    print("  from     : " + os.path.basename(export_dir))
    print("  spawn    : %.3f, %.3f, %.3f   (%s, +%.2f lift)"
          % (pos[0], pos[1], pos[2], origin, args.lift))
    print("  overlay  : Level Factory's debug_overlay.gd (F3 toggles; position, "
          "building, surface)")
    print("  player   : Lot's lot_player.gd as _walk_player.gd  "
          "(capsule 0.35 x 1.8, step 0.5)")
    sys.stdout.write(budget)
    print("  renderer : the package's own")
    if args.drip:
        print("  drip     : ON -- %s" % ", ".join(drip_staged))
        print("             +1.85 ms worst-station measured for 19 wall "
              "materials (LF 0.117.0; all brick on that package).")
        print("             THE PACKAGE HAS NO DRIPS. This is staged into the "
              "copy to be looked at.")
    if imported is not None:
        print("  import   : exit %d  (%s)" % (imported, how))
    elif args.no_import:
        print("  import   : SKIPPED (--no-import). This copy will not load "
              "until\n  something builds its .godot cache.")
    if not args.headlamp:
        print("  no headlamp: you are walking the package's lighting. If it is "
              "too dark to\n  judge, --headlamp, but note that a level too dark "
              "to walk IS a finding.")
    print("  THIS COPY IS NOT THE PACKAGE. It has a player in it. The export "
          "itself\n  is untouched; ship that one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
