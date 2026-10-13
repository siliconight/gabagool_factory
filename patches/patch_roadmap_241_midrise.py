"""Roadmap 241, 2026-10-13: step 1's first cut -- Deli Counter 0.213.0's mid-rise Empty family, named out of today's
streets, proven to move no draw in cold run 9277 (`docs/findings/urban_midrise/`). 241's status rewritten OPEN ->
NARROWED and one paragraph appended after its RELATED paragraph, before 242's status. The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_241_midrise.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S241_OLD = ("*STATUS: OPEN 2026-10-11 -- decided, not started. The walker chose a NEW URBAN LEVEL TYPE: a brief asks "
            "for an urban block, mid-rise Empties (5-12 storeys) form continuous street walls at the sidewalk line "
            "with the enterable buildings among them, and the Delco strip levels stay as they are "
            "(`docs/reference/URBAN_MIDRISE_COMPS.md`). Order: Deli Counter's mid-rise Empty family, Lot's urban "
            "layout, Level Factory's brief field, Lux's dusk haze, each priced.*")
S241_NEW = ("*STATUS: NARROWED 2026-10-13 -- step 1's first cut built: Deli Counter 0.213.0's six mid-rise Empties, "
            "`gs_midrise_a` to `_f`, brick blocks of 5, 6, 7, 8, 10 and 12 storeys with windows in regular bays, a "
            "lobby door and a parapet, named out of the prefix Level Factory hands to every terrace, and cold run "
            "9277 (0 interventions) drawing today's restaurant_row_001 byte for byte as 9276 did "
            "(`docs/findings/urban_midrise/`, its greybox frames for the walker). The walker chose this NEW URBAN "
            "LEVEL TYPE on 2026-10-11 (`docs/reference/URBAN_MIDRISE_COMPS.md`). Left: the walker's eye on the "
            "frames; the penthouse, corner-shop and bay-window variants, each a capability Deli Counter lacks; Lot's "
            "urban layout; Level Factory's brief field; Lux's dusk haze; the price.*")

RELATED = ("**RELATED.** Roadmap 240's parts (the pole line, stoops, silver roofs) serve both level types; 228's edge "
           "recipes gain taller massing for the urban one; 199 and 230 (the walkable-city brief, the adjacency "
           "guide) say what an urban block's routes and neighbours should be.")

BODY_241 = """

**STEP 1, THE FIRST CUT, 2026-10-13** (`docs/findings/urban_midrise/`; `patches/patch_dc_midrise.py`, `patch_dc_midrise_navgate.py`; `docs/cold_runs/cold_9277/`). **Deli Counter 0.213.0's `presets.empty_midrise`**: a brick block of `floors` storeys, its windows in regular bays about 3.2 m apart front and back (the bay CHOSEN, not read -- the comps give no dimension), a lobby door at grade and a service door behind it, party-wall sides sealed by `auto_exterior`, a parapet, 15 m deep at a 3.1 m storey -- an Empty in every respect Deli Counter keys on `facade`. `EMPTY_MIDRISES` holds six, 15 to 24 m wide, 16.5 to 38.7 m to the parapet's top, in the rowhome family's three bricks and one stone front; each built in 2 to 3 s, 223 to 615 slots. **Named out of today's streets:** Level Factory hands every `gs_empty_*` in the library to any brief that stands a terrace (`building_library.empty_rows`), so the family is `gs_midrise_*`; as facades they are already outside the enterable draw. The nav gate's baseline records the six UNJUDGED, as it records the rowhome Empties, which the pre-commit gate asked for. **The control, cold run 9277** (0 interventions), after the library was rebuilt whole: the three candidates' staged `level.tscn` and `site.tscn` byte-identical to 9276's, every Laser Tag summary field the same, findings 117 -> 117, the bake to the count. **Frames for the walker** (`midrise_street.png`, `midrise_high.png`): the six in a row as a street wall beside a rowhome Empty, greybox and tinted by piece name -- massing, height and the window rhythm, not a theme's look. **RETRACTED, KEPT in the findings:** the first frames tinted by material, which left every surface white and then drew floor-to-roof stripes, the sills and lintels wearing the window's greybox material. **Asked of the walker:** the window size and spacing, the ground floor (the comps' corners carry a lit shop -- the corner variant, not built), the plain parapet, the 5-12 storey range against the comps' 12-15 far blocks."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**STEP 1, THE FIRST CUT, 2026-10-13**" not in text, "already applied"
    assert text.count(S241_OLD) == 1, "241's status not found once"
    text = text.replace(S241_OLD, S241_NEW)
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and S241_NEW in text[s:h], "241's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    nh = re.search(r"\n\n\*\*(\d+)\. ", text[nxt:])
    assert nxt > h and nh and nh.group(1) == "242" \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "242 does not follow 241"
    r = text.rfind(RELATED, h, nxt)
    assert r > h and text.count(RELATED) == 1 and r + len(RELATED) == nxt, "RELATED is not 241's last paragraph"
    text = text[:nxt] + BODY_241 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
