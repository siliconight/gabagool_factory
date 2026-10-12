"""Roadmap 240: the street-light shadow fade refuted on GL Compatibility by its own self-test
(`patches/patch_lux_street_shadow_fade.py`, refusing). Replaces the end of 240's status (asserted
once, the status still above its heading) and appends one paragraph to 240's body, before 241's
status. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_240_fade.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("three levers measured (a 30 m shadow fade -154, a budget of 8 "
       "-118, of 4 -241), none applied (`docs/findings/pole_line/`). Left: the fade as a Lux change, "
       "priced with frames; the frames beside the comps for the walker's eye; then the rowhouse front and "
       "the silver roofs.*")
NEW = ("three levers measured (a 30 m shadow fade -154, a budget of 8 "
       "-118, of 4 -241), none applied (`docs/findings/pole_line/`): on GL Compatibility the fade freezes "
       "a far shadow rather than ending it -- its Lux draft refuted by its own self-test -- and the "
       "budgets are 243's. Left: Lot 0.119.1 in a cold run; the street lights' shadow cost, the walker's "
       "call among the levers; the frames beside the comps for the walker's eye; then the rowhouse front "
       "and the silver roofs.*")

BODY = """

**THE FADE, REFUTED ON THE TARGET RENDERER, 2026-10-12** (`docs/findings/pole_line/`). Drafted as Lux 0.76.0 -- the street rig gives each pole lamp Godot's `distance_fade_shadow` at 30 m, a wall pack none -- with a windowed self-test on GL Compatibility: every control held, and a slab's shadow seen from 44 m stayed black (0.000 against 0.499 unshadowed). The order probe read far FIRST and the pool was lit; read far after a near look, black. Past the distance the engine stops re-drawing the shadow map -- the 154 draws -- and the light keeps sampling its last one, so a far shadow freezes and a light never seen near casts none: stale or missing shadows on what moves through a far pool, and a failing (live) light first seen from afar lighting through the walls beside it. Two instruments disagreed and both were right about different things. The patch is kept refusing; the untried shape is fading the whole light, not its shadow, for steady (baked) street lights only."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE FADE, REFUTED ON THE TARGET RENDERER" not in text, "already applied"
    assert text.count(OLD) == 1, "240's status end not found once"
    text = text.replace(OLD, NEW)
    h = text.find("\n\n**240. ")
    assert h > 0 and text.count("\n\n**240. ") == 1
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert s >= 0 and NEW in text[s:h] and text[s:h].endswith(NEW), "240's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt, "241 does not follow 240"
    text = text[:nxt] + BODY + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status end and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
