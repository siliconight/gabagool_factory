"""Roadmap: item 206 carries the walker's two calls of 2026-10-07 -- the getaway
vehicle is a matte-black, faded Chevrolet P30-style step van, and it stands AT
the mission's spawn point.

    python patch_roadmap_206_van.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_203_close_207_208.py left
it (1,273,211 bytes, LF, as read 2026-10-07): 206's status line by its unique
prefix, directly above its heading, and two lines of 206's NEXT. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_PREFIX = "*STATUS: OPEN 2026-10-07 -- the walker's default, not yet built"
STATUS_NEW = ("*STATUS: OPEN 2026-10-07 -- the walker's design, not yet built: the getaway vehicle is a Chevrolet "
              "P30-style step van, matte black, faded, with patina -- \"a worn in truck...that's been on many jobs\", "
              "the crew's own \"millenial falcon\" -- parked AT the mission's spawn point: \"you spawn, do the job, "
              "then return to the car\". Today the extraction is a seeded draw among the buildings that are not the "
              "spawn, and it is the score building itself on 43 of 136 multi-building candidate specs on disk and on "
              "2 of cold run 9195's 3 candidates. Comps: `docs/reference/GETAWAY_VAN_COMPS.md`.*\n")

OLD_BULLETS = ("- Where it stands is a design question to weigh against `S_BACKTRACK`: at the crew's start (the briefs' "
               "\"backtrack\") or a different edge of the site (Lot's audit).\n"
               "- A choice of several vehicle spots is replayability's first step, and the package marks the live one "
               "(item 204).\n")
NEW_BULLETS = ("- **Where it stands -- decided** (the walker, 2026-10-07): \"the same as the missions spawn point. you "
               "spawn, do the job, then return to the car.\" The spawn and the extraction are one point, the van at "
               "the curb. 159 of 181 cold-run briefs already asked for this (`crew_start_backtrack`). Lot's "
               "`S_BACKTRACK` (\"the exfil rewinds the entry\") would fire on every level under it, so the rule must "
               "recognise the getaway van rather than overrule the walker. *As first filed:* \"a design question to "
               "weigh against `S_BACKTRACK`: at the crew's start ... or a different edge of the site\".\n"
               "- **What it is -- decided:** a step van -- walk-in body and cab as one box, flat split windshield, "
               "round headlights in square bezels, walk-in side door -- matte black, sun-faded, rust at the arches "
               "and seams, grime on the lower third. One hero prop, the same truck in every level. The comps and "
               "what each tool owes them: `docs/reference/GETAWAY_VAN_COMPS.md`. Show the walker a frame before it "
               "rolls out.\n"
               "- A choice of several spawn-and-van spots is replayability's first step, and the package marks the "
               "live one as the mission's start and extraction (item 204).\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times" % len(hits)
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1273211, "PIPELINE_ROADMAP.md is %d bytes, read at 1,273,211" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD_BULLETS) == 1, "bullets found %d times" % text.count(OLD_BULLETS)
    text = _replace_status(text, STATUS_PREFIX, STATUS_NEW, "**206. ")
    text = text.replace(OLD_BULLETS, NEW_BULLETS)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 206 carries the walker's van and its spot")


if __name__ == "__main__":
    main()
