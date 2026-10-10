"""Roadmap 228, step A shipped: Lux 0.73.0's horizon glow, seen and priced.

Replaces 228's status block and adds step A's record to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_step_a.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-10 -- the walker's call recorded and the arc designed; nothing built. "
    "Ships in five steps, each priced as the menu was: the glow (Lux), the fence at the plate's "
    "edge (Lot, Zoo), a backdrop rowhome kit and a water tower (Zoo), the bands beyond the plate "
    "by a per-level recipe (Lot), and their composition and the beacon (Level Factory, Lux).*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- step A shipped: Lux 0.73.0's `LuxHorizonGlow`, a ring every "
    "preset tunes (sodium at night, a haze by day; energy 0 draws nothing), seen on cold run "
    "9221's walk copy at the menu's stations (an orange band over the wall at eye level; from the "
    "elevated cameras the whole sky above the roofline goes sodium, the walker's dial) and priced "
    "at Level Factory's fixed stations against two controls: +1.0 draw, p95 +0.19 ms median "
    "inside the controls' 0.23 ms spread, 8 of 53 headings over it, the worst +1.81 ms on the "
    "level's heaviest frame, fill rate where the sky fills the view "
    "(`docs/findings/horizon_glow/`). Next: step B, the fence at the plate's edge (Lot, Zoo), "
    "priced with the glow standing; then the rowhome kit and the tower (Zoo), the bands by "
    "recipe (Lot), composition and the beacon (Level Factory, Lux).*\n"
)
BODY_ANCHOR = "Owners: Lux (A, E's beacon); Lot (B, D); Zoo (B, C); Level Factory (D's field, E).\n"
ADDED = (
    "\n**STEP A SHIPPED, Lux 0.73.0** (`patches/patch_lux_horizon_glow.py`, "
    "`docs/findings/horizon_glow/`). `LuxHorizonGlow`: six rows of 65 vertices at "
    "`horizon_glow_radius_m` (380), opaque dark land below the horizon, `horizon_glow_color` at a "
    "standing eye's height fading to nothing by `horizon_glow_top_deg` (20), the alphas scaled by "
    "`horizon_glow_energy`; unshaded, blended, fog ignored, no GI, no shadow; one draw; the four "
    "fields blend. Every preset carries one by its character: sodium for the night skies (Delco "
    "Night 1.0, three at 0.8, PS1 Storm Night 0.5), a warm dusk haze for Blue Hour, grey for "
    "Heavy Rain, a pale day haze for the three day skies at 0.35. Selftest "
    "`tools/horizon_glow_selftest.gd`, 30 checks.\n"
    "- **Seen:** at eye level an orange band over the pale wall, fading up into the stars (the "
    "sky band's luma 0.9 to 5.5 across the open lot, warmth -0.5 to +4.2); from look_shots' "
    "elevated cameras the whole sky above the rowhome roofline goes sodium (0.9 to 25 to 27). "
    "Interiors and the stations facing in do not move. The strength at the elevated views is the "
    "walker's call; `horizon_glow_energy` is the dial.\n"
    "- **Priced:** +1.0 draw a heading; p95 +0.19 ms median over 53 headings, inside the "
    "controls' own 0.23 ms spread; 8 headings over it by more than 0.5 ms, the worst +1.81 ms at "
    "`extraction_4` facing 270 (11.8 to 13.6 ms). A blended surface pays fill rate wherever the "
    "sky fills the view. The cheaper form, the glow in the sky's own shader, costs nothing a frame "
    "and waits on a provider whose shader Lux may write; reopen it when real sessions' data says "
    "the fill matters on the low-end target.\n"
    "- **Two refutations while writing it, kept:** a LuxRoot added under a SceneTree script's "
    "`_initialize` is not ready until the next frame (the selftest's first run found no glow); "
    "and a mesh stores its vertex colours in 8 bits, so a read-back is within 1/255 of what was "
    "written, not within 1/1000.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: step A shipped (Lux 0.73.0)")


if __name__ == "__main__":
    main()
