"""Roadmap 241 and 247, 2026-10-14: the corner shop built and proven -- Zoo 1.107.0, Deli Counter 0.218.0, Level
Factory 0.206.0 and 0.206.1, cold runs 9295 and 9296 -- and the roof props' run-to-run bytes filed as 247 (OPEN).
241's status stays NARROWED; its Left clause loses the corner-shop variant and gains 9295's sheet, the shops' glow
and the corners' heights, the awning and the sign band; one body paragraph follows the street trees'. The index is
NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_241_corner_shop.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

LEFT_OLD = ("Left: the walker's eye on 9287's, 9289's, 9292's and 9294's frames (`ab_9287/ab_sheet.png`, "
            "`ab_9289/ab_sheet.png`, `ab_9292/skyline_sheet.png`, `ab_9294/ab_sheet.png`); the frontage; the penthouse, "
            "corner-shop and bay-window variants, each a capability Deli Counter lacks;")
LEFT_NEW = ("The corner shop built: Zoo 1.107.0 (fbbe818) paints a shop's window from its own atlas, Deli Counter 0.218.0 "
            "(173c91b5) builds four corner blocks whose ground-floor front is a deli, a bar, a laundromat or a grocery, "
            "and Level Factory 0.206.0 (e8bd89b) and 0.206.1 (c189baf) open and close each run of the urban wall on "
            "one; cold runs 9295 and 9296 (0 interventions each) stood a lit shop at both ends of every candidate's "
            "wall and held the pick at PASS 100, priced at -4.0 draws a heading, a p95 within its 0.11 ms floor and "
            "+4.2 MiB video memory (`docs/findings/urban_street/ab_9295/corner_sheet.png`). Left: the walker's eye on "
            "9287's, 9289's, 9292's, 9294's and 9295's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`, "
            "`ab_9292/skyline_sheet.png`, `ab_9294/ab_sheet.png`, `ab_9295/corner_sheet.png`), and on the shops' "
            "glow and the corners' heights; the corner shop's awning and sign band; the frontage; the penthouse and "
            "bay-window variants, each a capability Deli Counter lacks;")
BODY_ANCHOR = "-- queued for the next Lot change.\n\n"
BODY_NEW = BODY_ANCHOR + (
    "**THE CORNER SHOP, 2026-10-14** (`docs/proposals/CORNER_SHOP.md`; `docs/findings/urban_street/corner_stations.py`, "
    "`fight_fields_9295.out.txt`; `patches/patch_zoo_shop_panes.py`, `patch_dc_corner_shop.py`, "
    "`patch_lf_corner_shops.py`, `patch_lf_corner_fill.py` and `lf_corner_fill/`; `docs/cold_runs/cold_9295/`, "
    "`cold_9296/`). The comps: \"Corners carry the life. The corner building has the shop at grade (lit, awning), "
    "homes above.\" Zoo 1.107.0 adds `shop_panes`, a second painted atlas beside `window_panes` -- a deli, a grocery, a "
    "bar, a laundromat, a roll-down gate and dark glass in landscape cells on `M_Shop_pane_Face` -- and picks a pane's "
    "atlas by its state. Deli Counter 0.218.0 builds `gs_cornershop_a` to `_d`, mid-rises whose ground-floor front "
    "bays are 2.4 m shop windows authored in one shop's state (`Opening.pane`, `empty_panes.SHOP_STATES`), the shop's "
    "door the block's front door and the homes' behind; its first build failed the specs' own schema gate (an opening "
    "could not carry `pane`), read off the validation manifests before anything was committed. Level Factory 0.206.0 "
    "opens and closes each run of the urban wall on a corner block -- on urban_row_001 no road crosses the far side, "
    "so at the plate's ends -- and 0.206.1 deals the fill afresh where 0.206.0 stopped on a spent bag: cold run "
    "9295's seed_9003 had closed 12.70 m short of its run's end, traced to a 19.8 m block the only one left with "
    "18.70 m to fill; over 600 walls the worst shortfall went 14.20 -> 4.10 m, at the cost of 20 walls standing a "
    "narrow block beside itself where no other design fits. Cold run 9295 (0 interventions, seed_9104 named): every "
    "candidate's wall opens and closes on a corner shop, the pick held at PASS 100 and the fights barely moved; seen "
    "from the near sidewalk straight across (`ab_9295/corner_sheet.png`), the laundromat's washers and the grocery's "
    "aisles read in the glass, both nearly white at `EMISSION` 2.2; priced at -4.0 draws a heading, a p95 +0.06 ms "
    "against a 0.11 ms floor and video memory +4.2 MiB. The glow is paint and costs no light, where the comps' table "
    "names Lux for the shop's light. Cold run 9296 (0 interventions, 0.206.1, the pick `auto`): every wall within the "
    "narrowest design of its end, as replayed beforehand, and the picked package 9295's. Found: the package carries "
    "every themed Empty, standing or not (9295's all four corner blocks, two standing; 194 -> 210 MB); and the "
    "pharmacy's roof props are not byte-stable from run to run (247).\n\n")
ITEM_247 = (
    "\n*STATUS: OPEN 2026-10-14 -- found by cold runs 9294 to 9296 and not traced; Zoo's to answer.*\n"
    "\n"
    "**247. Zoo's roof props are not byte-stable from run to run.** "
    "`lot/pharmacy_a01/art/roofprops/pharmacy_a01_roofprops.glb` read f8fd372b in cold runs 9294 and 9296 and "
    "290b98f0 in 9295: the same 67,908 bytes, its glTF JSON identical, 2,569 bytes of its binary buffer different "
    "from offset 30,276. Its job (`zoo_roof_props_build.pharmacy_a01`, `zoo_cli.py --roof-props`) ran the same "
    "command in all three, `--seed` included, on the same Deli Counter slots in 9295 and 9296, both on Zoo 1.107.0 "
    "(9294's 1.106.0). Roadmap 181 records the scatter as \"deterministic per manifest and seed\". Not traced: "
    "whether the differing bytes are positions, normals or UVs, and whether the skins the job reads differ between "
    "runs. **Why it matters:** a byte that moves without a cause defeats every comparison of packages -- "
    "`docs/cold_runs/cold_9296/NOTES.md` set this one aside only by reading both builds -- and every census that "
    "hashes outputs.\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE CORNER SHOP, 2026-10-14" not in text and "**247. " not in text, "already applied"
    for old in (LEFT_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert s < text.find(LEFT_OLD) < h, "the Left clause is not 241's status"
    e = text.find("\n\n*STATUS:", h)
    assert h < text.find(BODY_ANCHOR) < e, "the body anchor is not 241's"
    assert text.endswith("Laser Tag no longer says otherwise.\n"), "246 is no longer the roadmap's last item"
    for line in BODY_NEW.splitlines():
        assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(LEFT_OLD, LEFT_NEW).replace(BODY_ANCHOR, BODY_NEW) + ITEM_247
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut"), "241's status moved"
    h247 = text.find("\n\n**247. ")
    assert text.rfind("\n\n*STATUS: OPEN 2026-10-14", 0, h247) == h247 - len(
        "\n\n*STATUS: OPEN 2026-10-14 -- found by cold runs 9294 to 9296 and not traced; Zoo's to answer.*"), \
        "247's status does not adjoin its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241: the corner shop; 247 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
