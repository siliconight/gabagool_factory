"""Roadmap batch 24, 2026-09-11: item 144 narrowed by Level Factory 0.72.0.
REPLACE mode; old status kept verbatim. Asserts once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON; THE GAP PROTOCOL'S CASE*

**144. The stairs ship in the greybox's fallback yellow.**"""

NEW = """*STATUS: NARROWED 2026-09-11 -- THE CHEAPEST OF THE TWO ANSWERS SHIPPED IN
LEVEL FACTORY 0.72.0 AND MEASURED ON THE WALKED COPY; NOT YET RE-EXPORTED OR
RE-WALKED. `zoo_worldskin.gd` runs a second pass on `site_base*.glb` --
reachable at all only since 0.71.0 declared the script project-wide (item
141): every visual `stair<n>_*` mesh gets one `M_Skin_concrete_stairs`,
the concrete albedo/roughness Zoo copied beside a plain `wall_*` module
under `art/zoo/`, world-triplanar at that module's own imported
`uv1_scale`, so the stair's texel density is the wall's. No UVs needed,
which is the point of world projection on boxes nobody unwrapped. Measured
on the walked copy, base sidecar regenerated: 76 stair surfaces on 76
meshes skinned, 0 flat, `uv1_scale` 0.49999 read from
`wall_delco_1997_01_w200.glb`. REFUTED on the first run, kept: the first
albedo in sort order was `breach_*`'s BREACHED concrete and every stair
wore rubble edges; the script now prefers a plain wall's. RESIDUE: the
look-shot at the public stair is 75-84% crushed -- the stairwell is unlit,
which is item 147's finding again (its lamps are the room row's, 4.0 m
reach), so whether the concrete reads on the treads is for the re-walk;
the `floor_hole` link is still unmarked; and a Zoo stair species built to
DC's flight geometry remains the dearer, better answer. EARLIER STATUS,
KEPT VERBATIM: OPEN 2026-09-11 -- FOUND BY A PERSON; THE GAP PROTOCOL'S
CASE*

**144. The stairs ship in the greybox's fallback yellow.**"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(OLD, NEW, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); item 144 narrowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
