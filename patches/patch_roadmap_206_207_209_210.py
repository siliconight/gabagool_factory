"""Roadmap, 2026-10-08: 206 carries Zoo 1.83.0 and the walker's hero-prop call;
207 carries the measured cause of the dark stages; 209 (window displays, a
music store first) and 210 (payphones) are filed from the walker's comps.

    python patch_roadmap_206_207_209_210.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_206_zoo_182.py left it
(1,278,144 bytes, LF, as read 2026-10-08): 206's and 207's status lines by
their unique prefixes, each directly above its heading; 206's phase 1
"Unproven" line; 207's NEXT block; and the file's last line, item 208's.
Then run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S206_PREFIX = "*STATUS: NARROWED 2026-10-07 -- the van is built and not yet placed: Zoo 1.82.0's `step_van`"
S206_NEW = ("*STATUS: NARROWED 2026-10-08 -- the van is built and not yet placed: Zoo 1.83.0's `step_van`, a "
            "P30-style step van in matte black gone chalky, with the header, the chassis and the ghost lettering "
            "(variant 1) the walker's first look asked for, builds PASS at an exact fit, 5,372 tris against "
            "6,000, five submissions, 0 coincident pairs at six probed sizes and at every centimetre of height in "
            "its chassis sweep. The walker, 2026-10-08: it is the foundation of a hero prop reused across "
            "missions, so it can afford to look good -- a hero pass is next. Nothing parks it at the spawn yet: "
            "the extraction is still a seeded draw among the buildings that are not the spawn, and the score "
            "building itself on 43 of 136 multi-building candidate specs on disk and on 2 of cold run 9195's 3 "
            "candidates. Comps: `docs/reference/GETAWAY_VAN_COMPS.md`.*\n")

OLD_UNPROVEN = "- **Unproven:** the walker has not judged the frames, and nothing places the van.\n"
NEW_UNPROVEN = (
    "- *As first written:* \"Unproven: the walker has not judged the frames, and nothing places the van.\"\n"
    "\n"
    "**THE WALKER'S FIRST LOOK (2026-10-08), AND ZOO 1.83.0.** \"Looks great\", with three asks: \"the windows "
    "in the front feel proportionally a little too tall\"; the ghost lettering -- \"show me this\"; and \"flesh "
    "out the bottom of the truck a bit...like giving it a driveshaft and rear differential\". Then: \"this van "
    "is also going to be the foundation of a hero prop that get's reused in multiple missions, so we can afford "
    "to really make it look good\". The record is `patches/patch_zoo_van_183.py` with `patches/zoo_van_183/`.\n"
    "- **The header:** the glass stops `van_forms.HEADER` (0.28 m) under the roof, where 1.82.0 left 0.10.\n"
    "- **The chassis** (`van_forms.chassis`, prims): frame rails, crossmembers, leaf springs, a front beam, the "
    "rear axle with its differential and pinion, the engine's sump, the transmission, the driveshaft with its "
    "yokes, an exhaust with its muffler out to the road side, the fuel tank on its straps. 28 parts, 512 "
    "triangles, on the body's material: no submission more. Its first build read 1-2 coincident pairs at the "
    "corners and the next three more BETWEEN them -- a rail hung from the body's floor met the front axle's top "
    "within 1.8 mm near a 3.0 m slot -- so the rails now stand on the axle, and the species' test sweeps the "
    "chassis at every centimetre of height (`prims.rod` gained `phase` for it: level 6- and 10-sided pipes "
    "shared their flat tops at the exhaust's elbows).\n"
    "- **The ghost, variant 1:** the van's old life as SKEEVY'S WOODER ICE, its vinyl peeled off and the letters "
    "left as unfaded paint -- one 1024 x 512 image under the paint's `Wear` colour on the same material "
    "(`materials.make_wear_textured_material`); both the texture and COLOR_0 verified in the GLB. Off by default "
    "until the walker chooses; the frames showed it even and then patched.\n"
    "- **The budget:** `tris_lod0` 5,500 -> 6,000 (5,592 at the largest slot). A regression detector, not a frame "
    "cost: draw calls are the van's price, and they are unchanged at five.\n"
    "- **Unproven:** the walker's verdict on the ghost; the hero pass; and nothing places the van.\n")

S207_PREFIX = "*STATUS: OPEN 2026-10-07 -- recurring, unexplained: whenever a level places a strip club"
S207_NEW = ("*STATUS: OPEN 2026-10-08 -- cause measured, not fixed: Lot's `merge_lights` carries an anchor's `pos` "
            "into site coordinates and copies its `target` verbatim, so a stage light off the site's origin aims "
            "73-74 m away, past Lux's 12 m range, and Lux refuses it (`LUX_CLUB_REFUSED`). Cold run 9197: "
            "`b2/main_floor_stage` and `b2/vip_wing_stage` (strip_club_a01); cold run 9167 (club_block_014) carried "
            "the same code. Lux named this defect on cold run 9060 and left it to Lot.*\n")

OLD_207_NEXT = ("**NEXT.**\n"
                "- Read why Lux refuses a stage anchor (the refusal's own reason, in Lux's club rig builder), on "
                "strip_club_a01 and the other club variants.\n"
                "- Then decide whether the stage is lit by its hardware (the markerless fixtures) and the refusal "
                "is correct, or a rig is missing.\n"
                "- The walker's standing call applies: dens of sin are dark buildings, but a stage is where a "
                "club's light goes.\n")
NEW_207_NEXT = (
    "**THE CAUSE, MEASURED (2026-10-08).**\n"
    "- **Lux's refusal names it.** `lux_light_loader.gd` (the `stage_light` branch of the club rig builder, "
    "~1710-1760) refuses a stage light with no target, a throw under 0.25 m, or an energy that solves to 0 "
    "because the throw runs past the range it clamps to 12 m. Its comment records cold run 9060's "
    "`b0/main_floor_stage`: a 54.2 m throw, \"That is Lot's to fix and this cannot fix it -- an anchor carries "
    "no building transform.\" Nobody fixed it.\n"
    "- **Lot's `merge_lights`** (`lot.py` 611-621): `wa = dict(a)`, then `pos` through `_place_point` and "
    "`rot_y` plus the placement's turn. `target` rides in the copy untouched.\n"
    "- **9197's manifests, both builds** -- the greybox candidate's "
    "(`bank_block_001.lot_assemble.candidate.seed_9155/out/site.site.lights.json`) and the themed site's "
    "(`bank_block_001.themed_site_assemble/1/out/site.site.lights.json`), identical: `b2/main_floor_stage` "
    "pos [73.0, -6.5, 3.2], target [0.0, -5.0, 1.68], throw 73.03 m; `b2/vip_wing_stage` pos [69.0, 5.5, 3.2], "
    "target [-5.0, 7.0, 1.68], throw 74.03 m. The targets are the building's own coordinates.\n"
    "- **So it is not intermittent.** It fires whenever a club stands far enough off the site's origin, which "
    "is where a library draw puts it -- the reason it reads as recurring and unexplained.\n"
    "\n"
    "**NEXT.**\n"
    "- Lot: `merge_lights` carries `target` through `_place_point` with `pos`, and a test proves a placed stage "
    "light's throw is the building's own, at a turned and offset placement.\n"
    "- Then a cold run with a club: `LUX_CLUB_REFUSED` gone, 44 of 44 club rigs, and the stages lit in a frame.\n"
    "- *As first filed:* \"Read why Lux refuses a stage anchor ... Then decide whether the stage is lit by its "
    "hardware (the markerless fixtures) and the refusal is correct, or a rig is missing.\" The refusal is "
    "correct; the anchor is wrong. The walker's standing call still applies: dens of sin are dark buildings, "
    "but a stage is where a club's light goes.\n")

LAST_LINE = ("- Measure first: re-walk the kept workspaces' candidates with the contract's body and count what fails, "
             "before it becomes the gate it already is.\n")
NEW_ITEMS = (
    "\n"
    "*STATUS: OPEN 2026-10-08 -- filed for later, the walker's design: buildings with a window display on the "
    "front, a guitar and music store first. Nothing builds one: Deli Counter's storefront is glass onto the "
    "selling floor with an empty window bay, Zoo has no instrument species, and no library family is a music "
    "store. Comps: `docs/reference/MUSIC_STORE_WINDOW_COMPS.md`.*\n"
    "\n"
    "**209. Window displays, a music store first.** The walker, 2026-10-08: \"For later, I want to add to the "
    "roadmap the ability to create certain buildings with a Window Display on the front, we can start with a "
    "Guitar/Music Store\", with six photographs read for format only.\n"
    "\n"
    "**WHAT A WINDOW DISPLAY IS, from the comps:** a shop window as a stage -- a carpeted or draped riser with "
    "instruments on stands, a back of guitars hung by their headstocks with amps stacked behind, neon words hung "
    "in the glass, the display lit by spots and the window framed in neon tube at night, price tags and pedals, "
    "and the selling floor visible behind it.\n"
    "\n"
    "**WHAT EXISTS TODAY** (read 2026-10-08):\n"
    "- Deli Counter's storefront: a storey-0 `storefront_glass` wall built modular, its slots tagged "
    "`glazing: \"storefront\"` (0.153.0) and glazed see-through by Zoo (1.18.0), the room behind lit through it "
    "(0.157.0). The bay behind the glass holds nothing.\n"
    "- Zoo: no instrument. Near: `neon_sign`, `video_rack`, `pack_wall` (and the `slatwall` kind), "
    "`display_case`, `poster_wall` (already in store windows), a crude guitar icon in `poster_art`.\n"
    "\n"
    "**NEXT, when it is picked up.**\n"
    "- Deli Counter: the window bay as its own zone with slots (riser, back, hanging rails, words in the glass), "
    "and a music-store family whose front carries display windows -- two storeys of them in the first comp.\n"
    "- Zoo: guitars in their forms on a stand or hung, amps, the riser; a window of twelve guitars in twelve "
    "colours is one mesh with the colours in the vertex (the draw-call rule); neon words from `neon_sign`.\n"
    "- Lux: the display lit as a display, the window the street's brightest thing at night, within "
    "`max_lights_per_object` and priced.\n"
    "- An invented Delco music store on the sign band (the fake-brands rule).\n"
    "\n"
    "*STATUS: OPEN 2026-10-08 -- filed, the walker's design: payphones on city and urban streets, coin-operated "
    "(quarters), the handset on an armoured steel cord. Zoo's `payphone` (roadmap 153) is a box half-booth with a "
    "handset on a hook -- no cord, no keypad, no coin slot -- and Lot places exactly one, at a bus stop. Comps: "
    "`docs/reference/PAYPHONE_COMPS.md`.*\n"
    "\n"
    "**210. Payphones: quarters and a steel cord.** The walker, 2026-10-08: \"Another roadmap item for "
    "city/urban levels: PayPhones. In the 90s you would pay with quarters, and the phonse is not wireless, it's "
    "on a metal cord.\", with three photographs read for format only.\n"
    "\n"
    "**WHAT EXISTS TODAY** (read 2026-10-08):\n"
    "- Zoo's `payphone` recipe (81 lines): a post, a back panel, a hood, a face plate, a coin box and a handset "
    "on a hook, all boxes; the genome lists no parts and no params.\n"
    "- Lot: `site_furniture._stop_corner` stands one payphone 6.4 m along from each bus shelter, beside the "
    "mailbox and the news racks; a street with no stop has none.\n"
    "\n"
    "**NEXT, when it is picked up.**\n"
    "- Zoo: the instrument redrawn (keypad, coin slot, coin return, cradle, cards, vault door), the armoured "
    "cord as a swept tube on a hanging curve, the enclosure as forms (booth on a post, pedestal shroud, wall "
    "shroud), a \"PHONE\" header with an invented telephone company, a phone-book binder, graffiti and stickers.\n"
    "- Lot: wall shrouds on store walls by the door and pedestals at corners, on the streets the walker means by "
    "city and urban -- which themes those are is the walker's call.\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times: %r" % (len(hits), prefix[:50])
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1278144, "PIPELINE_ROADMAP.md is %d bytes, read at 1,278,144" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for name, anchor in (("206 unproven", OLD_UNPROVEN), ("207 next", OLD_207_NEXT), ("last line", LAST_LINE)):
        assert text.count(anchor) == 1, "%s found %d times" % (name, text.count(anchor))
    assert text.endswith(LAST_LINE), "item 208's NEXT is not the file's last line"
    assert "**209. " not in text and "**210. " not in text
    text = _replace_status(text, S206_PREFIX, S206_NEW, "**206. ")
    text = _replace_status(text, S207_PREFIX, S207_NEW, "**207. ")
    text = text.replace(OLD_UNPROVEN, NEW_UNPROVEN)
    text = text.replace(OLD_207_NEXT, NEW_207_NEXT)
    text = text + NEW_ITEMS
    RM.write_bytes(text.encode("utf-8"))
    print("206 and 207 updated, 209 and 210 filed; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
