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

_WALK_SCENE = """[gd_scene load_steps=4 format=3]

[ext_resource type="PackedScene" path="res://mission.tscn" id="mission"]
[ext_resource type="Script" path="res://_walk_player.gd" id="player"]

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
{headlamp}"""

_HEADLAMP = """
[node name="Headlamp" type="SpotLight3D" parent="Player/Camera"]
light_energy = 2.0
spot_range = 18.0
spot_angle = 55.0
"""

_MAIN_SCENE = re.compile(r'\s*run/main_scene\s*=')


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
    ap.add_argument("--lot-repo", default=None)
    ap.add_argument("--godot", default=None)
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
    scene = _WALK_SCENE.format(x=pos[0], y=pos[1], z=pos[2],
                               headlamp=_HEADLAMP if args.headlamp else "")
    if eol == "\r\n":
        scene = scene.replace("\n", "\r\n")
    with open(os.path.join(out, "_walk.tscn"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write(scene)

    imported = None
    if args.godot:
        try:
            proc = subprocess.run(
                [args.godot, "--headless", "--path", out, "--import"],
                capture_output=True, timeout=900)
            imported = proc.returncode
            if imported != 0:
                sys.stderr.write("import pass exited %d; open the project once "
                                 "in the editor before walking.\n" % imported)
        except (OSError, subprocess.SubprocessError) as exc:
            sys.stderr.write("import pass did not run: %s\n" % exc)

    budget = ""
    m = re.search(r"max_renderable_lights\s*=\s*(\d+)", text)
    if m:
        budget = "  lights   : package budget %s (its own, not raised)\n" % m.group(1)
    print("[walk_export] assembled " + os.path.abspath(out))
    print("  from     : " + os.path.basename(export_dir))
    print("  spawn    : %.3f, %.3f, %.3f   (%s, +%.2f lift)"
          % (pos[0], pos[1], pos[2], origin, args.lift))
    print("  player   : Lot's lot_player.gd as _walk_player.gd  "
          "(capsule 0.35 x 1.8, step 0.5)")
    sys.stdout.write(budget)
    print("  renderer : the package's own")
    if imported is not None:
        print("  import   : exit %d" % imported)
    if not args.headlamp:
        print("  no headlamp: you are walking the package's lighting. If it is "
              "too dark to\n  judge, --headlamp, but note that a level too dark "
              "to walk IS a finding.")
    print("  THIS COPY IS NOT THE PACKAGE. It has a player in it. The export "
          "itself\n  is untouched; ship that one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
