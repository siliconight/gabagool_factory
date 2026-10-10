"""Roadmap 219 note 11: cold run 9220 proves the garbage bags (Zoo 1.93.0, Lot 0.104.0).

The 219 status line and note 11's row are each rewritten from their unique openings, asserted to
be exactly one line each. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S219 = "*STATUS: NARROWED 2026-10-10 -- nine of the twelve notes fixed, eight of them PROVEN"
OLD_HEAD = "*STATUS: NARROWED 2026-10-10 -- nine of the twelve notes fixed, eight of them PROVEN"
NEW_HEAD = "*STATUS: NARROWED 2026-10-10 -- nine of the twelve notes fixed and PROVEN"
OLD_TAIL = ("Note 11 is FIXED and not yet run cold: Zoo 1.93.0 draws a heap of filled garbage bags, "
            "and Lot 0.104.0 stands one beside each dumpster. Still the walker's: the brighter fill, "
            "the club's office-tile ceiling, and bags by the street's litter bins. Next: a cold run "
            "of note 11; then the perimeter and the backdrop as a menu with frames. The moon waits "
            "on the walker.*")
NEW_TAIL = ("Note 11 was proven in cold run 9220 (0 interventions, 0 retries, findings 71 to 71): Zoo "
            "1.93.0's heaps of filled garbage bags, one beside each of the three dumpsters, all on "
            "their pads, where Lot 0.104.0 put them (`docs/cold_runs/cold_9220/`). At midnight, on "
            "the buildings' north sides, the black bags read as a black lump against the pad. Still "
            "the walker's: the brighter fill, the club's office-tile ceiling, bags by the street's "
            "litter bins, and light on the service side. Next: the perimeter and the backdrop as a "
            "menu with frames. The moon waits on the walker.*")

S11 = "| 11 | filled black garbage bags stacked by the bins |"
R11_OLD = "the cans. FIXED, not yet run cold: Zoo 1.93.0's `trash_bags`"
R11_NEW = "the cans. FIXED and PROVEN in cold run 9220: Zoo 1.93.0's `trash_bags`"
R11_END_OLD = "whether the street should look that neglected is the walker's call. |"
R11_END_NEW = ("whether the street should look that neglected is the walker's call. In 9220 all three "
               "heaps stood beside their dumpsters on their pads, and at midnight in the buildings' "
               "shadow they read as black lumps against the pad, where the dumpster reads by its "
               "paint; light on the service side is the walker's call. *Corrected:* 1.93.0's "
               "1,536 triangles are heaps 0 and 2; heaps 1 and 3 are 1,920 at the default slot and "
               "2,688 at the largest, under the genome's 2,800. |")


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
    assert len(rows) == 1, ("note 11's row", len(rows))
    row = lines[rows[0]]
    assert row.count(R11_OLD) == 1 and row.endswith(R11_END_OLD), row[-160:]
    lines[rows[0]] = row.replace(R11_OLD, R11_NEW)[: -len(R11_END_OLD)] + R11_END_NEW
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: note 11 proven in 9220")


if __name__ == "__main__":
    main()
