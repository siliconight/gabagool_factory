"""Roadmap: 206 records the walker's choice on the ghost -- "make the ghost the
default, patchy version" -- shipped as Zoo 1.84.0.

    python patch_roadmap_206_ghost_default.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_206_207_209_210.py left it
once its index was regenerated (1,286,077 bytes, LF, as read 2026-10-08 --
the first draft asserted the patch's own printed 1,285,775 and refused,
which is the guard working): 206's status line by its unique prefix,
directly above its heading, and its "Unproven" bullet. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S206_PREFIX = "*STATUS: NARROWED 2026-10-08 -- the van is built and not yet placed: Zoo 1.83.0's `step_van`"
S206_NEW = ("*STATUS: NARROWED 2026-10-08 -- the van is built and not yet placed: Zoo 1.84.0's `step_van`, a "
            "P30-style step van in matte black gone chalky, with the header and the chassis the walker's first "
            "look asked for and the ghost of SKEEVY'S WOODER ICE on every build (the walker: \"make the ghost the "
            "default, patchy version\"), builds PASS at an exact fit, 5,372 tris against 6,000, five submissions, "
            "0 coincident pairs at six probed sizes and at every centimetre of height in its chassis sweep. The "
            "walker, 2026-10-08: it is the foundation of a hero prop reused across missions, so it can afford to "
            "look good -- a hero pass is next. Nothing parks it at the spawn yet: the extraction is still a "
            "seeded draw among the buildings that are not the spawn, and the score building itself on 43 of 136 "
            "multi-building candidate specs on disk and on 2 of cold run 9195's 3 candidates. Comps: "
            "`docs/reference/GETAWAY_VAN_COMPS.md`.*\n")

OLD_UNPROVEN = "- **Unproven:** the walker's verdict on the ghost; the hero pass; and nothing places the van.\n"
NEW_UNPROVEN = (
    "- **The walker's choice, 2026-10-08:** \"make the ghost the default, patchy version\". Zoo 1.84.0: every "
    "step van carries it, the variant is gone, and the paint is `M_Van_paint` again, always the art under the "
    "`Wear` colour. The record is `patches/patch_zoo_ghost_default_184.py`.\n"
    "- **Unproven:** the hero pass, and nothing places the van. *As first written:* \"the walker's verdict on the "
    "ghost; the hero pass; and nothing places the van.\"\n")


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
    assert len(data) == 1286077, "PIPELINE_ROADMAP.md is %d bytes, read at 1,286,077" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD_UNPROVEN) == 1, "unproven found %d times" % text.count(OLD_UNPROVEN)
    text = _replace_status(text, S206_PREFIX, S206_NEW, "**206. ")
    text = text.replace(OLD_UNPROVEN, NEW_UNPROVEN)
    RM.write_bytes(text.encode("utf-8"))
    print("206: the ghost is the default; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
