"""Roadmap batch 10, 2026-09-11: close 110.

STATUS replaces the block and keeps the old one verbatim inside the new
(batch 5's mechanism). Asserts its anchor and refuses on a miss.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    110: """*STATUS: CLOSED 2026-09-11 -- CONNECTED END TO END, IN THE ORDER THE ITEM
GAVE, AND PROVEN ON A REAL PACKAGE. Level Factory 0.68.0 plans three
art-layer jobs after `themed_site_assemble`: `zoo_clutter_build` (Zoo
`--habitat` over the four species, no collision, then `shape_metrics` on the
result -- the `measure_shapes` capability the adapter had carried since 0.4.0
and the planner had never asked for), `lot_site_surfaces` (`site_surfaces.py
--strict` over the locked candidate's own site spec and assembly), and
`patina_surface_dressing` (the 0.4.0 mode, planned against the THEMED
assembly as its `source`). The curation the item found as untracked scratch
in `_dress/` is `patina/asset_sets/ground_clutter.json` (Patina 0.21.1), and
it drives BOTH ends: the spec builder reads the species off it for the Zoo
build and hands the same file to the dressing pass. The mesh question
`dressing_scene` refused to guess -- how a .glb becomes an addressable Mesh
for a MultiMesh -- is answered once, in `assets/godot/extract_meshes.gd`: a
scratch Godot project imports the clutter GLBs, merges each specimen's
MeshInstance3D nodes into one ArrayMesh with placement baked in, and saves a
bundled `.res`; the export puts them in `dressing/`, writes
`<site>_dressing.tscn`, and the entry scene instances it BESIDE the level,
never inside the locked shell. RUN ON cold-9005-ws (`county_hospital_001`,
seed 9005): clutter built in one Blender pass (4 species, 120-230 vertices
each), surfaces 6 zones / 3 exclusions / 1 of 1 footprints read, Patina
1,094 instances / 144,532 tris / 4 meshes over 5,465.64 m2 (0.20 per m2), 9
placements refused; export ships `county_hospital_001_dressing.tscn` at 4
draw calls, `export_closure_scan` ok with 0 issues, portability PASS with the
scene instantiated and 0 parser errors. THREE THINGS FOUND ON THE WAY, ALL
FIXED: Lot's `--strict` counted its own info line ("footprints merged") as a
failure and failed the first pipeline run of the stage on a clean result
(Lot 0.55.2); the extraction script's first run hung Godot to the caller's
timeout on `global_transform` of a node never added to a tree and a method
that does not exist (`get_surface_arrays`), and the closure scan then read
the diagnostics the report carried (`res://extract_meshes.gd`, a repo path)
as references to resolve -- the report in the package is words now and the
log sits beside it. THE VERSION DRIFT is fixed in the same pass: the adapter
header no longer claims 0.18.0. NOT JUDGED BY A PERSON: nobody has looked at
the dressed site yet, and the instance count (1,094) is one over the planner's
auto budget (1,093), which the audit does not gate on. Both belong to item 18,
where the rest of "does it read as placed" already lives.*""",
}


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    lines = raw.decode("utf-8").split("\n")
    for num, block in STATUS.items():
        heading = re.compile(r"^\*\*%d\. " % num)
        hits = [i for i, l in enumerate(lines) if heading.match(l)]
        if len(hits) != 1:
            print(f"item {num}: heading matched {len(hits)} times", file=sys.stderr)
            return 1
        h = hits[0]
        if h < 3 or lines[h - 1].strip() != "":
            print(f"item {num}: no blank line above heading", file=sys.stderr)
            return 1
        e = h - 1
        while e > 0 and lines[e].strip() == "":
            e -= 1
        blanks = h - 1 - e
        if not lines[e].rstrip().endswith("*"):
            print(f"item {num}: line above the blank does not close a status "
                  f"block: {lines[e][:60]!r}", file=sys.stderr)
            return 1
        s = None
        for i in range(e, max(-1, e - 40), -1):
            if lines[i].startswith("*STATUS:"):
                s = i
                break
        if s is None:
            print(f"item {num}: no *STATUS: within 40 lines", file=sys.stderr)
            return 1
        old = "\n".join(lines[s:e + 1]).strip()
        if not (old.startswith("*STATUS: ") and old.endswith("*")):
            print(f"item {num}: old block is not a *STATUS: ...* block", file=sys.stderr)
            return 1
        old_body = old[len("*STATUS: "):-1].rstrip()
        merged = block[:-1] + "\nEARLIER STATUS, KEPT VERBATIM: " + old_body + "*"
        lines[s:e + 1 + blanks] = merged.split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} replaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
