"""Roadmap 233 CLOSED by cold run 9244, and 178's newest member (a failed bake that counted zero).

233: its status block replaced (asserted whole by its first and last text, and asserted to adjoin
its heading) and a paragraph appended to its body. 178: a paragraph appended to its body; its status
is not touched. Nothing written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_233_178.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD_233 = "\n\n**233. A fixture's same-material parts are separate meshes: a pendant pays a draw for its cord.**"
S233_START = "*STATUS: OPEN 2026-10-11 -- measured, not started. A building's fixtures ship as one GLB per scope"
S233_END = "per fixture and never across fixtures (the module rule, `merge.py`'s), then price it the cover merge's way.*"
S233_NEW = ("*STATUS: CLOSED 2026-10-11 -- Zoo 1.100.0 (`patches/patch_zoo_fixture_merge.py`, "
            "`docs/findings/fixture_merge/`): `merge.pack_by_material` takes each part's placement as a unit "
            "and `build.build_fixtures` exports merged by it, a placement's same-material parts one mesh and no "
            "two placements sharing one. Cold run 9244 (restaurant_row_001, 0 interventions, baked on one "
            "attempt) priced against 9241's package: -26 draws a heading at the median, -49 at most, none more, "
            "p95 +0.06 ms inside the controls' 0.24 ms spread; 3,483 lightmap users where 9241 read 3,518, the "
            "35 meshes merged away; the pendant frames the same picture. Cold runs 9242 and 9243 asked first "
            "and shipped unbaked, which Level Factory 0.178.5 and 0.178.6 fixed (roadmap 178).*")
TAIL_233 = ("the lens materials' names (Lux's emissive binder keys on `M_*_Lens`), and each part's shading (no "
            "welding, as `merge.py` keeps it).")
ADD_233 = """

**CLOSED BY ZOO 1.100.0 AND COLD RUN 9244, 2026-10-11.** The merge keeps the module rule by making the PLACEMENT the module: `pack_by_material(collection, units)` groups by each part's placement, and since a placement's parts move with one matrix, the identity rule a module keeps becomes one transform inside a unit -- the parts merge in the frame they share and the merged mesh takes it; a part whose transform differs is refused and named, not baked. Built from Deli Counter's own manifests, cold run 9239's three fixture layers went from 437 submissions to 402 -- the deli's pendants' metal 46 meshes to 23, a sign box's and a wall pack's 2 to 1 -- with every lens, dome, troffer and sign face the same and the `LuxEmit_*` markers untouched. In a level (9244 against 9241): -26 draws a heading at the median and -49 at most, more than the 35 meshes at some headings, which is consistent with GL Compatibility drawing a mesh once more for each further light that reaches it (inferred, not measured); no frame time the harness can see. The street's lamps were never in scope: Lot places them as site furniture, which Zoo builds as modules already merged by material. A roof's props, if roadmap 181 ships them through Zoo's roof-prop builder, can take the same units."""
TAIL_178 = ("Connecting them is cheaper than\nbuilding anything new and is the difference between a pipeline "
            "that produces\nlevels and one that produces levels somebody would ship.")
ADD_178 = """

**A FIFTH, 2026-10-11: A BAKE THAT FAILED SHIPPED UNBAKED, TWICE, AND COUNTED ZERO** (cold runs 9242 and 9243). The export's light bake failed -- first `bake.tscn did not open` (the plugin counted frames while an unfocused editor sleeps 100 ms a frame), then a lightmap image read back empty -- restored the presentation scene, shipped the package without its lightmap and printed a WARNING. The drive stopped only when nothing was exported, so both runs went on to their walks and counted 0 interventions with levels lit only by their live lights. Closed for this member: Level Factory 0.178.5 keeps the bake's editor awake, asks for the scene until it opens and keeps the editor's output; 0.178.6 tries a failed bake once more on a fresh copy; and `tools/cold_drive/cold_drive.sh` now STOPS when an export asked to bake ships unbaked, reading the package's `light_bake.json` rather than its log (`patches/patch_cold_drive_bake_stop.py`). Cold run 9244 baked on its first attempt under all three. The rest of the family -- the z-fight gate, the isolation warning, the approach count, the navgate population -- still reports into logs nobody's counter reads."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "CLOSED BY ZOO 1.100.0" not in text and "A FIFTH, 2026-10-11" not in text, "already applied"
    assert text.count(HEAD_233) == 1, "233's heading not found once"
    h = text.index(HEAD_233)
    s = text.rfind("\n\n*STATUS:", 0, h) + 2
    status = text[s:h]
    assert status.startswith(S233_START) and status.endswith(S233_END), ("233's status", status[:80], status[-80:])
    nxt = text.find("\n\n*STATUS:", h + 10)
    body = text[h:nxt]
    assert body.endswith(TAIL_233), ("233's body tail", body[-120:])
    h2 = text.index("\n\n**178. ")
    n2 = text.find("\n\n*STATUS:", h2 + 10)
    assert text[h2:n2].endswith(TAIL_178), ("178's body tail", text[h2:n2][-120:])
    # later edits first, so earlier offsets stay right
    text = text[:nxt] + ADD_233 + text[nxt:]
    text = text[:s] + S233_NEW + text[h:]
    h2 = text.index("\n\n**178. ")
    n2 = text.find("\n\n*STATUS:", h2 + 10)
    text = text[:n2] + ADD_178 + text[n2:]
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 233 CLOSED with its paragraph, 178's fifth member; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
