"""Roadmap 242, 2026-10-13: the wall's end where Laser Tag 0.31.0's guards are held, probed -- it holds no lone
body (`docs/findings/route_snag/corner_hold_probe.gd`). Two clauses of 242 rewritten, the status's and the
0.31.0 paragraph's "Left". The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check`.

    python patches/patch_roadmap_242_corner_probe.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("left, 14 guards at one wall's end on warehouse_yard_001 seed_9206 that the physics holds, and the fights "
     "0.31.0 moved, read on the breadth and not yet judged (below)",
     "left, 14 guards at one wall's end on warehouse_yard_001 seed_9206 that the physics holds -- a lone "
     "capsule there walks away in every direction but into the wall, so the level is not the trap "
     "(`corner_hold_probe.gd`) -- and the fights 0.31.0 moved, read on the breadth and not yet judged (below)"),
    ("**Left:** the wall's end on warehouse_yard_001 seed_9206, a hold in the engine reached from off the mesh;",
     "**Left:** the wall's end on warehouse_yard_001 seed_9206, a hold in the engine reached from off the mesh"
     " -- and, probed (`docs/findings/route_snag/corner_hold_probe.gd`), not the level's: a fresh capsule of the"
     " contract's size at the held guards' place, at the engine's step and the grader's, goes the whole way in"
     " every direction but into the wall, the seam between the wall's two boxes changing nothing, so what holds"
     " the guards is their own state as they arrive;"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "corner_hold_probe" not in text, "already applied"
    for old, new in EDITS:
        assert text.count(old) == 1, ("not found once", old[:60], text.count(old))
        text = text.replace(old, new)
    h = text.find("\n\n**242. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert EDITS[0][1] in text[s:h], "242's status does not sit directly above its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242: two clauses; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
