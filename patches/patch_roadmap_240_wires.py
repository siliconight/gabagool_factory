"""Roadmap 240, 242 and a new 243: the pole line's wires proven in cold run 9263 and held to a pixel by
Lot 0.119.1; the line priced afterwards and its cost found in the street lights' shadow maps; 9263's
reading of 242's kerb-face snag; and the quality tier no package sets. Replaces 240's status block
(asserted once and above its heading), appends one paragraph to 240's body (before 241's status),
appends one paragraph to 242's body (the file's end) and appends item 243.
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_240_wires.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = (
    "*STATUS: NARROWED 2026-10-12 -- the pole line's first two builds shipped and proven in a level, "
    "the walker's four calls of 2026-10-12 built as asked (one side of every street, the full wire set "
    "without house drops, a can every third or fourth pole, a cobra-head on every pole; "
    "`docs/proposals/POLE_LINE_DESIGN.md`). Zoo 1.104.0's `utility_pole` (a 40 ft wood pole, crossarm "
    "and insulators, the cobra-head on a 6 ft arm, a `transformer` form; four draws a pole) and Lot "
    "0.118.0's line (one kerb of every street at 0.61 m from the kerb face, no more than 36 m between "
    "poles, every pole's light at its lens, the band roads' steel lamps gone): cold run 9262, 0 "
    "interventions, 11 poles and 4 cans on the picked lot, both forms built PASS, 13 street lights at "
    "their lenses and lamps (`docs/findings/pole_line/`). Its Laser Tag route read 0.64 where 9261's "
    "read 1.00, and `lt_pole_ab.py` puts that on the lot's furniture rolling two pre-existing snags, "
    "not on the poles (filed as 242). Left: the wires (build 3), frames beside the comps for the "
    "walker's eye, then the rowhouse front and the silver roofs.*")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-12 -- the pole line's three builds shipped and proven in levels, the "
    "walker's four calls of 2026-10-12 built as asked (`docs/proposals/POLE_LINE_DESIGN.md`): Zoo "
    "1.104.0's pole and Lot 0.118.0/0.118.1's line (cold run 9262, 0 interventions), Lot 0.119.0's "
    "wires -- the full set along every line and tied across each junction, unshaded, shadowless, out of "
    "the lightmap by Level Factory 0.194.0, in the themed site only -- in cold run 9263 (0 "
    "interventions; 12 poles, 11 spans, 7 cells; +2.2 draws a heading and p95 +0.05 ms, inside the "
    "noise), and Lot 0.119.1 holding a far wire to a pixel where 9263's frames showed dashes. PRICED "
    "AFTERWARDS, the line itself: +170 draws a heading against 9261's lamps (p95 +0.39 ms at the "
    "median), and the arms put it on the street lights' shadow maps -- the same twelve, a cobra-head "
    "1.6 m higher -- not on the poles; three levers measured (a 30 m shadow fade -154, a budget of 8 "
    "-118, of 4 -241), none applied (`docs/findings/pole_line/`). Left: the fade as a Lux change, "
    "priced with frames; the frames beside the comps for the walker's eye; then the rowhouse front and "
    "the silver roofs.*")

BODY_240 = """

