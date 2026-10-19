"""Roadmap 173 and 105, 2026-10-19: the breadth sweep's two stops on the drop-edge gate, both fixed and proven, and
105's next step filed as a proposal.

173 stays CLOSED -- the gate exists and its zero held -- and its status gains the sweep's account in front: one stop
the gate was right about (county_hospital_001's stacked shaft, Deli Counter 0.232.0, cold run 9334) and one that was
its instrument's (a float32 gap at a lattice line, Level Factory 0.219.0, cold run 9335). 105 stays OPEN and points
at `docs/proposals/ROW_ARRANGEMENT.md`. Each status line is replaced at its front only, the earlier status kept after
it verbatim; each is anchored on its line's sha256, with its heading two lines below. The index is NOT touched here:
run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_173_105.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    {
        "item": "173",
        "status_sha": "4bc8326d61facafa3604798cd3423af56154dfac4ea53296b18c22ac2292c9d7",
        "heading": "**173. A drop is either guarded or declared, and today nothing declares one.**",
        "old_prefix": "*STATUS: CLOSED 2026-10-18 -- ",
        "new": (
            "*STATUS: CLOSED 2026-10-18; its first breadth sweep stopped twice, both fixed and proven 2026-10-19 -- "
            "the gate refused two of the six missions it had not yet seen (`docs/findings/breadth_sweep_2026-10-19/`), "
            "once rightly and once on its own instrument. county_hospital_001 (cold run 9329, 0 interventions): 20 "
            "undeclared edges round the elevator shaft's storey-2 hole, 7.2 m above the ground floor. "
            "`presets.hospital` stacks the shaft's holes on every storey and declared only storey 1's, and a declared "
            "rim is keyed on its storey, rightly. Deli Counter 0.232.0 (22f71e05, `patches/patch_dc_hospital_shaft.py`) "
            "declares every hole it stacks and lands a drop on the first floor below that is not cut; cold run 9334 "
            "(0 interventions, seed 9208 PASS 100) reads 40 at declared drops and 0 undeclared. restaurant_row_001 "
            "(cold run 9333, 0 interventions): 3 'undeclared drops' at deli_a03's discharge plate were a 1.7 um "
            "float32 gap between a slab cut and a plate authored flush at site x -64.0, a line of the gate's 0.5 m "
            "lattice, and the ray cast exactly on the line fell through it (`seam_floats.py` off the GLB, "
            "`seam_ulps.gd` off the engine; the reading 'a ray on a flush seam meets neither' refuted, kept). Level "
            "Factory 0.219.0 (c80a7ec, `patches/patch_lf_edge_seam.py`) lays the instrument's lattice 3.1 mm and "
            "2.3 mm off the round coordinates, so no query lands where pieces meet. Through the gate on the sweep's "
            "six packages, the old instrument reproducing each export's own scan: 9333 refuses on 0.218.2 and passes "
            "on 0.219.0, no other verdict moves, and the 38 edge rows that change are each attributed to a query that "
            "sat on a round coordinate. PROVEN on cold run 9335 (restaurant_row_001 from 9333, 0 interventions, seed 9003 "
            "PASS 90): the export ships with 52 unguarded and 0 undeclared, the very rows the A/B predicted off 9333's "
            "package. Still not proven, as before: a drop link in the flood, and how far the "
            "answer moves with the lattice's phase at the cell's own scale (the finding's What is left, items 6 and "
            "7). Earlier status kept: CLOSED 2026-10-18 -- "
        ),
    },
    {
        "item": "105",
        "status_sha": "4c86c9d625de79a071c7ea7d3fb6b06614b1876d144a85f75706a98a79ffa824",
        "heading": "**105. Lot builds one arrangement of buildings, and nothing varies it.**",
        "old_prefix": "*STATUS: OPEN 2026-10-15 -- ",
        "new": (
            "*STATUS: OPEN 2026-10-19 -- PROPOSED, not built: `docs/proposals/ROW_ARRANGEMENT.md` reads why the row "
            "never varies off the code, mapped read-only against Level Factory 0.218.2 and Lot. "
            "`building_library.pick_lot` orders the list anchor first, then the template's families in the guide's "
            "order, and `site_variation.site_placements` lays it west to east, so the objective always stands at the "
            "west end. The turn and the stagger the placer still draws are discarded on a row on purpose: Level "
            "Factory 0.132.0 turns every front door to the through road (`fronts`), and 0.135.0 stands every street "
            "edge on one building line (`street_line`). It files four dials: A, a seeded mirror of the row (Level "
            "Factory; every neighbour pair kept, so no adjacency audit moves); B, the corner building fronting its "
            "cross street; C, a gap in the row; D, the side of the street. It recommends A first, behind `row_order: "
            "seeded | picked` with seeded the default, a call meant to be changed, and B once A's numbers are in. "
            "Earlier status kept: OPEN 2026-10-15 -- "
        ),
    },
]


def _sha(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def main():
    for it in ITEMS:
        assert "@@" not in it["new"], "item %s's status still carries a marker" % it["item"]
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    for it in ITEMS:
        hits = [i for i, l in enumerate(lines) if _sha(l) == it["status_sha"]]
        assert len(hits) == 1, "item %s's status found %d times" % (it["item"], len(hits))
        i = hits[0]
        assert lines[i + 1] == "" and lines[i + 2].startswith(it["heading"]), \
            "the status no longer adjoins item %s's heading" % it["item"]
        old = lines[i]
        assert old.startswith(it["old_prefix"]) and old.endswith("*")
        lines[i] = it["new"] + old[len(it["old_prefix"]):]
        assert lines[i].endswith("*") and not lines[i][1:-1].count("*STATUS:")
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 173 (the sweep's two stops, fixed and proven) and 105 (the proposal) written; now "
          "roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
