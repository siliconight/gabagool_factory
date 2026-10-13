"""Roadmap 197, 2026-10-13: CLOSED -- the walker's decision shipped as Deli Counter 0.214.0 and proven in cold runs
9285 and 9286. The status line becomes CLOSED with its evidence, the old status kept after it as what it
replaced; one body paragraph is added at the item's end, after Lot 0.120.2's. The index is NOT touched here:
run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_197_door_width.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = "*STATUS: NARROWED 2026-10-11 -- re-measured on today's tools and half explained."
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-13 -- the doors are the contract's and the deli's guards do not jam. The walker: "
    "\"widen the doors and keep 1.25\", called out in the agent contract. Deli Counter 0.214.0 (2879716a) "
    "writes every walkable door at least `clearances.min_door_width_m`: 152 authored library doors in 29 "
    "specs widened, a width-less door's default, every preset (61 doors in 15), the staff door, and the "
    "generated deli's six 1.1 m doors (`rear_staff_entry` this item's) and 1.2 m front, all at 1.25. "
    "`agent_contract.json` says so beside the number: the derivation re-worked at the contract's own 0.1 "
    "cell (the bake needs 1.00; 1.25 is a DESIGN MINIMUM), `min_door_width_note`, and `re_derive_when` for "
    "the walker's \"singular changes when we know the size of characters\". Cold run 9286 (deli_001, 9191's "
    "brief and seeds, 0 interventions): enemy stuck 0 on all three candidates where 9246 read 49 / 0 / 19, "
    "grades PASS_WITH_TUNING 80 / PASS 90 / PASS_WITH_TUNING 80, seed_9292 picked at PASS 90; seed_9191 "
    "reads the grade, stuck and blocked roadmap 242 measured on 9246's narrow-door copy under Laser Tag "
    "0.31.0 (80, 0, 29). Cold run 9285 (restaurant_row_001, 0 interventions): its lots' widened buildings "
    "reached the level and every Laser Tag summary field matches 9277's. Before it, NARROWED 2026-10-11 -- "
    "re-measured on today's tools and half explained.")

BODY_ANCHOR = ("that decision is the walker's, as the status says.\n\n"
               "*STATUS: CLOSED 2026-10-07 -- cold run 9193")
BODY_NEW = (
    "that decision is the walker's, as the status says.\n\n"
    "**THE DECISION, SHIPPED: Deli Counter 0.214.0, 2026-10-13** (`docs/findings/door_widths/README.md`, "
    "`deli_counter/CHANGELOG.md`, `docs/cold_runs/cold_9285/`, `docs/cold_runs/cold_9286/`). The walker chose "
    "option 2 -- \"yes, widen the doors and keep 1.25\" -- and then asked for the contract to stay the one place "
    "a body's size is changed: \"continue to update the agent contract file so we can make singular changes "
    "when we know the size of characters in the game\". So every door width Deli Counter's code writes now "
    "reads the contract: the presets (`DOOR_W`), the width-less default, the staff door (was a literal 1.25) "
    "and the stairs-first landing door (the corridor's width, was a literal 1.1). `clearances.re_derive_when` "
    "lists what one change to a body moves on its own, and the body-sized literals that do not follow yet: "
    "`stairwell.LANDING_DEPTH` and the vault's 1.3 x 2.1 m aperture, spelt in Deli Counter and Zoo. Two doors "
    "stay under 1.25, named in `min_door_width_note`: `primos_pizza`'s `kitchen_stairs` (no place on its wall "
    "between L18 and L21) and the stairs-first landing doors (at 1.25 none of 20 crossings holds one). The "
    "wider doors moved what the furnishing pass puts beside them: 8 specs refurnished, 3 pieces lost and 4 "
    "gained, the library's cigarette machines 119 -> 118. Measured before it shipped: `layout_lint` 0 FAIL / "
    "391 WARN both ways; the presets as Level Factory makes them, 304 and 432 variants, the same FAILs, narrow "
    "doors 1,568 and 2,148 -> 0; 140 stairs-first specs byte-identical; 1,480 passed. Not separated: 9286's "
    "gains on seed_9292 and seed_9393 against 9246 -- the grader, Lot and Level Factory have all moved since.\n\n"
    "*STATUS: CLOSED 2026-10-07 -- cold run 9193")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "Deli Counter 0.214.0 (2879716a)" not in text, "already applied"
    for old in (STATUS_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    h = text.find("\n\n**197. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s + 2:].startswith(STATUS_OLD), "197's status does not sit directly above its heading"
    text = text.replace(STATUS_OLD, STATUS_NEW).replace(BODY_ANCHOR, BODY_NEW)
    h = text.find("\n\n**197. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith(STATUS_NEW), "197's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 197: CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
