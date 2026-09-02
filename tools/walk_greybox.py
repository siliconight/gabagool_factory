"""Assemble a Godot project you can open and WALK the GREYBOX site in.

    python tools\\walk_greybox.py <workspace>\\.level_factory <mission-id> [--out DIR]

Then open DIR in Godot and press F5.

WHY A SECOND WALKER. `walk_themed.py` walks the site AFTER Zoo has swapped its
modules in, which is what a player sees and the right thing to review most of
the time. It is the wrong thing for judging what Deli Counter BUILT. A corner
post leaves DC as a `wallEnd` slot and comes back from Zoo as
`wallEnd_<theme>_0N.glb`, so a corner that reads wrong in the themed walk
might be DC's geometry or might be Zoo's art, and the themed walk cannot tell
you which. Walking both, in that order, can.

HOW LITTLE THIS DOES, deliberately. Level Factory already stages a complete,
working Godot project for the nav-QA run:
`staging/<mission>.walktest_navqa.candidate.seed_<n>/` holds `site.tscn`,
`site_walk.tscn`, `buildings/shell.glb`, Lot's player and site scripts, and a
`project.godot` -- and every path in those scenes is relative, so unlike the
themed side there is nothing to rewrite. Two things are missing and only two:
the project has no `run/main_scene`, because walktest names its scene on the
command line, and no renderer pin. This copies the directory out and adds
those two lines. It does not assemble a level; it un-hides one.

WHAT IT IS NOT. Not an export, not a deliverable, and not written anywhere the
pipeline reads -- the same refusal `walk_themed.py` learned the hard way, for
the same reason: anything under `.level_factory` is treated as job output and
gets provenance stamped onto it, and then shows up in every instrument that
scans the workspace.

THE STAGING DIRECTORY IS EPHEMERAL. walktest rebuilds it on every run, which
is exactly why this copies rather than pointing you at it. Walk the copy.

WHAT A NONZERO EXIT MEANS. The project was not assembled. It never leaves a
half-built directory reporting success.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

_PROJECT = """; Scratch greybox walk project, assembled by tools/walk_greybox.py.
; Throw it away and rebuild it; nothing reads it back.
config_version=5

[application]
config/name="{name} (greybox walk)"
run/main_scene="res://site_walk.tscn"
config/features=PackedStringArray("4.7")

[editor_plugins]
enabled=PackedStringArray()

