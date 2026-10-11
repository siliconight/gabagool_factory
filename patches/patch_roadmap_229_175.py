"""Roadmap 229 and 175, from cold run 9241's block.

229: one paragraph appended to its body (the dome's fix proven in a level: +0 draws against the
troffers it replaced at 53 of 53 headings, the bowl lit under its canopy), and its status's
remainder names the dome as landed. 175: CLOSED -- Deli Counter 0.144.0 fixed it and nobody closed
it; the closure rests on an engine probe on 9241's package (`docs/findings/hidden_state_collision/`),
with one paragraph appended to its body. Every anchor asserted once; each status asserted to adjoin
its heading; nothing written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_229_175.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEAD_229 = "\n\n**229. "
TAIL_229 = ("Cold run 9241 is the fix's reading. Still owed: a residence-heavy lot for the look, and the "
            "pendant and the other species the guide names (strip light, sconce, high-bay, exit sign).")
ADD_229 = """

**THE DOME'S FIX, PROVEN, 2026-10-11** (cold run 9241, `docs/cold_runs/cold_9241/NOTES.md`; on Zoo 1.99.1, whose hemisphere helper now keeps the upper half and on which the dome builds the same vertex for vertex). On 9233's lot again, 0 interventions, seed_9104 picked and 123 findings as 9238 and 9239. A dome is two meshes as the troffer it replaced: the deli's fixtures layer 257 submissions as 9238's where 9239's read 263 (`docs/findings/fixture_merge/layer_count.py`), the bake's lightmap users 3,518 as 9238's where 9239's read 3,524, and priced against 9238's package **+0 draws at all 53 headings** (9239: +6 at 24) with the p95 -0.20 ms inside the controls' 0.39 ms spread. Seen (`fixtures.png`, `dome_zoom.png`): the hideout warm as 9239 first showed it, and the fixture a lit frosted bowl under the canopy's rim with the finial at its bottom, where 9239's was a dark disc with its finial hanging alone. The species step's first species stands landed, proven and seen; the rest of it is the pendant over a home's table and the guide's strip light, sconce, high-bay and exit sign."""

STATUS_229_OLD = ("and the species (strip light, sconce, high-bay, exit sign). Owner: Deli Counter, with Zoo for "
                  "the species and Lux for the rigs.*")
STATUS_229_NEW = ("and the species beyond the dome (Zoo 1.98.0/1.98.1, Lux 0.75.0, Deli Counter 0.208.0: a "
                  "home's room hangs a flush-mount dome, proven at +0 draws and seen lit in cold run 9241): "
                  "strip light, sconce, high-bay, exit sign. Owner: Deli Counter, with Zoo for the species and "
                  "Lux for the rigs.*")

HEAD_175 = "\n\n**175. A hidden interactive state keeps its collider, so there is collision\nwhere nothing is drawn.**"
STATUS_175_OLD = ("*STATUS: OPEN 2026-09-23 -- MEASURED IN THE ENGINE. All 11 `breached` nodes\n"
                  "carry `visible = false` and a live collider; at 2 of 6 sampled walls a ray hits\n"
                  "`Breach` rather than `Wall`. The shipped default is still SOLID, which is what\n"
                  "the walker wants, but by coincidence rather than by construction.*")
STATUS_175_NEW = ("*STATUS: CLOSED 2026-10-11 -- fixed by Deli Counter 0.144.0 (`319f25c2`, \"a hidden "
                  "interactive state keeps its collision off\"), closed now on an engine probe: "
                  "`docs/findings/hidden_state_collision/breach_ray_probe.gd`, headless on the imported copy "
                  "of cold run 9241's package, reads the deli's 9 hidden `_breached` states each with its "
                  "one body, `Breach`, at collision layer 0 and mask 0, and 18 full-mask rays through their "
                  "origins from either side meet the visible `Wall` or the greybox lintel -- 0 of 18 hit a "
                  "hidden state (`breach_ray_9241.txt`). Not read: a navmesh baked from physics geometry.*")
TAIL_175 = ("None of the 11 measured is that; all are wall panels. Worth a\n"
            "look before the rule is written as unconditional.")
ADD_175 = """

**CLOSED 2026-10-11, A MONTH LATE.** Deli Counter 0.144.0 wrote the fix this item asks for -- `themed_tscn.write_themed_tscn` gives every hidden state its contract marks not solid (`interactives._DEFAULTS`' `collision_per_state`: a breach's `breached`, a door's `open`, a window's `broken`) an editable override that sets each collision body's layer and mask to 0 -- and the item stayed OPEN, found again on 2026-10-11 while reading the open list. In cold run 9239's and 9241's packages the deli's scene carries 9 `_breached` nodes and 9 overrides, and the engine agrees (`docs/findings/hidden_state_collision/`). The rule's one caveat above stands as written: a state legitimately solid while hidden would need its contract to say so, and none does."""


def _append(text, head, tail, add, what):
    assert text.count(head) == 1, (what, "heading not found once", text.count(head))
    h = text.index(head)
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, (what, "no status after it")
    body = text[h:nxt]
    assert body.endswith(tail), (what, "body does not end where this patch read it", body[-160:])
    return text[:nxt] + add + text[nxt:]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE DOME'S FIX, PROVEN" not in text and "CLOSED 2026-10-11, A MONTH LATE" not in text, "already applied"
    # 175's status, adjoining its heading
    assert text.count(STATUS_175_OLD) == 1, ("175's status", text.count(STATUS_175_OLD))
    s = text.index(STATUS_175_OLD)
    assert s + len(STATUS_175_OLD) == text.index(HEAD_175), "175's status does not adjoin its heading"
    # 229's status remainder
    assert text.count(STATUS_229_OLD) == 1, ("229's status remainder", text.count(STATUS_229_OLD))
    text = _append(text, HEAD_229, TAIL_229, ADD_229, "229")
    text = _append(text, HEAD_175, TAIL_175, ADD_175, "175")
    text = text.replace(STATUS_175_OLD, STATUS_175_NEW)
    text = text.replace(STATUS_229_OLD, STATUS_229_NEW)
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 229's paragraph and status remainder, 175 CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
