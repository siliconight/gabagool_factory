"""Factory 1.42.0: certify the set install test 13 made a level with (roadmap 202).

Copied from `patch_factory_manifest_1_41_0.py`, as every release copies the one before: the manifest's description
is CUMULATIVE, and this puts 1.42.0's story ahead of the description it keeps. Sets every tool's `version` and `tag`
in `factory.manifest.json` to the checkout's VERSION and adds the factory CHANGELOG entry. Asserts the manifest is
1.41.0, that each VERSION parses, and that the tools that moved are exactly the six the story names; writes nothing
on a miss. The repos are tagged afterwards, at the commits this certifies. The walker, 2026-10-27: "we are also
probably due for a new release/package?", then "fix it before we rush to the release", then "fix those three, then
cut the release", then "hold the release, do the interior pass first", and on 2026-10-28, "lets get to shipping that
release".

    python patches/patch_factory_manifest_1_42_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_13"
MOVED = {"deli_counter", "level_factory", "lot", "lux", "pixelcoat", "zoo"}

STORY = (
    "1.42.0 certifies the set install test 13 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. SIX TOOLS MOVED FROM 1.41.0. A LEVEL WITHOUT A TERMINAL (roadmaps 310-318, the walker's "
    "no-AI authoring loop): level_factory's Factory panel in Godot -- setup checked and the tools' Python "
    "prepared, a level a saved design, its layouts generated, planned top-down and chosen, walked, its "
    "settings changed and seen in the next walk, exported as a snapshot, the Level Standard's designer brief "
    "on its tab (0.243.0-0.259.0). THE SUPERMARKET (roadmaps 274-279, 319): rows of gondolas selling what "
    "the numbered markers over them say, a produce section, a cooler wall, tile and a store's lamp density "
    "(deli_counter 0.271.0-0.279.0; zoo 1.131.0-1.134.0; pixelcoat 0.63.0), and a baked row's range "
    "lent to the bake (lux 0.80.0, level_factory 0.261.0). THE BANK, INSIDE AND OUT (roadmap 321, the "
    "walker's twelve comps and the researched 1990s branch): lit and tiled, its lobby furnished with a check "
    "desk and its chained pens, officers' desks, a queue, plants, a clock, CCTV cameras and its printed "
    "offers and rate board, its walls plastered over dark wood panelling, a glass storefront to the street "
    "framed in aluminium, its teller line naming it over numbered windows; its vault's steel money racks, "
    "cash carts and a wall of numbered deposit boxes with brass locks (deli_counter 0.280.0-0.286.1; zoo "
    "1.135.0-1.142.0); outside, its time-and-temperature sign, its night "
    "depository, a drive-up lane with a pneumatic tube station under a canopy, a clearance bar, bollards "
    "and painted lanes, and one name on its band, door, line, sign and canopy (zoo 1.138.0, 1.139.0; lot "
    "0.132.0-0.135.0; level_factory 0.262.0). EVERY PIECE ON WHAT IT IS MADE OF (deli_counter 0.284.0, "
    "zoo 1.139.0): about 2,800 library slots asked Zoo for a kind their species does not offer, and "
    "delco_1997's `metal` is street rust. ALSO: civic rooms furnished as themselves (deli_counter 0.270.0); "
    "the scout model and the exploded axonometric of every building (deli_counter 0.254.0-0.260.0; "
    "level_factory 0.232.0-0.236.1); stairs solid underneath and stair holes railed (deli_counter "
    "0.262.0-0.269.0; zoo 1.128.0, 1.129.0); queues and crowd barriers (deli_counter 0.242.0-0.244.0; "
    "zoo 1.118.0, 1.119.0); no parking at a bus stop and a signal facing every approach (lot "
    "0.127.0-0.131.0). " + RESULT + " "
)

ENTRY = (
    "## [factory-v1.42.0] - 2026-10-28\n"
    "\n"
    "Six tools move:\n"
    "{table}\n"
    "\n"
    "- **A level without a terminal** (roadmaps 310-318): the Factory panel in\n"
    "  Godot generates a level's layouts, plans them top-down, walks the chosen\n"
    "  one, changes its settings and exports it -- no terminal, no JSON, no AI.\n"
    "- **The supermarket** (roadmaps 274-279, 319): numbered aisles whose\n"
    "  shelves sell what their markers say, produce, a cooler wall, tile, a\n"
    "  store's light, and a bake that reaches the next lamp along.\n"
    "- **The bank, inside and out** (roadmap 321): lit and tiled, plastered over\n"
    "  wood panelling, a glass storefront; a check desk with chained pens,\n"
    "  officers' desks, a queue, plants, a clock, cameras, its printed offers and\n"
    "  rate board; a teller line naming it over numbered windows; a vault of\n"
    "  steel money racks, cash carts and deposit boxes; outside, a time-and-temperature sign, a night depository and a\n"
    "  drive-up lane with its tube station, canopy, clearance bar and painted\n"
    "  lanes; one name on every face of it.\n"
    "- **Every piece on what it is made of**: about 2,800 library slots asked\n"
    "  for a material their species does not offer, many of them street rust.\n"
    "- **Also:** civic rooms furnished as themselves; the scout model and the\n"
    "  exploded axonometric of every building; stairs solid underneath and\n"
    "  stair holes railed; queues and crowd barriers; no parking at a bus stop.\n"
    "\n"
    "Certified by install test 13: the set's package, unzipped into a fresh\n"
    "folder, made a level with START_HERE.md's commands, the PyPI download\n"
    "included. " + RESULT + "\n"
    "\n"
    "Not certified: Linux.\n"
    "\n"
)


def _semver(text):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    assert m, ("no version in", text)
    return m.group(0)


def main():
    raw = MANIFEST.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    m = json.loads(raw)
    assert m["factory_version"] == "1.41.0", m["factory_version"]
    assert not m["description"].startswith("1.42.0"), "already promoted"
    assert m["description"].startswith("1.41.0 certifies"), m["description"][:40]
    result = pathlib.Path(__file__).with_name("factory_1_42_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 13 result to certify from (factory_1_42_0_result.txt)"
        result_text = RESULT
    versions = {}
    rows = []
    moved = set()
    for key, entry in m["tools"].items():
        folder = entry.get("path") or key
        v = _semver((ROOT / folder / "VERSION").read_text(encoding="utf-8"))
        if v != entry["version"]:
            moved.add(key)
            rows.append(f"- {key}: {entry['version']} -> {v}")
        versions[key] = v
        entry["version"] = v
        entry["tag"] = f"v{v}"
    assert moved == MOVED, ("the story names", sorted(MOVED), "but these moved", sorted(moved))
    m["factory_version"] = "1.42.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.41.0] - 2026-10-20\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.41.0 -> 1.42.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
