"""Roadmap 173 NARROWED, 2026-10-15: the drop-edge instrument sound and seeded after nine runs on cold run 9317's
package (`docs/findings/drop_edges_173/`), and its first findings that are not its own -- two stairs. Replaces the
status written earlier the same day (which was dated 2026-10-16 by mistake; asserted once). The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_173_narrowed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-10-16 -- the instrument made sound and the residue named: four runs on cold run "
                   "9317's package")
HEADING = "\n\n**173. A drop is either guarded or declared, and today nothing declares one.**"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-15 -- the instrument is sound and seeded, and its first findings that are not its "
    "own are two stairs. Nine runs on cold run 9317's package (`docs/findings/drop_edges_173/`, every run, sort "
    "and probe kept), each repair attributed in the scene by `probe_at.gd` before it was made: the headroom ray "
    "starting inside a wall (2,703 edges), a surface inside a slab (664), a bottomless neighbour (2,090), "
    "furniture and walls read as a drop a storey down because the floor under them was rejected (the 592 indoor "
    "'storey rims' in three places: all 16 probed points), the parapet standing just past where the barrier ray "
    "ends (the 236 roof rims), a column seeing THROUGH a slab once an occupied surface was dropped from it (8), "
    "the capsule overlapping the 40-degree ramp it stands on (every stair ramp in the level occupied, no upper "
    "floor reachable), and two spellings of the neighbour test that cost a true rim (1,382 of the plate's) or "
    "swallowed every guard (7,628 of 7,629 drops unguarded). `tools/walkable_edge.gd` now: a surface is [height, "
    "owner, free], the capsule lifted by the slope's rise across its radius and anything over `floor_max_angle` "
    "45 skipped; the surface a body moves to is the highest within its step-up, and an occupied one is walked "
    "into; then a barrier ray at step-over height, then the body above FALL_M in the next column; a seed (the "
    "package's `player_start`, the getaway van) floods reachability across the same transitions, and only "
    "reached cells are asked; rows carry what they stand on and drop to. Run 9, seeded: 114,992 standable "
    "(22,984 occupied, 4,184 steep), 84,367 reached -- both mission buildings' upper floors and basements in "
    "full, no roof (a ladder is a climb the flood does not make: open) and no Empty's upper floor (doors shut by "
    "design) -- 936 drops, 874 guarded, 3 blocked, 59 unguarded, all indoors: 33 declared by the package's "
    "records (13 at the ladder hatches, 16 `floor_hole` links, 4 recorded cuts), 3 a guard rail's top (excluded "
    "by owner), and 23 on the office's and the deli's stairs, probed: FIVE at the office's storey-2 discharge "
    "landing, open over the well 6.67 m straight down onto the lower flight's foot with nothing between the "
    "cells or in the body's column beyond; SEVEN along its upper flight's inner side, open over the lower flight "
    "1.3-5.9 m below; ELEVEN at the first metre of three flights' open sides, 0.52-1.3 m, the deliberately open "
    "sides this item named. Left, in order: the two office gaps against Deli Counter's `stairwell.py` guard rules "
    "(which sides of a switchback it guards, and its top landing -- rails without colliders or no rails), and a "
    "fix there if real; the declared set read off the package's records and emitted as `walk_off_ledge` links in "
    "Dispatch's `navigation_hints`; the gate in Level Factory, seeded as the instrument is, surfaces read by "
    "owner with the toolchain's names (`sort_edges.py` `_floor_like`), the residue frozen (178's pattern); "
    "ladders in the flood; one unnamed collider (`GreyboxBase/@StaticBody3D@19803`, 1.05 m up in both mission "
    "buildings). The statuses written on the afternoon of 2026-10-15 were dated 2026-10-16 by mistake. Earlier "
    "status kept: 2026-09-23, the instrument exists and cannot yet be a gate -- 121 unguarded cells at the "
    "stairwell the walker stepped off, 2.90 m at floor level, and 5,897 drop edges on a clean package, 1,024 the "
    "deliberately open sides of staircases; a declaration is what separates the two.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "173's status block not found once"
    j = i
    while True:
        k = text.find("\n", j)
        assert k > 0
        if text[i:k].endswith("*"):
            break
        j = k + 1
    old = text[i:k]
    assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "173's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 173 updated (NARROWED, nine runs); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
