"""Roadmap: 206 records Zoo 1.85.0, the getaway van's hero pass.

    python patch_roadmap_206_hero_pass.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_206_ghost_default.py left it
once its index was regenerated (1,286,499 bytes, LF, as read 2026-10-08):
206's status line by its unique prefix, directly above its heading, and its
"Unproven" bullet. Then run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S206_PREFIX = "*STATUS: NARROWED 2026-10-08 -- the van is built and not yet placed: Zoo 1.84.0's `step_van`"
S206_NEW = ("*STATUS: NARROWED 2026-10-08 -- the van is built and not yet placed: Zoo 1.85.0's `step_van`, a "
            "P30-style step van in matte black gone chalky, with the header and the chassis the walker's first "
            "look asked for, the ghost of SKEEVY'S WOODER ICE on every build (the walker: \"make the ghost the "
            "default, patchy version\"), and the hero pass the walker's \"we can afford to really make it look "
            "good\" bought -- real tyres and steel wheels, hung wipers, West Coast mirrors, the tail's lamps, hinges and "
            "corner caps -- builds PASS at an exact fit, 13,792 tris against 16,000, five submissions, 0 "
            "coincident pairs at six probed sizes, by the census and in its chassis sweep. Nothing parks it at "
            "the spawn yet: the extraction is still a seeded draw among the buildings that are not the spawn, "
            "and the score building itself on 43 of 136 multi-building candidate specs on disk and on 2 of cold "
            "run 9195's 3 candidates. Comps: `docs/reference/GETAWAY_VAN_COMPS.md`.*\n")

OLD_UNPROVEN = ("- **Unproven:** the hero pass, and nothing places the van. *As first written:* \"the walker's "
                "verdict on the ghost; the hero pass; and nothing places the van.\"\n")
NEW_UNPROVEN = (
    "- **The hero pass, Zoo 1.85.0 (2026-10-08).** One van a level, priced by its five draw calls, so the "
    "detail is triangles on materials the van already had: tyres from `van_forms.tyre_profile` (a bulged "
    "sidewall, a rounded shoulder, two tread grooves; 22 points at 28 segments, where 1.82.0 lathed 6 at 14), "
    "steel wheels whose disc, hub, eight lug nuts and cap nest, wipers hung from the header as the P30 comp's "
    "are, West Coast mirrors with glass, the crew's step at the kerb-side door, side markers, drip rails, three "
    "identification and two clearance lamps over the rear doors, hinges, aluminium caps on the box's rear "
    "corners, a bumper step, mud flaps. 13,572 / 13,792 / 14,012 tris at the corners (budget 6,000 -> 16,000), "
    "0 coincident pairs on the first build. The record is `patches/patch_zoo_van_185.py` with "
    "`patches/zoo_van_185/`.\n"
    "- **Unproven:** no frame time exists with the van in a level, and nothing places it -- phase 2 is next, "
    "and its cold run owes the performance contract's price (draw calls and frame time at fixed stations, with a "
    "control). *As first written:* \"the hero pass, and nothing places the van.\"\n")


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
    assert len(data) == 1286499, "PIPELINE_ROADMAP.md is %d bytes, read at 1,286,499" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD_UNPROVEN) == 1, "unproven found %d times" % text.count(OLD_UNPROVEN)
    text = _replace_status(text, S206_PREFIX, S206_NEW, "**206. ")
    text = text.replace(OLD_UNPROVEN, NEW_UNPROVEN)
    RM.write_bytes(text.encode("utf-8"))
    print("206: the hero pass; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
