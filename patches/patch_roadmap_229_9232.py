"""Roadmap 229: Deli Counter 0.207.0 seen in cold run 9232 (the deli's market aisles, the hideout).

Replaces one sentence of 229's status block and appends the record to its body. Each anchor must
match exactly once; nothing is written on a miss, and nothing is written while the SEEN_
placeholder is unfilled. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_229_9232.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

SEEN = ("the sheet shows the market aisles' three rows in both packages, 9232's on the lanes' centres by "
        "construction where 9229's grid had missed the gondolas by luck (a 0.4 to 0.8 m shift the frame "
        "barely shows; the rule earns its keep where a grid crossed a run, 15 rooms in the library, none "
        "in this level's frame), and the hideout dim under its one fixture, a 21 x 16 m room lit like a "
        "bedsit -- a refinement to queue: a home's room's fixtures by area (one per 30 to 40 m2) or bulbs")

OLD_STATUS = "; cold run 9232 shows the deli's market aisles. "
NEW_STATUS = (
    "; cold run 9232 (0 interventions) shows it: the deli's generate log reads `17 row(s) laid to the "
    "work, 1 room(s) over their aisles`, the market aisles stand three rows over the three lanes "
    "between its aisle shelves (-5.2, +0.4, +4.8 off the room's centre, where 0.206.1 stood them at "
    "-5.6, -0.4, +4.4 across it) and the hideout one fixture; " + SEEN + " (`docs/cold_runs/cold_9232/"
    "rooms_before_after.png`, 9229 against 9232). "
)
BODY_ANCHOR = (
    "stations.\n"
    "\n**THE ROWS OVER THE AISLES, AND THE LONG HALL, 2026-10-10.**"
)
BODY_TAIL_MARK = "Cold run 9232 shows the deli's market aisles and the hideout from room \nstations.\n"


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert not SEEN.startswith("SEEN_"), "fill SEEN before applying"
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    # the body: the 0.207.0 paragraph ends with "... from room stations.\n"; the record goes after it
    end = "Cold run 9232 shows the deli's market aisles and the hideout from room stations.\n"
    assert text.count(end) == 1, text.count(end)
    added = (
        "\n**SEEN IN COLD RUN 9232** (`docs/cold_runs/cold_9232/NOTES.md`, `rooms_before_after.png`): "
        "the deli's four largest rooms from the same room stations in 9229's package (0.206.0) and 9232's "
        "(0.207.0). " + SEEN + " The merged lights put the market aisles' three rows at -5.2, +0.4 and "
        "+4.8 off the room's centre, four lamps each, over the three lanes between the preset's aisle "
        "shelves; the hideout is one fixture; site-wide 41 rows and 161 lamps where 9229 had 44 and "
        "174. Not priced at stations; cheaper than 0.206.1 by count.\n"
    )
    text = text.replace(end, end + added).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**229. "), "229's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 229: Deli Counter 0.207.0 seen in cold run 9232")


if __name__ == "__main__":
    main()
