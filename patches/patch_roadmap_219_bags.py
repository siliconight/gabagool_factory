"""Roadmap 219 note 11: the garbage bags are fixed and not yet run cold (Zoo 1.93.0, Lot 0.104.0).

The 219 status line and note 11's row are each replaced whole: the one line that starts with its
unique opening, asserted to be exactly one. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S219 = "*STATUS: NARROWED 2026-10-10 -- eight of the twelve notes fixed and PROVEN on the walked level"
OLD_TAIL = ("Still the walker's: the brighter fill, and the club's office-tile ceiling. Next: note 11, "
            "the bags; then the perimeter and the backdrop as a menu with frames. The moon waits on "
            "the walker.*")
NEW_TAIL = ("Note 11 is FIXED and not yet run cold: Zoo 1.93.0 draws a heap of filled garbage bags, "
            "and Lot 0.104.0 stands one beside each dumpster. Still the walker's: the brighter fill, "
            "the club's office-tile ceiling, and bags by the street's litter bins. Next: a cold run "
            "of note 11; then the perimeter and the backdrop as a menu with frames. The moon waits "
            "on the walker.*")
OLD_HEAD = "*STATUS: NARROWED 2026-10-10 -- eight of the twelve notes fixed and PROVEN"
NEW_HEAD = "*STATUS: NARROWED 2026-10-10 -- nine of the twelve notes fixed, eight of them PROVEN"

S11 = "| 11 | filled black garbage bags stacked by the bins |"
R11_OLD = ("| 11 | filled black garbage bags stacked by the bins | Zoo, Lot | A new species and its "
           "placement beside the dumpsters (one a building) and the cans. |")
R11_NEW = ("| 11 | filled black garbage bags stacked by the bins | Zoo, Lot | A new species and its "
           "placement beside the dumpsters (one a building) and the cans. FIXED, not yet run cold: "
           "Zoo 1.93.0's `trash_bags`, a heap of filled bags -- a row of two to five on the ground "
           "and one or two thrown on top, slumped, lumpy and knotted, mostly black with the odd "
           "white or green bag, one draw a heap, 1,536 triangles at the default slot. Lot 0.104.0 "
           "stands one beside each dumpster, turned to line its side and on its pad where the pad "
           "has room. Replayed on cold run 9218's spec: three dumpsters, three heaps, all on their "
           "pads, and nothing else on the site moved. *Not done: the cans.* No bags stand by the "
           "street's litter bins. A heap there would stand on the sidewalk's walking band, and "
           "whether the street should look that neglected is the walker's call. |")


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(S219)]
    assert len(hits) == 1, ("219 status", len(hits))
    st = lines[hits[0]]
    assert st.startswith(OLD_HEAD) and st.endswith(OLD_TAIL), st[-200:]
    lines[hits[0]] = NEW_HEAD + st[len(OLD_HEAD):-len(OLD_TAIL)] + NEW_TAIL
    rows = [i for i, ln in enumerate(lines) if ln.startswith(S11)]
    assert len(rows) == 1 and lines[rows[0]] == R11_OLD, ("note 11's row", len(rows))
    lines[rows[0]] = R11_NEW
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: note 11 fixed, not yet run cold")


if __name__ == "__main__":
    main()
