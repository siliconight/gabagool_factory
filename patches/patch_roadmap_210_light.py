"""Roadmap 210 NARROWED again: the light and the indoor form shipped -- Zoo
1.89.0 (a backlit header and a hood lamp's diffuser, and the lamp's marker),
Lux 0.70.0 (the `payphone_hood` row), Deli Counter 0.204.0 (an indoor payphone
is a wall unit). Cold run 9213. Lot's placement by theme stays open.

Anchored on 210's status line (its unique opening, then to its line end) and
on the STILL OPEN block's last bullet; each must match exactly once, and no
RESULT_ placeholder may remain, or nothing is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

STATUS_HEAD = "*STATUS: NARROWED 2026-10-09 -- the Zoo half shipped. Zoo 1.88.0 redraws the payphone"
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-09 -- the Zoo half, the light and the indoor form shipped. Zoo 1.88.0 redrew the "
    "payphone (cold run 9212). Zoo 1.89.0 lights it -- the header's face and a hood lamp's diffuser on a backlit "
    "atlas, `LuxEmit_payphone_hood` under the diffuser carrying its height above the ground -- Lux 0.70.0 spawns "
    "that lamp (`payphone_hood`, `REFERENCE_POOL` x 0.75 on the ground under it, set from frames of a lamp stood "
    "live in 9212's package), and Deli Counter 0.204.0 makes an indoor payphone a wall unit (39 payphones in 38 "
    "specs refurnished and rebuilt). Cold run 9213 (club_block_014, 0 interventions): three lamps spawned and baked; "
    "the booth's caller view at midnight 20.5 to 81.8 mean luma; priced against 9212 at 53 headings with no "
    "measurable frame cost, one draw per payphone in view, 0 over the paired 8-light cap. Open: Lot's placement by "
    "theme (the walker's call on which are city and urban), and the walker's eye on the lit booth.*"
)

OPEN_TAIL = ("- **Light at night:** a backlit header and a hood lamp at `ATT_hood`, at one more draw a "
             "payphone. The walker's to call.\n")
DONE = (
    "\n"
    "**ZOO 1.89.0, LUX 0.70.0, DELI COUNTER 0.204.0, DONE: THE PAYPHONE LIT, AND INDOORS A WALL UNIT (2026-10-09)** "
    "(`patches/patch_zoo_payphone_light.py`, `patch_lux_payphone_hood.py`, `patch_dc_payphone_wall.py`, "
    "`patch_dc_kind_paint_matte.py`, `patch_dc_0204_release.py`; finding `docs/findings/payphone_light/`; cold run "
    "9213). The walker, 2026-10-09: \"yes light it, and do the indoor wall form\".\n"
    "- **Where the lamp hangs, and how bright, were measured, not chosen.** A lamp was stood live in 9212's package "
    "at five levels and two depths.\n"
    "  - Behind the header, the card takes 0.42 per unit of energy and the back panel's top 5.9. Mid-hood they take "
    "0.27 and 11.4. A real booth's tube sits behind its header too.\n"
    "  - At 0.75 x `REFERENCE_POOL` every word on the instrument reads and nothing clips.\n"
    "- **Zoo 1.89.0.**\n"
    "  - The header's face and a diffuser just behind it go on a second, backlit atlas named `_Face`, which the power "
    "cut takes.\n"
    "  - Two draws; 1,056 triangles in a default booth; 0 coincident pairs over 3 forms at 3 corners.\n"
    "  - `LuxEmit_payphone_hood` hangs 30 mm under the diffuser, in free air, carrying `lux_type` and `lux_drop` as "
    "glTF extras.\n"
    "  - A recipe may now return `marker_props`, which `markers.add_marker` sets as the empty's custom properties.\n"
    "- **Lux 0.70.0:** the `payphone_hood` row.\n"
    "  - One cool fluorescent downlight; its range is `fluorescent_range(drop)`.\n"
    "  - Its energy puts `PAYPHONE_HOOD_LEVEL` on the ground under it at any drop. That level is `REFERENCE_POOL` x "
    "0.75, the streetlight's ratio, kept as its own constant.\n"
    "  - Not preset scaled.\n"
    "- **Deli Counter 0.204.0.**\n"
    "  - The payphone piece asks `form=\"wall\"`.\n"
    "  - The refurnish, run on a copy first, gave exactly 39 payphones in 38 specs the form and moved nothing "
    "else. The 38 shells were rebuilt.\n"
    "  - The two AUTHORED payphones (`primos_pizza`, `strip_retail_a01`) stay booths.\n"
    "  - A second fix: `material_kind` learns Zoo 1.82.0's `paint_matte`, whose pin to Zoo's kinds had failed since "
    "that release.\n"
    "- **Cold run 9213, 0 interventions.**\n"
    "  - Three lamps spawned and baked: steady rigs 76 to 79. The indoor payphones built as `_fwall`.\n"
    "  - At midnight the booth's caller view reads 20.5 to 81.8; the live probe read 94.8.\n"
    "  - Priced against 9212: no measurable frame cost; one draw per payphone in view (23 of 53 headings, +1 to "
    "+4); 0 over the paired 8-light cap.\n"
    "  - *Corrected, kept:* 9212's notes faced the booth to +X. Its transform faces it to -X.\n"
    "\n"
    "**STILL OPEN.**\n"
    "- **Lot's placement:** wall units by store doors, pedestals at corners. Which themes are city and urban is the "
    "walker's call.\n"
    "- **The walker's eye** on the lit booth and the wall units at midnight (`docs/cold_runs/cold_9213/"
    "payphone_*.png`).\n"
)


def main():
    if "RESULT_" in NEW_STATUS + DONE:
        sys.exit("refusing: a RESULT_ placeholder remains")
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
    if text.count(OPEN_TAIL) != 1:
        sys.exit("refusing: 210's open light bullet matches %d times" % text.count(OPEN_TAIL))
    text = text.replace(OPEN_TAIL, OPEN_TAIL + DONE)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 210 narrowed; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