; MUST match the shipped export's project.godot, which sets gl_compatibility.
; Without this Godot defaults to forward_plus and the greybox renders under a
; different renderer than both the deliverable and the themed walk -- which
; would make the one comparison this tool exists for a comparison of two
; renderers. (`walk_themed.py` pins the same value for the same reason.)
[rendering]
renderer/rendering_method="gl_compatibility"
"""

# Copied because the walk needs them; everything else in the staging dir is
# either the nav-QA harness or its report.
_SKIP_NAMES = {"site_navqa.tscn", "site_navqa.walktest.json",
               "staging.notes.json", "project.godot"}
_SKIP_DIRS = {".godot"}


def selected_candidate(lf_dir, mission_id):
    """The candidate a human approved, if one has been."""
    marker = os.path.join(lf_dir, "approvals", f"{mission_id}.selected")
    if os.path.exists(marker):
        try:
            with open(marker, encoding="utf-8") as fh:
                return fh.read().strip()
        except OSError:
            pass
    return None


def staging_dirs(lf_dir, mission_id):
    """Every walktest staging directory for this mission, newest first."""
    root = os.path.join(lf_dir, "staging")
    if not os.path.isdir(root):
        return []
    pre = f"{mission_id}.walktest_navqa.candidate."
    found = [os.path.join(root, n) for n in os.listdir(root)
             if n.startswith(pre) and os.path.isdir(os.path.join(root, n))]
    return sorted(found, key=lambda p: os.path.getmtime(p), reverse=True)


def default_out(mission_id, seed):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "_runs", f"walk_greybox_{mission_id}_{seed}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="assemble a walkable GREYBOX project from a workspace")
    ap.add_argument("lf_dir", help="the workspace's .level_factory directory")
    ap.add_argument("mission_id")
    ap.add_argument("--candidate", default=None,
                    help="full candidate id; default is the approved selection, "
                         "else the most recently staged candidate")
    ap.add_argument("--out", default=None, help="where to assemble (scratch)")
    ap.add_argument("--godot", default=None,
                    help="godot executable; runs an --import pass if given")
    args = ap.parse_args(argv)

    dirs = staging_dirs(args.lf_dir, args.mission_id)
    if not dirs:
        sys.stderr.write(
            f"no walktest_navqa staging for {args.mission_id}. Run the mission "
            f"(graybox is enough) first -- the greybox walk is assembled from "
            f"what walktest stages, and nothing has staged it yet.\n")
        return 2

    want = args.candidate or selected_candidate(args.lf_dir, args.mission_id)
    src = None
    if want:
        seed = want.rsplit(".", 1)[-1]          # candidate.seed_7003 -> seed_7003
        for d in dirs:
            if d.endswith("." + seed) or d.endswith("." + want.split(".", 1)[-1]):
                src = d
                break
        if src is None:
            sys.stderr.write(
                f"no staging directory for {want}. Staged candidates:\n")
            for d in dirs:
                sys.stderr.write("   " + os.path.basename(d) + "\n")
            return 2
    else:
        src = dirs[0]
        sys.stderr.write(
            "[walk_greybox] no approved selection; using the most recently "
            "staged candidate. Pass --candidate to choose.\n")

    seed = os.path.basename(src).rsplit(".", 1)[-1]
    walk = os.path.join(src, "site_walk.tscn")
    if not os.path.exists(walk):
        sys.stderr.write(
            f"{src} has no site_walk.tscn -- Lot did not stage a walk scene, "
            f"so there is nothing to walk with.\n")
        return 2

    out = args.out or default_out(args.mission_id, seed)
    real_out = os.path.abspath(out)
    if os.path.abspath(args.lf_dir) + os.sep in real_out + os.sep:
        sys.stderr.write(
            "refusing to assemble inside the workspace (%s).\n"
            "This is throwaway scratch; the pipeline treats anything under\n"
            ".level_factory as job output and stamps provenance on it. Pass\n"
            "--out somewhere outside, e.g. _runs\\walk_greybox.\n" % out)
        return 2

    if os.path.isdir(out):
        try:
            shutil.rmtree(out)
        except OSError as exc:
            sys.stderr.write(
                "cannot rebuild %s: %s\nGodot holds a project's files while it "
                "has it open. Close the editor and run this again, or pass "
                "--out somewhere else.\n" % (out, exc))
            return 2
    os.makedirs(out, exist_ok=True)

    copied = 0
    for name in sorted(os.listdir(src)):
        if name in _SKIP_NAMES or name in _SKIP_DIRS:
            continue
        s, d = os.path.join(src, name), os.path.join(out, name)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
        copied += 1

    with open(os.path.join(out, "project.godot"), "w", encoding="utf-8") as fh:
        fh.write(_PROJECT.format(name=f"{args.mission_id} {seed}"))

    imported = None
    if args.godot:
        # Reported, not swallowed: a silently failed import is how 13 modules
        # lost their sidecars and nobody noticed for a week (roadmap 33).
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

    print("[walk_greybox] assembled " + os.path.abspath(out))
    print("  from     : " + os.path.basename(src))
    print("  entry    : site_walk.tscn   (Lot's player, ladders and spawn)")
    print("  copied   : %d item(s)" % copied)
    print("  renderer : gl_compatibility (same as the export and the themed walk)")
    if imported is not None:
        print("  import   : exit %d" % imported)
    print("  UNTHEMED ON PURPOSE: this is Deli Counter's geometry with no Zoo")
    print("  swap over it. Walk tools\\walk_themed.py next to see what a")
    print("  player gets, and compare.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
