"""Roadmap 173 CLOSED, 2026-10-18: the drop-edge gate ships in Level Factory (0.216.0, 8520801), its first export
refused a package for the right reason (cold run 9320: the declared drops' links stopped at Level Factory's own
staging), Level Factory 0.216.1 (c62b873) staged them, and cold run 9321's package carries them and passes the gate
with 0 undeclared. The status line is replaced whole: the closing evidence first, with figures, what is not
proven, and the NARROWED 2026-10-15 status kept after it verbatim. Anchored on that line's sha256 and on the item
heading below it (asserted once). The index is NOT touched here: run `python tools/roadmap_status.py --write`
then `--check` after it.

    python patches/patch_roadmap_173_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD_PREFIX = "*STATUS: NARROWED 2026-10-15 -- "
OLD_SHA256 = "3fc3b0231364132c642d584dc2b77918911c7e126f1ab9f1c910613983288e3d"
HEADING = "**173. A drop is either guarded or declared, and today nothing declares one.**"

CLOSED = (
    "*STATUS: CLOSED 2026-10-18 -- the gate exists, and its zero is real on a package that declares its drops. "
    "Level Factory 0.216.0 (8520801, `patches/patch_lf_drop_edge_gate.py`) runs its own copy of "
    "`tools/walkable_edge.gd` at export step 4.88: seeded from the package's `player_start`, flooding across "
    "steps, falls and the package's links, its grid bounded by the nav nodes plus 12 m and snapped to the cell "
    "lattice (341 x 126 cells and 7 s on cold run 9318's package, the same rows as 1,521 a side and 150 s "
    "unbounded). Every unguarded edge goes in the first class that claims it, off the package's OWN declared "
    "set -- a thing's top, outdoors, a flight's own side, a drop link's `hole`, a ladder's shaft from foot to "
    "head -- and an undeclared drop indoors is REFUSED (`ExportProfile.require_declared_drops`, default on; a "
    "package with no `player_start` is NOT TAKEN and says so). No baseline is frozen, unlike the plan below: on "
    "a package that declares its drops the residue is zero. Its first engine run, on 9318's package, refused 27: "
    "20 at deli_a01's floor hole, which that package predates the links for, and 7 where the deli's roof ladder "
    "passes the first floor, because the first draft asked for a ladder's ENDS only -- refuted, kept, replaced "
    "by the shaft rule (`docs/findings/drop_edges_173/gate_probe_9318.out.txt`, `gate_reclass_9318.out.txt`). "
    "ITS FIRST EXPORT REFUSED THE PACKAGE, CORRECTLY: cold run 9320 (0 interventions, seed 9104 PASS 100) "
    "stopped at the export on those 20 rows with the package's links reading climb 2, drop 0. Traced hop by "
    "hop, Level Factory's `stage_dispatch_inputs` wrote Dispatch's inputs from a whitelist without "
    "`vertical_links`, so the status below's THE DECLARED SET SHIPS AS LINKS held in each repo and not end to "
    "end -- the ladders' 9075/9076 seam, one record over. Level Factory 0.216.1 (c62b873, "
    "`patches/patch_lf_stage_vertical_links.py`) stages the key on both sides, with a test that both staged "
    "manifests carry every key Dispatch 0.5.3's importers read. PROVEN on cold run 9321 (0 interventions, seed "
    "9104 PASS 100, findings 109 -> 109; `docs/cold_runs/cold_9321/NOTES.md`): the package's "
    "`navigation_hints.json` carries 2 one-way drop links with their holes and 2 climbs; the gate counts 54 "
    "unguarded -- 10 a flight's own side, 20 at a declared drop, 13 at a ladder's shaft, 3 a rail's top, 8 "
    "outdoors -- and 0 UNDECLARED, and the export ships with `drop_edges.json` and `drop_edges_scan.json` in its "
    "manifest and the closure verdict clean. The factory's instrument unbounded on the same package finds the "
    "same 54 rows, and `sort_edges.py`'s `declared_link` class claims the 20 off the package's links. Not "
    "proven: the flood resolves neither drop link (a drop link starts over its hole), so a floor reachable only "
    "by a drop would go unasked; and the lattice fragility (one turn landing lost to a centimetre's offset) has "
    "no sweep yet -- both are items 6 and 7 of the finding's What is left. Earlier status kept: NARROWED "
    "2026-10-15 -- ")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(OLD_PREFIX)
            and hashlib.sha256(l.encode("utf-8")).hexdigest() == OLD_SHA256]
    assert len(hits) == 1, f"the NARROWED 2026-10-15 status line found {len(hits)} times"
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2] == HEADING, "the status no longer adjoins item 173's heading"
    old = lines[i]
    assert old.endswith("*")
    lines[i] = CLOSED + old[len(OLD_PREFIX):]
    assert lines[i].startswith("*STATUS: CLOSED 2026-10-18 -- ") and lines[i].endswith("*")
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 173 CLOSED (gate 0.216.0 + staging 0.216.1, proven on cold run 9321); now roadmap_status.py "
          "--write / --check")


if __name__ == "__main__":
    sys.exit(main())
