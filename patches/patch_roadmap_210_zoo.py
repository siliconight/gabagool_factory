"""Roadmap 210 NARROWED: the Zoo half shipped -- Zoo 1.88.0 redraws the
payphone (cold run 9212). Lot's placement, Deli Counter's indoor form and the
payphone's light at night stay open.

Anchored on 210's status line (its unique opening, then to its line end) and
on the body's last line; each must match exactly once, or nothing is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

STATUS_HEAD = "*STATUS: OPEN 2026-10-08 -- filed, the walker's design: payphones on city and urban streets"
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-09 -- the Zoo half shipped. Zoo 1.88.0 redraws the payphone as a stainless coin "
    "phone -- twelve keys showing their digits, a coin slot, a real coin-return recess, the vault door, the "
    "instruction card, the cradle with the handset hung in it -- on an armoured cord swept as one tube, in a booth "
    "(the default), a pedestal shroud or a wall unit, YOUSETEL's header, card and stickers in one atlas: one draw "
    "where 1.87.0 drew three, 980-1,098 tris, 0 coincident pairs over 3 forms at 3 corners in Blender. Cold run 9212 "
    "(club_block_014, 0 interventions): three payphones in the level, priced against 9211 at 53 headings with no "
    "measurable frame cost and 2-8 fewer draws at the 21 that see one. Open: Lot's placement by theme (the walker's "
    "call on which are city and urban), Deli Counter's indoor payphones asking for the wall form, and light at night "
    "-- at midnight the booth is a silhouette.*"
)

TAIL = ("- Lot: wall shrouds on store walls by the door and pedestals at corners, on the streets the walker means by "
        "city and urban -- which themes those are is the walker's call.\n")
DONE = (
    "\n"
    "**ZOO 1.88.0, DONE: THE PAYPHONE REDRAWN (2026-10-09)** (`patches/patch_zoo_payphone.py`; finding "
    "`docs/findings/payphone_redraw/`; cold run 9212). The walker, on 1.87.0's frames: it \"doesn't have a phone or "
    "appropriate decals\". It is also the modern low-poly standard's second worked example (item 214).\n"
    "- **Planned in pure Python, the dumpster's way.** `core/payphone_forms.py` names a tile in one atlas for every "
    "face; `recipes/payphone.py` builds it with `_card_atlas.build_art`. One object, one material, one draw.\n"
    "- **The instrument, at its real size.** Its foot is 1.0 m up wherever the slot allows. Twelve keys each show "
    "their own digit's window of one printed face. The coin-return recess is a real hole 30 mm deep, as the "
    "standard asks.\n"
    "- **The cord** is one swept tube with its rings turned by parallel transport (`payphone_forms.tube`), which "
    "roadmap 216's trunks can reuse.\n"
    "- **The forms**, `params.form`, `auto` the booth:\n"
    "  - the booth: a header reading PHONE beside YOUSETEL, and a shelf;\n"
    "  - the pedestal: the handset glyph stamped on each side;\n"
    "  - the wall unit: a line conduit to the ground, and a phone book on two rings.\n"
    "- **The name is invented:** YOUSETEL, \"YOUSE TALK. WE TOLL.\", held against the factory's denylists and the "
    "1990s telephone companies and payphone makers.\n"
    "  - The line rides only a header 0.66 m or wider, measured to set there.\n"
    "  - The stickers each sample their own tile, cut into the back panel's face, and a sticker that does not fit "
    "is left off by the plan.\n"
    "- **Coincident faces: 0** in Python (27 sizes, 3 forms) and in Blender (3 forms at 3 corners). The payphone "
    "leaves `test_coincident_faces.RESIDUE`, 2,997 pairs to 2,995.\n"
    "  - *Retracted, kept:* the first Blender census found 6 pairs, the vault lock's inner cap 2.0 mm proud of "
    "the face, on the probe's window, with float32 deciding. The lock now starts inside the body, and the suite "
    "checks at 3 mm.\n"
    "- **Its tests and suite.** 22 tests; Zoo's suite is 4,045 passed. `test_recipe_reads_its_genome` now skips "
    "the payphone, which builds no material for it to read, and a colour test in the species' own suite takes its "
    "place.\n"
    "- **What it costs** (cold run 9212 against 9211, four price runs):\n"
    "  - no measurable frame cost;\n"
    "  - 2 to 8 fewer draws at the 21 of 53 headings that see a payphone;\n"
    "  - a default booth is 76,928 bytes of GLB and a 137,458-byte atlas of 256 x 1,243 px, about 1.2 times the "
    "standard's 512 x 512 area.\n"
    "- **The level.** Lot's bus-stop payphone faces the sidewalk, back to the traffic. At midnight it reads as a "
    "silhouette: its roof shades the instrument, as 1.87.0's did.\n"
    "\n"
    "**STILL OPEN.**\n"
    "- **Lot's placement:** wall units by store doors, pedestals at corners. Which themes are city and urban is "
    "the walker's call.\n"
    "- **Deli Counter's indoor payphones**, the airport terminal's and the funeral home's, stand against walls "
    "(`level_design._piece(\"payphone\", ..., \"wall\")`) and build as booths. Asking for `form=\"wall\"` is a "
    "one-field change, and a piece edit needs the library refurnished (L23).\n"
    "- **Light at night:** a backlit header and a hood lamp at `ATT_hood`, at one more draw a payphone. The "
    "walker's to call.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(STATUS_HEAD) != 1:
        sys.exit("refusing: 210's status opening matches %d times" % text.count(STATUS_HEAD))
    i = text.index(STATUS_HEAD)
    j = text.index("\n", i)
    if not text[i:j].endswith(".*"):
        sys.exit("refusing: 210's status line does not end its block on one line")
    text = text[:i] + NEW_STATUS + text[j:]
    if text.count(TAIL) != 1:
        sys.exit("refusing: 210's last line matches %d times" % text.count(TAIL))
    text = text.replace(TAIL, TAIL + DONE)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 210 narrowed; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
