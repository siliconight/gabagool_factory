"""Roadmap 228: the yards recipe proven in cold run 9226.

Replaces 228's status block and adds 9226's record to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_9226.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS_TAIL = (
    "`surroundings`, named by the brief or decided by the archetype; cold runs 9226 to 9228 "
    "prove a recipe each. The walker's: the near band 4 m past the fence reads as a dark wall of "
    "windows down the main road at dusk.*\n"
)
NEW_STATUS_TAIL = (
    "`surroundings`, named by the brief or decided by the archetype. Cold run 9226 "
    "(warehouse_yard_001, 0 interventions) proved `yards`: the archetype decided it, Lot laid 97 "
    "containers, 23 warehouses and the tower, Level Factory shipped 121 instances in 17 draws, "
    "seen as stacked containers and a warehouse silhouette past the fence, priced against the "
    "package's own backdrop-off copy at +27.7 draws a heading and no frame time "
    "(`docs/cold_runs/cold_9226/`); 9227 (parkland) and 9228 (roadside) run next. The walker's: "
    "the near band 4 m past the fence reads as a dark wall of windows down the main road at dusk "
    "(9225), and a container's near-white roof reads as a pale slab over the roofline from an "
    "elevated view (9226).*\n"
)
BODY_ANCHOR = (
    "Cold runs 9226 (warehouse_yard_001), 9227 "
    "(county_hospital_001) and 9228 (gas_stop_001) are staged to prove a recipe each.\n"
)
ADDED = (
    "\n**YARDS PROVEN, cold run 9226** (`docs/cold_runs/cold_9226/NOTES.md`): 0 interventions, 0 "
    "retries; the brief named no surroundings and `surroundings_of` decided `yards` from the "
    "archetype (`surroundings_resolved: {asked: \"\", got: \"yards\", known: true}`); Lot laid "
    "`LOT_BACKDROP_PLACED: recipe yards ... 5 module(s), 1 water tower(s)`, 121 `site_backdrop` "
    "slots (97 `cargo_container`, 23 `backdrop_warehouse`, 1 `water_tower`); Zoo's site kit built "
    "every module PASS; Level Factory shipped `121 instances of 5 module(s) on their sides, 17 "
    "draw calls`. Seen in heavy rain at night: the road ends at the fence against stacked "
    "containers and a warehouse's silhouette instead of the bare glow band. Priced against the "
    "package's own copy with the backdrop scene not loaded (`tools/backdrop_off.py`, "
    "`tools/recipe_run_record.sh`): +27.7 draws a heading mean (+15 to +37), p95 median -0.01 ms "
    "inside the controls' 0.12 ms spread, worst heading +0.53 ms.\n"
    "- **Cosmetic, both to fix:** Lot's summary line says `0 rowhome(s)` of a recipe that lays "
    "none, and Level Factory's by-side count reads `N 0, S 0, E 0, W 0` beside its 121 "
    "instances; both tally rowhomes where they mean pieces.\n"
    "- **For the walker's eye:** from the elevated west view a container's top face in the near "
    "band, 3 to 10 m past the fence, is a flat pale rectangle over the roofline ((191, 191, "
    "202); the cargo container is a bevelled box on a near-white tintable). A darker, dirtier "
    "roof in Zoo, or the near band stood further off at a yard, are the two answers.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS_TAIL) == 1, text.count(OLD_STATUS_TAIL)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS_TAIL, NEW_STATUS_TAIL)
    i = text.index(NEW_STATUS_TAIL)
    assert text[i + len(NEW_STATUS_TAIL):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: the yards recipe proven in cold run 9226")


if __name__ == "__main__":
    main()
