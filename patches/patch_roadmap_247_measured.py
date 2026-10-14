"""Roadmap 247, 2026-10-14: the roof props' bytes measured -- one mesh, the same geometry, its vertices in another
order. The status stays OPEN, its text says what was measured; one body paragraph is added. The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_247_measured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = "*STATUS: OPEN 2026-10-14 -- found by cold runs 9294 to 9296 and not traced; Zoo's to answer.*\n"
STATUS_NEW = ("*STATUS: OPEN 2026-10-14 -- measured, not traced: one mesh, the satellite dish's, the same 376 triangles "
              "with 64 of its vertices in another order; the step that reorders them is Zoo's to find.*\n")
TAIL_OLD = ("`docs/cold_runs/cold_9296/NOTES.md` set this one aside only by reading both builds -- and every census that "
            "hashes outputs.\n")
TAIL_NEW = TAIL_OLD + (
    "\n"
    "**MEASURED, 2026-10-14** (`docs/findings/roofprops_bytes/glb_order.py`, `glb_order.out.txt`; 9294 against 9295, "
    "and 9294 against 9296 as the control, 0 bytes). Every one of the 2,569 differing bytes is "
    "`SatelliteDish_metal_delco_1997`'s, the merged dish: its positions, normals, UVs, colours and indices, 180 of "
    "1,071 position values moved by up to 0.75 m. It is the same set of 376 triangles, each with its winding, and the "
    "64 vertices that differ lie between indices 79 and 160 of 357, a permutation of the same positions. So the "
    "geometry is identical and the order is not, inside one span rather than a part swapped whole; the merge orders "
    "parts by name (`partnames.group_parts`), so the reordering more likely happens inside one part's build. Not "
    "traced: which step, and why one run in three.\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**MEASURED, 2026-10-14** (`docs/findings/roofprops_bytes/" not in text, "already applied"
    for old in (STATUS_OLD, TAIL_OLD):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    assert text.endswith(TAIL_OLD), "247 is no longer the roadmap's last item"
    assert text.find(STATUS_OLD) < text.find("**247. ") < text.find(TAIL_OLD)
    text = text.replace(STATUS_OLD, STATUS_NEW).replace(TAIL_OLD, TAIL_NEW)
    h = text.find("\n\n**247. ")
    assert text.rfind("\n\n*STATUS:", 0, h) + 2 == text.find(STATUS_NEW), "247's status does not adjoin its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 247: measured; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
