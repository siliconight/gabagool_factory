"""What the v0.19 reference-plane fix moved, per dressing family.

WHAT THIS IS FOR. Four dressing families are placed by phrases that each name a
reference plane -- "the foot of each wall", "where walls meet the ground",
"above exterior doors". Three of them were measured against the wrong plane
because a wall segment is bucketed by wall PLANE, so every storey of a facade
collapses into one row running from the bottom of the foundation to the top of
the parapet. This prints the OLD rule and the NEW rule side by side on a real
shell, so the change is a number rather than a claim.

    python tools\\anchor_planes_diff.py <shell.glb> [<shell.glb> ...]

Run it from the Patina repo so `patina` imports. The shell needs its DC
siblings (`<name>.slots.json`, `<name>.lights.json`) next to it -- that is how
the pipeline ships them, and without them there is nothing to compare.

MISLABELLED FIRST DRAFT, kept because the wrong column was easy to believe.
The first version produced its "OLD" column by calling the NEW generator with
empty options. That works for the ground families, whose fallback really is the
old rule -- but not for conduit, where the new code emits nothing without a
light manifest, so the column read `0` and looked like the old rule had
produced no conduit. It had produced 27, at 5.67 m. The old rule is now
evaluated explicitly from the segment table instead of being approximated by a
degraded call.

WHAT IT MEASURES, AND IN WHAT FRAME. Segments and both rules are evaluated in
the canonical Z-up view the placement math runs in. `blender_to_canonical` is
checked on the way past: for a DC export the vertical coordinate is unchanged
between DC's Blender Z-up manifests and this frame, which is what lets a ground
plane come straight off the slot manifest with no conversion.

WHAT A NONZERO EXIT MEANS. Nothing was measured -- unreadable file, or no
exterior-wall faces. An absent manifest is reported as absent, never as "no
change".
"""
import sys

from patina import anchors, gltf_io, slots, surfaces

#: anchor kind -> the Zoo cover it becomes, so the table names what you SEE.
COVER = {"roofline": "edge_strip", "wall_base": "base_course",
         "exterior_light": "conduit_run", "ground_edge": "curb"}


def old_rule(segs, opts):
    """The pre-v0.19 heights, evaluated from the segment table.

    Written out rather than obtained by degrading the new generator: the two
    differ for conduit, and a column that quietly means something else is worse
    than no column.
    """
    out = {k: [] for k in anchors.ANCHOR_KINDS}
    for s in segs:
        n = len(anchors._points_along(s["a_min"], s["a_max"],
                                      opts.roofline_spacing))
        out["roofline"] += [s["z_hi"]] * n
        n = len(anchors._points_along(s["a_min"], s["a_max"],
                                      opts.wall_base_spacing))
        out["wall_base"] += [s["z_lo"]] * n
        n = len(anchors._points_along(s["a_min"], s["a_max"],
                                      opts.ground_spacing))
        out["ground_edge"] += [s["z_lo"]] * n
        n = len(anchors._points_along(s["a_min"], s["a_max"],
                                      opts.light_spacing))
        out["exterior_light"] += [s["z_lo"] + 0.75 * (s["z_hi"] - s["z_lo"])] * n
    # the same per-kind budget the real pass applies
    return {k: v[:opts.max_per_kind] for k, v in out.items()}


def span(vals):
    return "%3d  %6.2f..%6.2f" % (len(vals), min(vals), max(vals)) if vals \
        else "%3d       --     " % 0


def report(path):
    scene = gltf_io.load_glb(path)
    scene.bake_visual_transforms()
    up = slots.detect_up_axis(scene)
    surfaces.classify(scene, up_axis=up)
    manifest = slots.load(scene)

    print("=" * 72)
    print(path.replace("\\", "/").split("/")[-1])
    print("  slots.json: %-4s  lights.json: %-4s  up_axis: %s"
          % ("yes" if manifest else "NO", "yes" if scene.lights else "NO",
             "XYZ"[up]))

    probe = (7.0, -3.0, 2.45)
    canon = anchors.blender_to_canonical(probe, up)
    print("  frame check: blender %s -> canonical %s   height preserved: %s"
          % (probe, tuple(round(v, 3) for v in canon), canon[2] == probe[2]))

    ground = manifest.storey_base(0) if manifest else None
    targets = anchors.conduit_targets(scene.lights, up)
    print("  story-0 floor plane: %s      exterior fixtures: %d"
          % ("(unknown -- falls back to the wall's lowest point)"
             if ground is None else "%.2f" % ground, len(targets)))

    saved = [(p, p.positions)
             for m in scene.visual_meshes() for p in m.primitives]
    for p, _ in saved:
        p.positions = anchors._up_to_z(p.positions, up)
    try:
        segs = list(anchors._wall_segments(scene))
    finally:
        for p, pos in saved:
            p.positions = pos
    if not segs:
        print("  NO exterior-wall segments -- nothing measured")
        return False

    opts = anchors.AnchorOptions(ground_z=ground, conduit_targets=targets)
    before = old_rule(segs, opts)
    after = anchors.generate(scene, opts, 1999, up)
    vert = up                            # output is back in the scene's frame

    print()
    print("  %-28s %19s   %19s" % ("family (cover)", "OLD", "NEW"))
    for k in anchors.ANCHOR_KINDS:
        now = [a.pos[vert] for a in after if a.kind == k]
        print("  %-28s %19s   %19s"
              % ("%s (%s)" % (k, COVER[k]), span(before[k]), span(now)))

    runs = [a for a in after if a.kind == "exterior_light"]
    if runs:
        print()
        print("  conduit runs (size = ground plane -> fixture):")
        for a in runs:
            print("    %-20s %5.2f m" % (a.tag, a.size))
    return True


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        sys.stderr.write("usage: anchor_planes_diff.py <shell.glb> [...]\n")
        return 2
    ok = 0
    for path in argv:
        try:
            ok += bool(report(path))
        except (OSError, ValueError, KeyError) as exc:
            sys.stderr.write("unreadable: %s: %s\n" % (path, exc))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
