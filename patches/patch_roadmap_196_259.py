"""Roadmap 196 NARROWED again, 2026-10-19 -- its regression fixed in the generator and seen in a level -- and roadmap
259 filed.

196: the delis' video poker cabinets are back. Deli Counter 0.228.0 (3dd5d62e, `patches/patch_dc_store_cabinets.py`)
and cold run 9324 (`docs/cold_runs/cold_9324/`). The status line is replaced whole, the NARROWED 2026-10-07 status
kept after it verbatim; a body paragraph, TWO A STORE, goes after the item's last body line. Anchored on the status
line's sha256 with the item heading two lines below it, and on the last body line's sha256 with the next item's
status two lines below that.

259: Deli Counter's build freshness gate watches 22 of the 54 modules a shell build reaches
(`docs/findings/build_freshness_259/`). Appended after item 258, the last item, as OPEN.

The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_196_259.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
STATUS_SHA = "8f2891e5556a3206c5a405875dc4ab7add111e7394a99fc968960f3874b7114a"
HEADING = "**196. Furnish stands wall pieces against walls that are not there.** Found 2026-10-07 framing the deli case in cold run 9190 (`docs/findings/wall_pieces_without_walls/`)."
OLD_PREFIX = "*STATUS: NARROWED 2026-10-07 -- "
BODY_END_SHA = "0d9d742095b222acb781086f9042898338da21eaac7e270a841c9340fd4c4a29"
NEXT_STATUS_PREFIX = "*STATUS: CLOSED 2026-10-13 -- "
LAST_ITEM_TAIL = "package stops carrying an asset nothing references, which `export_closure` could refuse."

NEW = ("*STATUS: NARROWED 2026-10-19 -- the regression fixed in the generator and seen in a level. Deli Counter "
       "0.228.0 (3dd5d62e, `patches/patch_dc_store_cabinets.py`): a store's video poker cabinet with no free wall "
       "takes a file cabinet's slot, then a vending machine's, in its own room, and a building holds two -- two "
       "dials on the piece, `displaces` and `most_building`, a call made 2026-10-19 and meant to be changed. The "
       "library stripped and refurnished: 27 of the 31 buildings that ask hold two, where 16 did; +18 cabinets "
       "with their stools, 9 file cabinets and 6 vending machines displaced, 3 poster boards fewer. Cold run 9324 "
       "(urban_row_001, 0 interventions, seed 9104 PASS 100, findings 108 -> 108): deli_a01 stands both cabinets, "
       "its composed gates 9323's but for one module more (placement 509/509, the same two seam pairs), the bake "
       "keeps both dynamic as it keeps every lit machine, and Laser Tag moves 0 of 32 summary fields. Priced "
       "against 9323 at 53 headings, 9323 the control twice: +0.7 draws a heading on the mean and +4 at the most, "
       "p95 -0.02 ms at the median inside a 0.05 ms floor, textures +0.7 MiB. Seen "
       "(`cold_9324/cabinets_before_after.png`): each cabinet and its stool against a wall, in a vending machine's "
       "place and a file cabinet's, the poster board over the file cabinet gone with it. "
       "Open: fuel_stop_heist and pawn_shop_a01 hold none and pharmacy_a01 and stop_n_go one, their rooms holding "
       "no filler a cabinet and its stool fit; a partition is still unfurnished (`_seed_clear` keeps every piece "
       "1.0 m off a partition's line). Earlier status kept: NARROWED 2026-10-07 -- ")

BODY = [
    "",
    "**TWO A STORE, 2026-10-19** (`patches/patch_dc_store_cabinets.py` and `dc_store_cabinets/`; "
    "`docs/cold_runs/cold_9324/`). **Measured first** (`dc_store_cabinets/census.py` on Deli Counter 0.227.0's "
    "library): of 31 buildings whose rooms ask for `video_poker_store`, 16 held two, 6 one and 9 none -- four "
    "delis, four pawn shops and a fuel stop. **Why** (`why.py`, replayed on the pre-change deli_a01 the test keeps "
    "as a fixture): both of deli_a01's selling rooms are offered held wall slots and `_seed_clear` refuses every "
    "draw, 58 and 67. The held walls are already stood -- shelf runs, vending, file cabinets, the service counter -- "
    "and the rest are partitions, kept 1.0 m off for their doors; a fixture is placed after its room's wall run, so "
    "it meets a full wall. **The rule, a call made 2026-10-19 and meant to be changed** (Deli Counter 0.228.0): "
    "`displaces=(\"cabinet_file\", \"vending\")` -- a cabinet with no free wall takes a file cabinet's slot, then a "
    "vending machine's, in its own room, passing every test of its own and its stool's, and the filler is put back "
    "when the retry fails -- and `most_building=2`, two a store across its rooms (`most` stays two a room). **The "
    "library, stripped and refurnished** (`migrate_furnish_recipes.py`): 11 specs, +18 cabinets and their 18 "
    "stools, 9 file cabinets and 6 vending machines displaced. A store's poster boards come after its cabinets in "
    "the recipe and meet different walls: corner_deli_heist_01 3 -> 2, cr_deli, deli_a01 and night_deli 2 -> 1, "
    "convenience_store_a01 1 -> 2; every store keeps a board, and the dial, if boards should come first, is the "
    "recipe's order. **Refuted, kept in the patch and the changelog:** the patch's first migration placed the "
    "cabinets alone (`place_fixtures(spec, keys=...)`, +15) and left the library no fixed point of furnish -- "
    "test_wall_backing's, test_club_fixtures' and test_deli_window's fixed-point tests failed -- because a fresh "
    "furnish places a cabinet before the poster boards. The migration is the strip and refurnish every furnishing "
    "change uses.",
    "",
    "**SEEN IN A LEVEL: cold run 9324** (`docs/cold_runs/cold_9324/NOTES.md`; 0 interventions, findings 108 -> "
    "108). deli_a01 composes 538 themed modules where 9323 composed 537, placement 509/509, and the z-fight gate "
    "reads 9323's two seam pairs across 756 solids, the new pieces adding none. The package carries both cabinets "
    "(`lot/deli_a01/art/zoo/prop_video_poker_delco_1997_07_w65_d65_h175_n1.glb`, `_n2.glb`) and their stools; the "
    "light bake keeps the cabinets dynamic, as it already kept pharmacy_a01's and both ATMs (6 -> 8), and "
    "lightmaps the stools. Laser Tag, seed 9104: 0 of 32 summary fields moved, PASS 100 both, 0 stuck events. "
    "**Priced** against 9323 at its 53 headings, 9323 the control twice (`cold_9324/price/`): +0.7 draws a "
    "heading on the mean, +4 at the most and none fewer; p95 -0.02 ms at the median against the controls' 0.05 ms "
    "spread; textures +0.7 MiB, and the buffers not read, the controls disagreeing by 4.1 MiB between themselves. "
    "**Seen** (`cabinets_before_after.png`, the same stations in both packages, the level's own light): on the "
    "customer floor PIKE DRAW and its stool stand beside the ATM where the lemonade vending machine stood; in the "
    "market aisles LUCKY HOAGIE stands where a file cabinet stood under the LOTTO HERE / OPEN 24 HRS board, and the "
    "board went with it: it hung 1.20-1.80 m up over a file cabinet 1.05 m tall, the cabinet on that spot is 1.75 m "
    "tall and overlaps its band in plan and height, and the room holds no board now. That is the board deli_a01 "
    "lost, for the walker's eye.",
    "",
    "**LEFT.** The four stores still short: fuel_stop_heist and pawn_shop_a01 at none, pharmacy_a01 and stop_n_go "
    "at one, whose rooms hold no file cabinet or vending machine a cabinet and its stool fit in. The next dials are "
    "a third filler stem or a narrower partition keepout for a piece with no door to clear; neither is chosen. "
    "The partitions themselves stay unfurnished.",
]

ITEM_259 = [
    "",
    "*STATUS: OPEN 2026-10-19 -- measured, not fixed. Deli Counter's build freshness gate, and Level Factory's "
    "guard that reads its tuple, watch 23 sources; a shell build reaches 54 of Deli Counter's modules, and 32 of "
    "them are unlisted -- 21 whose output a build writes (the agent contract, setbacks, skin styles, the stoop, the "
    "vault room, furnish's own `level_design` among them) and 11 readers or reports -- and `agent_contract.json`, "
    "the body sizes every clearance derives from, is a source no tuple names "
    "(`docs/findings/build_freshness_259/`). Nothing measured says a stale shell has reached a level by it. What "
    "would close it: the 21 and the contract listed, the 11 named read-only with a reason each, and a test that "
    "fails on a reached module in neither.*",
    "",
    "**259. Deli Counter's freshness gate watches 22 of the 54 modules a shell build reaches.** Found 2026-10-19 "
    "shipping Deli Counter 0.228.0, whose change lives in `level_design.py`: a module the builder imports at build "
    "time (`deli_counter.py:3241` and `:3451`) and `build_freshness.GEOMETRY_SOURCES` does not list "
    "(`docs/findings/build_freshness_259/README.md`).",
    "",
    "**WHAT THE GATE IS.** `build_freshness.py` compares each built shell's modification time with the newest of "
    "`GEOMETRY_SOURCES`, \"modules whose output is BAKED INTO a shell\", deliberately not the readers that re-run "
    "against whatever is there; `check.py`, the pre-commit hook, runs it before the nav gate. Level Factory parses "
    "the same tuple with `ast.literal_eval` as the consumer's guard (`packages/pipeline/building_library.py`), "
    "because a brief with a `lot_library` stands the library's own `build/*.glb` and those are gitignored. So the "
    "tuple is both guards' whole idea of what a shell is made of, and it has to stay a literal.",
    "",
    "**WHAT WAS MEASURED** (`freshness_imports.py`, `call_sites.py`; Deli Counter 3dd5d62e). AST imports, "
    "top-level and inside functions, followed from `build.py` and `deli_counter.py` through repo-local modules: 54 "
    "reached; the tuple lists 23, 22 of them reached and `ladder_place.py` named on the build path only in "
    "comments. Of the 32 unlisted, read off their call sites: 21 put their output into what a build writes -- "
    "`agent_contract`, `layout_lint` (stairwell asks its `_host_openings` and `DOOR_APPROACH_M` where a stair can "
    "stand), `ledge_cover`, `level_design`, `material_kind`, `prop_species`, `rarity`, `setbacks`, `skin_style`, "
    "`stair_pitch`, `stoop`, `tactical`, `tscn_export`, `vault_room`, `zoo_export`, and six migrations the presets "
    "call -- and 11 are readers or reports: `circulation`, `zfight_gate`, and `evidence` with the eight it calls, "
    "whose reports no tool outside Deli Counter reads. `agent_contract.json` is read by `agent_contract.py`, and "
    "the tuple names `.py` files only.",
    "",
    "**WHAT IT MEANS, AND WHAT IT DOES NOT.** A commit changing only one of the 21, or the contract, passes the "
    "hook with every shell older than the code that makes them, and Level Factory's guard serves those shells as "
    "fresh. Nothing here says that has happened; 0.228.0 rebuilt every shell after its change. Not established: "
    "whether `ladder_place.py` is reached some way the AST cannot see, and what each of the 21 would change in a "
    "shell if edited -- read off call sites, not measured.",
    "",
    "**WHAT WOULD CLOSE THIS.** The 21 and `agent_contract.json` in `GEOMETRY_SOURCES`, still a literal; the 11 in a "
    "second literal with a reason each; and a test walking the same import graph that fails when a reached module "
    "is in neither, so the next module the builder imports is classified the day it lands. Its price: "
    "`layout_lint.py`, edited often, then asks for a rebuild on every change, because stairwell reads two of its "
    "names -- moving those two into a geometry module would end that. The content fingerprint the gate's own "
    "docstring calls strictly better is the larger step and not this one.",
]


def _sha(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def main():
    marker = "@" * 2
    for block in [NEW] + BODY + ITEM_259:
        assert marker not in block, "a placeholder is still unfilled: " + block[block.index(marker):][:40]
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    assert lines[-1] == "" and lines[-2] == LAST_ITEM_TAIL, ("the roadmap no longer ends on item 258", lines[-2][:80])
    hits = [i for i, l in enumerate(lines) if _sha(l) == STATUS_SHA]
    assert len(hits) == 1, f"item 196's NARROWED 2026-10-07 status found {len(hits)} times"
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2] == HEADING, "the status no longer adjoins item 196's heading"
    old = lines[i]
    assert old.startswith(OLD_PREFIX) and old.endswith("*")
    ends = [j for j, l in enumerate(lines) if _sha(l) == BODY_END_SHA]
    assert len(ends) == 1 and ends[0] > i, f"item 196's last body line found {len(ends)} times"
    j = ends[0]
    assert lines[j + 1] == "" and lines[j + 2].startswith(NEXT_STATUS_PREFIX), "item 196's body no longer ends there"
    for k in range(i + 3, j):
        assert not lines[k].startswith("*STATUS:"), "another status inside item 196's body at line %d" % (k + 1)
    assert not any(l.startswith("**259. ") for l in lines), "item 259 exists"
    for block in BODY + ITEM_259:
        assert not (block.startswith("**") and block[2:3].isdigit()) or block.startswith("**259. "), \
            "a body line would parse as an item: " + block[:30]
    lines[i] = NEW + old[len(OLD_PREFIX):]
    assert lines[i].startswith("*STATUS: NARROWED 2026-10-19 -- ") and lines[i].endswith("*")
    lines[j + 1:j + 1] = BODY
    assert lines[-1] == ""
    lines[-1:-1] = ITEM_259
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 196 NARROWED 2026-10-19 (Deli Counter 0.228.0, cold run 9324) and 259 filed OPEN; "
          "now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
