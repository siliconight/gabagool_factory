"""Level Factory 0.174.0's changelog entry takes cold run 9225's seen and price, which it promised.

Replaces the two sentences the entry shipped with ("in cold run 9225 ... to come") with the
figures, in `level_factory/CHANGELOG.md` and in the patch's own copy. Each anchor must match
exactly once; nothing is written on a miss.

    python patches/patch_lf_0174_results.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
TARGETS = (HERE.parent / "level_factory" / "CHANGELOG.md",
           HERE / "lf_backdrop" / "CHANGELOG_0.174.0.md")
OLD_SEEN = (
    "**Seen:** in cold run 9225, the first to carry Zoo 1.95.0, Lot 0.108.0 and this release "
    "together (`docs/cold_runs/cold_9225/` at the factory root); until that run this layer is "
    "exercised by its tests alone, and the entry is corrected with the frames afterwards.\n"
)
NEW_SEEN = (
    "**Seen,** cold run 9225 (`docs/cold_runs/cold_9225/` at the factory root): "
    "`[export] backdrop: site_backdrop.tscn -- 277 instances of 19 module(s) on their sides, 69 "
    "draw calls`, and at the edge stations the road ends at the fence with a skyline of rowhome "
    "blocks, lit windows and the water tower behind it; the paint travels inside each extracted "
    "mesh (`embedded_textures: 2`). The 19 modules are Lot 0.108.0's three band depths making "
    "three modules of each pair; Lot 0.109.0 gives every band one depth.\n"
)
OLD_PRICE = (
    "**Priced:** cold run 9225's package against 9224's at Level Factory's fixed stations, "
    "control, subject, control, as every step of roadmap 228 is priced; the figures land in that "
    "run's notes and in this entry afterwards.\n"
)
NEW_PRICE = (
    "**Priced,** 9225's package against 9224's at the fixed stations, control, subject, control: "
    "+43 draws a heading median (+17 to +91), the 69 MultiMeshes; p95 frame time +0.02 ms median, "
    "inside the controls' own 0.67 ms spread, 7 of 53 headings over +0.5 ms, the worst +1.25.\n"
)


def main():
    for p in TARGETS:
        raw = p.read_bytes()
        eol = b"\r\n" if b"\r\n" in raw else b"\n"
        text = raw.decode("utf-8").replace("\r\n", "\n")
        assert text.count(OLD_SEEN) == 1, (p, text.count(OLD_SEEN))
        assert text.count(OLD_PRICE) == 1, (p, text.count(OLD_PRICE))
        text = text.replace(OLD_SEEN, NEW_SEEN).replace(OLD_PRICE, NEW_PRICE)
        p.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    print("0.174.0's entry carries 9225's seen and price")


if __name__ == "__main__":
    main()
