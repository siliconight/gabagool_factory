"""Roadmap 173, 2026-10-16 morning: the re-measure on cold run 9318 (the office's pit gone: 59 -> 46 unguarded,
all declared or deliberate), the declared set shipped as nav links across three repos (Deli Counter 0.226.0,
Lot 0.125.0, Dispatch 0.5.3), ladders resolved in the flood, the unnamed collider named. The status stays
NARROWED; its 'Left, in order' list shrinks to the gate. Anchored on the sentence `patch_roadmap_173_dc0225.py`
wrote (asserted once). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_173_links.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("The re-measure on a fresh package is cold run 9318, staged. Left, in order: the declared "
       "set read off the package's records and emitted as `walk_off_ledge` links in Dispatch's `navigation_hints`; "
       "the gate in Level Factory, seeded as the instrument is, surfaces read by owner with the toolchain's names "
       "(`sort_edges.py` `_floor_like`), the residue frozen (178's pattern); ladders in the flood; one unnamed "
       "collider (`GreyboxBase/@StaticBody3D@19803`, 1.05 m up in both mission buildings).")
NEW = ("RE-MEASURED on cold run 9318 (0 interventions, the same pick and grade as 9317; "
       "`docs/cold_runs/cold_9318/NOTES.md`): 921 drops, 872 guarded, 46 unguarded, all indoors -- the office's "
       "13 pit rows gone and nothing new; what stands is 10 at three flights' first metre (0.52-1.30 m, "
       "deliberate), 13 at the two ladder hatches, 16 at the deli's `floor_hole` link, 4 at recorded cuts, 3 on a "
       "rail's top. THE DECLARED SET SHIPS AS LINKS: Deli Counter 0.226.0 files a one-way `nav_link` on every "
       "`floor_hole` / `hatch` vertical link (`ladder.drop_nav_link`: the ladder link's shape, "
       "`required_capability` 'drop', the cut's rect as `hole`), Lot 0.125.0 moves its points into site space "
       "with the building (`_ladder_to_site` parametrised), Dispatch 0.5.3 reads it from both importers into "
       "`navigation_hints.json` `links[]`; the package proof is the next cold run. The instrument resolves a "
       "link's end to the nearest free surface in the ring of cells around it (both ladders were unresolved on "
       "an occupied foot cell). The unnamed collider is the VAULT LEDGE (`VAULTLEDGE_n`, DC 0.215.0's routed "
       "vault): the collider and its marker empty share a base name, so Godot auto-names the body; a prop top "
       "either way. Left: the gate in Level Factory, seeded as the instrument is, the declared set read off the "
       "package's links and stair footprints, surfaces by owner with the toolchain's names (`sort_edges.py` "
       "`_floor_like`), the residue frozen (178's pattern).")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert text.count(OLD) == 1, f"anchor found {text.count(OLD)} times"
    RM.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("roadmap 173: re-measured on 9318, the declared set ships as links; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
