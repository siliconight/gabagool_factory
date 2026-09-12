"""Roadmap batch 22, 2026-09-11: item 141 narrowed by Level Factory 0.71.0.
REPLACE mode; the old status block is kept verbatim. Asserts once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, INSTRUMENT NAMED, NOT YET RUN*

**141. The facade's texel scale jumps at the remainders and the openings.**"""

NEW = """*STATUS: NARROWED 2026-09-11 -- INSTRUMENT RUN, CAUSE FOUND IN THE WIRING,
FIXED IN LEVEL FACTORY 0.71.0, MEASURED BACK TO 1.0x ON THE WALKED COPY;
NOT YET RE-EXPORTED OR RE-WALKED. `tools/texel_density.gd` over the walked
copy: 537 kit surfaces over 4 skins, concrete 0.152..10.0 texels/m (66.0x
mismatch, 278 surfaces), drywall 0.152..5.0 (33.0x), glass_facade 11.0x --
box projection, roadmap 88's defect, shipped. Of the two halves this item
named, it is the binding: the package carries the script at
`lot/shell/zoo_worldskin.gd` (compose installs it at the composed package's
root; export nests that as `lot/shell/`), `export._importer_defaults_block`
tested for it at the export ROOT, wrote no `[importer_defaults]`, and the
sidecar pass baked `import_script/path=""` into all 48 kit sidecars. The
same shape export.py's own docstring records for `LF_precinct_yard_001`
("the package carried the script and ran it on nothing"), fixed once at
the declaration and never at the path. LF 0.71.0 declares the script at
the path it is found; `test_worldskin_declared` holds the `lot/shell/`
shape. Measured on the walked copy with the declaration added by hand and
the kit sidecars regenerated: 46 of 48 bound, all four skins
world-triplanar, worst mismatch 1.0x. RESIDUE: no package has been
exported by 0.71.0 yet; the walked copy `_runs/walk_county_hospital_001`
now carries the declaration (its old `project.godot` kept as
`project.godot.pre141`) and the Lux 0.33.0 runtime, so it is the copy to
re-walk. EARLIER STATUS, KEPT VERBATIM: OPEN 2026-09-11 -- FOUND BY A
PERSON, INSTRUMENT NAMED, NOT YET RUN*

**141. The facade's texel scale jumps at the remainders and the openings.**"""


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); item 141 narrowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
