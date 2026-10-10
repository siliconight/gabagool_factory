"""Roadmap 219 notes 8 and 12: the perimeter and backdrop menu is filed, the walker's to pick.

Note 8's and note 12's rows and the 219 status line are each rewritten in place, asserted to be
exactly one line each. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

R8_OLD = ("| 8 | a diegetic perimeter that keeps the collision and the signal | Lot, Zoo | The `perim_*` "
          "edges are bare walls. A menu with frames is owed. |")
R8_NEW = ("| 8 | a diegetic perimeter that keeps the collision and the signal | Lot, Zoo | The `perim_*` "
          "edges are bare walls, 3 m, pale in the moon: the brightest thing at the end of a street. "
          "THE MENU IS FILED, the walker's to pick (`docs/findings/edge_menu/`): six options on cold "
          "run 9219's walk copy, framed at five stations and priced against two controls. The "
          "perimeter is a dark concrete-block wall (A, B, C) or Zoo's chain-link with the wall's "
          "collision kept behind it (D, E, F). No option moves frame time past the controls' own "
          "0.65 ms spread; draws rise 1.6 (D) to 16.1 (A) a heading on about 1,150. Recommended: D, "
          "the fence. |")
R12_OLD = ("| 12 | something past the sky's horizon, \"to make the level not look like it's literally "
           "floating in space\" | Lot, Zoo | Nothing stands beyond the perimeter. "
           "`docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md` was filed for this. Goes with 8. |")
R12_NEW = ("| 12 | something past the sky's horizon, \"to make the level not look like it's literally "
           "floating in space\" | Lot, Zoo, Lux | Nothing stands beyond the perimeter. "
           "`docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md` was filed for this. Goes with 8. "
           "THE MENU IS FILED with 8's: a sodium sky-glow over dark land in every option (Lux, per time "
           "of day; it ignores the night's fog and climbs to 20 degrees, or a 3 m wall hides it), with "
           "a tree belt (B, D), rows of rowhome blocks with lit windows and a water tower (A, E), or "
           "both (F). Recommended: D, the tree belt; houses later, with a real kit. |")
S219 = "*STATUS: NARROWED 2026-10-10 -- nine of the twelve notes fixed and PROVEN"
OLD_TAIL = "Next: the perimeter and the backdrop as a menu with frames. The moon waits on the walker.*"
NEW_TAIL = ("Notes 8 and 12: the perimeter and backdrop menu is filed, six options framed and priced "
            "(`docs/findings/edge_menu/`), recommended D, the chain-link fence, the tree belt and the "
            "glow: the walker's to pick. The moon waits on the walker too.*")


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    for old, new in ((R8_OLD, R8_NEW), (R12_OLD, R12_NEW)):
        hits = [i for i, ln in enumerate(lines) if ln == old]
        assert len(hits) == 1, (old[:40], len(hits))
        lines[hits[0]] = new
    hits = [i for i, ln in enumerate(lines) if ln.startswith(S219)]
    assert len(hits) == 1, ("219 status", len(hits))
    assert lines[hits[0]].endswith(OLD_TAIL), lines[hits[0]][-120:]
    lines[hits[0]] = lines[hits[0]][: -len(OLD_TAIL)] + NEW_TAIL
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: notes 8 and 12, the menu filed")


if __name__ == "__main__":
    main()
