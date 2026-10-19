"""Read a `.tscn` `Transform3D(...)` the way Godot 4.7 does: the basis's three ROWS, then the origin.

THE ONE READER FOR THE FACTORY'S TOOLS (2026-10-19, roadmap 177's defect class). Five tools here read the twelve
numbers as the basis's COLUMNS -- `site_fights`, `insert_overhang`, `light_check`, `module_extents` and
`repetition_census` -- and so did Deli Counter's z-fight gate (fixed in Deli Counter 0.230.0), Level Factory's
ground-contact pre-flight (0.218.2), and Lot's collision reader until Lot 0.72.1. Godot writes and parses rows,
measured three times off the engine:

  * Deli Counter on cold run 9013 (`tscn_export.godot_basis`, 0.120.1): wall remainders read as columns stood
    across their walls;
  * Lot's `str_to_var` on 2026-09-13 (`lot/site_furniture.plate_facing`): `Transform3D(c, 0, s, 0, 1, 0, -s, 0,
    c, ...)` at 30 degrees sends local +X to world (0.866, 0, -0.5);
  * `tools/module_pose_census.py` on cold run 9324's deli_a01 (`docs/findings/zfight_rows_177/`): `ext_0_E_seg10`,
    written `Transform3D(0, 0, -0.35, 0, 3, 0, 0.6, 0, 0, 19, 1.496, -6)`, stands x 18.825..19.175 and z
    -6.300..-5.700 -- 0.35 m through its wall and 0.6 m along it.

Read as columns, a pure turn comes out turned the other way, which a box centred on its own origin cannot show;
a turned AND non-uniformly scaled module comes out with two extents swapped, and a point off a turned
instance's origin lands mirrored about it. Per-axis scale is the length of each COLUMN of the matrix -- where
the basis sends the module's own x, y and z -- and the length of each written triplet is a row's, which swaps
x and z for every quarter-turned module.
"""


def floats(text):
    """The twelve reals of a ``Transform3D(...)`` argument list (or of a ``transform = Transform3D(...)`` line)."""
    s = str(text)
    if "(" in s:
        s = s[s.index("(") + 1:s.rindex(")")]
    return [float(v) for v in s.split(",")]


def matrix(f):
    """The 3x4 row-major matrix ``[[r00, r01, r02, ox], ...]`` from the twelve numbers as written."""
    if len(f) != 12:
        raise ValueError("a Transform3D has 12 numbers, got %d" % len(f))
    return [[f[0], f[1], f[2], f[9]],
            [f[3], f[4], f[5], f[10]],
            [f[6], f[7], f[8], f[11]]]


def apply(m, p):
    """``m`` (3x4) applied to the point ``p``."""
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3] for i in range(3))


def axis(f, k):
    """Where the basis sends the module's own axis ``k`` (0 x, 1 y, 2 z): the matrix's column ``k``."""
    return (f[k], f[3 + k], f[6 + k])


def scales(f):
    """Per-axis scale: the length of each column, the module's own x, y and z."""
    return tuple(sum(c * c for c in axis(f, k)) ** 0.5 for k in range(3))


def box(f, lo, hi):
    """The world AABB ``(lo, hi)`` of the local box ``lo..hi`` under the transform ``f``."""
    m = matrix(f)
    pts = [apply(m, (x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]
