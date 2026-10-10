"""Roadmap 219: the six fixes proven together in cold run 9217; item 220 filed, the sign's bar.

219's status line is replaced whole: the one line that starts with its unique opening, asserted
to be exactly one. Item 220 is appended after 219, the file's last item, its status directly
above its heading, refused if a 220 exists. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

START = "*STATUS: NARROWED 2026-10-09 -- six of the twelve notes fixed, not yet run cold."
NEW = (
    "*STATUS: NARROWED 2026-10-09 -- six of the twelve notes fixed and PROVEN together in cold run "
    "9217, club_block_014 at seed 9181 by night, the walked level: 0 interventions, 0 retries, "
    "findings 72 to 71 against 9213. Lot 0.102.1 stands the bus stop on its band before the corner "
    "is spaced against it (note 6: in 9217 the racks stand 0.89 and 0.715 m from their nearest "
    "pieces, where 9213 had one 0.11 m from the flag post and one over the shelter's end); Lot "
    "0.102.2 turns each meter's windows across the kerb (note 4, framed); Deli Counter 0.204.1 keeps "
    "3 of the rowhomes' 10 roof fixtures (note 3: 6 of the level's 26 roofs dressed, where 19 were); "
    "Zoo 1.90.0 letters the door sign in Blue Highway Condensed, Aileron Bold for a civic fascia "
    "(note 10, framed: MOM THINKS I'M AT BINGO on one line); Level Factory 0.165.0 gives a signal's "
    "lenses one 60 s clock at import (note 9, framed: both heads green alone; the import log names "
    "the pass on both passes); Zoo 1.91.0's `window_drape`, hung by Deli Counter 0.205.0 on every "
    "strip club window with no window light behind it (note 2: placed, and dark at night from "
    "both sides, as the club itself is -- note 1). Pixelcoat's street band still letters in Pixel "
    "Operator; none is in club_block_014. Next: the club's light (note 1), the two placeholders and "
    "the bags; then the perimeter and the backdrop as a menu with frames; the moon waits on the "
    "walker. The run's frames found item 220.*"
)

ITEM_220 = (
    "\n"
    "*STATUS: OPEN 2026-10-09 -- found in cold run 9217's frames and older than them: a thin light "
    "vertical bar on the lit door sign at its centre, from about mid-text to the bottom rule, in "
    "9213 (Zoo 1.89.0) and 9217 (1.90.0) alike. Not the texture, not a thing standing off the face, "
    "not Lux's preview quad. Cause not established.*\n"
    "\n"
    "**220. A bar down the middle of the door sign.** `docs/cold_runs/cold_9217/sign_bar_9213_9217.png`: "
    "strip_club_a01's door sign, framed close at midnight in both runs, carries a thin, light "
    "vertical bar at its centre. It runs from about the text's middle to the bottom rule, over 1.89.0's "
    "pixel lettering and 1.90.0's Blue Highway alike, so no release in 9217 made it.\n"
    "\n"
    "What it is not, measured:\n"
    "- **The texture:** the package's `SignBox_Face_608x216_2573fba6_4af3fd0b.png` is clean.\n"
    "- **Geometry standing off the face:** shot head-on and from 1.8 m to the side "
    "(`sign_close`, `sign_angle`), the bar keeps its place between the letters, as a thing on the "
    "face's plane would.\n"
    "- **Lux's emissive preview quad:** both paths turn it off (`lux_fixture_spawner.gd` 106, "
    "`lux_light_loader.gd` 1396).\n"
    "\n"
    "Next: frame `sign_box` alone, in a probe the drape's way (`docs/findings/den_drapes/probe.gd`). A "
    "bar there is Zoo's; none there is the level's -- the bake, or the rig standing 0.29 m off the "
    "face.\n"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "**220." not in text, "item 220 exists"
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(START)]
    assert len(hits) == 1, len(hits)
    lines[hits[0]] = NEW
    text = "\n".join(lines)
    assert text.endswith("\n"), "the roadmap ends without a newline"
    ROADMAP.write_bytes((text + ITEM_220).encode("utf-8"))
    print("roadmap 219: proven in 9217; 220 filed")


if __name__ == "__main__":
    main()
