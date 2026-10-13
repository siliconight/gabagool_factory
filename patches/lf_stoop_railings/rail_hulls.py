"""The stoop's and its railings' collider hulls on a built rowhome shell, as Level Factory's reader gives them.

Level Factory 0.197.0's evidence: `glb_collision.collision_solids` (the reader `street_line.shell_extents`
measures with) on Deli Counter 0.212.0's built `gs_empty_rowhome_*.glb`. Prints every `stoop*` solid --
its name, centre and size in glTF metres (x, height, z; site y = -z) -- then the shell's extent read
whole, with 0.195.0's three prefixes skipped, and with `STOOP_COLLIDERS` as this checkout has it. Prints
what it measured and stops.

    python patches/lf_stoop_railings/rail_hulls.py deli_counter/build/gs_empty_rowhome_a.glb [...]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "level_factory"))

from packages.pipeline import street_line  # noqa: E402
from packages.validation import glb_collision  # noqa: E402

THREE = ("stoop_landing", "stoop_under_", "stoop_ramp")


def main(paths):
    for p in paths:
        reading = glb_collision.collision_solids(Path(p))
        print("%s: read %s, %d solids" % (Path(p).name, reading.read, len(reading.solids)))
        for s in sorted(reading.solids, key=lambda s: s.name):
            if s.name.startswith("stoop"):
                print("  %-36s centre (%8.4f, %7.4f, %7.4f)  size (%6.4f, %6.4f, %6.4f)"
                      % ((s.name,) + tuple(s.centre) + tuple(s.size)))
        whole = street_line.shell_extents(p)
        three = street_line.shell_extents(p, skip=THREE)
        now = street_line.shell_extents(p, skip=street_line.STOOP_COLLIDERS)
        fmt = "  %-44s x %8.4f .. %8.4f  y %8.4f .. %8.4f"
        print(fmt % (("whole",) + tuple(whole)))
        print(fmt % (("skip 0.195.0's three",) + tuple(three)))
        print(fmt % (("skip STOOP_COLLIDERS %s" % (street_line.STOOP_COLLIDERS,),) + tuple(now)))


if __name__ == "__main__":
    main(sys.argv[1:])