**THE WIRES (BUILD 3) AND THE LINE'S PRICE, 2026-10-12** (`docs/findings/pole_line/`, cold run 9263). **Lot 0.119.0** strings the walker's full set -- three primaries, the neutral, the secondary and two cables -- along every line and from each line's end pole to the nearest pole of another road's line within 30 m: a parabola through Zoo's attachments sagging 2 to 3 % of the span, four-sided tubes at about twice a conductor's radius, one mesh a 32 m cell, unshaded and casting no shadow, in the themed site only so no grader's lot moves (242); **Level Factory 0.194.0** keeps their OBJs out of the lightmap. Cold run 9263, 0 interventions: 12 poles, 11 spans from 12.7 to 33.2 m (2 ties), 7 cells and 7,392 triangles, the lowest cable 5.43 m over the road; the bake's users moved by the new corner pole alone. Priced in the run's own package against the wires hidden: +2.2 draws a heading, p95 +0.05 ms at the median inside the controls' 0.09. **What the price could not see, the frames did:** past about 60 m a few-centimetre tube is under a pixel and drew as dashes. **Lot 0.119.1** gives each vertex its wire's drawn radius, and the material's vertex shader widens a wire thinner than a pixel to one and fades it by the share it covers; spliced into a copy of 9263's package and shot at the same stations, the dashes became faint continuous lines and the near wires read the same. On the way: 0.119.0 wound every face inward and drew both sides, which a fade would have doubled. **THE LINE, PRICED AFTERWARDS.** Builds 1 and 2 shipped without a station price; against 9261's lamps (the same lot, the same anchors) 9262 reads +170.3 draws a heading (-114 to +783) and p95 +0.39 ms at the median. Arms of both packages put it in one place: the street lights' shadow maps cost 300.1 draws a heading in 9262 and 133.4 in 9261 -- Lux shadows twelve street lights in both, and a cobra-head's lamp hangs at 7.50 m where a steel lamp's hung at 5.92 -- and with no shadows in either the two levels differ by 3.5; the poles' own meshes are 29.6, nearly paid for by the lamps. **Refuted on the way, kept:** two scene edits that moved nothing (`shadow_enabled` is set by Lux's policy at runtime; the street rig frees and rebuilds its lamps), each a knob with no effect rather than a measurement. **The levers**, on 9262: Godot's `distance_fade_shadow` at 30 m set in the rig, -154.0 (+16.2 over the lamps), keeping every light near the player shadowed; a budget of 8, -118.2; of 4, -240.9 (-70.6 under the lamps). None applied; the budgets are 243's question."""

BODY_242 = """

**COLD RUN 9263 READ IT AGAIN** (`docs/cold_runs/cold_9263/NOTES.md`). Lot 0.118.1 added one corner pole on the west side street and restepped the east street's -- the only change to seed_9104's graded lot -- and Laser Tag read route completion 0.72 (clearing the candidate's `LT_MAP_TRAVERSAL`) with 72 player-stuck events, where 9262 read 0.64 and 29 and 9261 1.00 and 9. 64 of the 72 stand at one place, plan (-68, -4), the kerb face named above, where 9261's bot stuck 6 times and 9262's 18: furniture 40 m away moves how often the bot walks into it, and the count is the snag's."""

ITEM_243 = """
*STATUS: OPEN 2026-10-12 -- found, a call for the walker. `LuxRoot.quality_tier` defaults to High and no tool sets it, so every package runs High (12 shadow casters, sun shadows, post-fx, glow) on GL Compatibility; roadmap 60's Compatibility tier (4 casters, no sun shadows, no post-fx, no glow) has never shipped. Measured on cold run 9262's package (`docs/findings/pole_line/`): its twelve shadowed street lights cost 300 draws a heading; a budget of 8 saves 118, of 4 saves 241.*

**243. A package runs Lux's High tier on its low-end renderer.** Found pricing the pole line (roadmap 240). `LuxRoot.quality_tier` is an export defaulting to 0, High; Level Factory, Lot and Lux's injector never set it -- only a Lux self-test does -- so the shipped scene runs `LuxQualityProfile.make_tier(0)`: twelve shadow casters ranked by `apply_shadow_policy` (signs, wall packs and street lights first), sun shadows, post-fx, glow, 9,000 rain drops. CLAUDE.md names GL Compatibility as the low-end target the packages ship on, and roadmap 60 priced the tiers on it and built a Compatibility tier (4 casters, no sun shadows, no post-fx, no glow, no film emulsion, 2,000 drops) that no package has run. The tier is a look and a price at once -- post-fx, glow and the sun's shadows are the level's look, not only its cost -- so this is not a default to change in passing. **THE QUESTION FOR THE WALKER.** Which tier a package runs at, or whether the game picks it at runtime (a settings menu is the gameplay layer's, outside the factory) and the factory prices at more than one. **WHAT IS MEASURED.** On 9262's package, the street lights' shadow maps alone: 300.1 draws a heading at 12 casters, 59.2 at 4 (`docs/findings/pole_line/price_9261_9262/`). Not measured: the other tier switches, and any tier on a weaker GPU than the RTX 2060.
"""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**243. " not in text and "THE WIRES (BUILD 3)" not in text, "already applied"
    assert text.count(STATUS_OLD) == 1, "240's status not found once"
    text = text.replace(STATUS_OLD, STATUS_NEW)
    h = text.find("\n\n**240. ")
    assert h > 0 and text.count("\n\n**240. ") == 1
    assert text[h - len(STATUS_NEW):h] == STATUS_NEW, "240's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt, "241 does not follow 240"
    text = text[:nxt] + BODY_240 + text[nxt:]
    g = text.find("\n\n**242. ")
    assert g > 0 and text.count("\n\n**242. ") == 1 and text.find("\n\n*STATUS:", g + 10) < 0, \
        "242 is not the file's last item"
    assert text.endswith("\n")
    text = text.rstrip("\n") + BODY_242 + "\n" + ITEM_243
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status and a paragraph; 242: a paragraph; 243 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
