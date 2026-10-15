"""Factory 1.40.0: certify the set install test 9 made a level with (roadmap 202).

Copied from `patch_factory_manifest_1_39_0.py`, as every release copies the one before: the manifest's description
is CUMULATIVE, and this puts 1.40.0's story ahead of the description it keeps. Sets every tool's `version` and `tag`
in `factory.manifest.json` to the checkout's VERSION and adds the factory CHANGELOG entry. Asserts the manifest is
1.39.0, that each VERSION parses, and that the tools that moved are exactly the seven the story names; writes
nothing on a miss. The repos are tagged afterwards, at the commits this certifies:

    python patches/patch_factory_manifest_1_40_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_9"
MOVED = {"deli_counter", "laser_tag", "level_factory", "lot", "lux", "patina", "zoo"}

STORY = (
    "1.40.0 certifies the set install test 9 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. SEVEN TOOLS MOVED FROM 1.39.0, the walker's streets most of it, over cold runs 9262 to "
    "9312, all 51 at 0 interventions. THE URBAN STREET (roadmap 241): level_factory deals a continuous "
    "mid-rise wall across the street, the mission's buildings among mid-rises on the near side, its "
    "lowest blocks across from the action, and a corner block at each crossing (0.200.0 to 0.206.1); "
    "deli_counter's mid-rise Empties, narrow and corner blocks, the corner shop's awning and a walk-up's "
    "fire escape (0.213.0, 0.217.0 to 0.220.0); zoo's painted shop window, the awning and the fire escape "
    "(1.107.0, 1.108.0, 1.110.0); lot's planners keep clear of the Empties, enemies may stand behind the "
    "near side, and a city block's trees stand one every 30 ft (0.121.0 to 0.123.0). PHILADELPHIA'S "
    "STREETS (roadmap 240): a wooden pole line carrying the lamps and its wires (zoo 1.104.0, lot "
    "0.118.0 to 0.119.2), rowhomes three steps up on a stoop with iron railings and a tar roof "
    "(deli_counter 0.210.0 to 0.212.0, zoo 1.105.0, level_factory 0.195.0 to 0.197.0), and the street's "
    "drains (roadmap 179: lot 0.120.0, 0.120.1). THE BODY (roadmap 197): every walkable door at least the agent "
    "contract's 1.25 m, the landing and the vault's opening following the contract, the census's "
    "body-sized literals reading it (deli_counter 0.214.0 to 0.216.0; lot 0.120.2). THE BOTS (roadmaps "
    "242, 246): laser_tag's bots keep to the mesh they plan on, a guard held by another bot is blocked "
    "and not stuck, the guards step up as the crew does, and an arrival is at the point, not at the end "
    "of a path that stops short of it (0.28.0 to 0.32.0). LIGHT AND COST: lux bakes the sun while the "
    "lightmap shows, -1,854 draws and -3 ms on the level that priced it (0.76.0, 0.76.1); level_factory "
    "keeps a site's wires out of the lightmap, sizes the reflection atlas to the package's probes (314.6 "
    "-> 65.6 MiB of textures), reports memory in every price, ships only the buildings its scene stands, "
    "merges a walk-up's fire escape with its front and drops the kit modules the per-side merge made "
    "redundant (0.194.0, 0.198.0, 0.199.0, 0.207.0, 0.209.0, 0.210.0). THE SAME BYTES TWICE (roadmap "
    "247): zoo restarts every bevelled face at its "
    "lowest vertex (1.109.0), lux's rigs rest before their scene is packed and level_factory rests them "
    "(0.77.0, 0.208.0), so two runs of one command build every GLB and the lightmap alike. A PICK "
    "COUNTS WHAT IT SHOULD (roadmap 245): the grade breaks a tie (level_factory 0.202.0). A PROP IS NOT "
    "THE BUILDING (roadmap 248): patina leaves a slots.json's props out of the building's bounds "
    "(0.31.0). FLOATERS: zoo's one rule for a detail laid on a surface (1.106.0). THE WALKER'S WALK OF "
    "2026-10-14 (roadmap 250), each fix the walker's call: a lit shop's room glows under its goods, a "
    "desk's stock faces its sitter, a banded door says its trade (zoo 1.111.0, 1.112.0); a ground under "
    "the backdrop (level_factory 0.211.0); a cut switchback's second flight stands on the floor under it "
    "(deli_counter 0.221.0); the delis' basement divider runs wall to wall and the utility room gets a "
    "door (deli_counter 0.222.0). level_factory 0.211.1 re-grounds the doctor's certified table to this "
    "set. Install test 9 (docs/findings/stranger_install/install_test_9/) made this set's package, "
    "unzipped it into a folder that had never held a factory, and typed START_HERE.md's commands into "
    "cmd.exe, `setup --venv` and its PyPI download included: " + RESULT + " The real-tool smoke "
    "(LF_TOOLS_DIR=<factory> pytest tests/real_tools) licenses Level Factory {level_factory}'s "
    "grounded table, which the doctor reads. WHAT THIS SET DOES NOT CERTIFY: Linux (no Linux machine "
    "has run it; the walker has none); the backdrop's ground, shipped unpriced (roadmap 252); the "
    "versions of the nine packages the venv's three pins bring, which pip resolves afresh (roadmap 256); "
    "and every item earlier descriptions name as open that nobody has closed since. THE 1.39.0 STORY AND "
    "EVERYTHING BEFORE IT, unchanged: "
)

ENTRY = (
    "## [factory-v1.40.0] - 2026-10-14\n"
    "\n"
    "Seven tools move:\n"
    "{table}\n"
    "\n"
    "- **The urban street** (roadmap 241): a continuous mid-rise wall, the mission's\n"
    "  buildings among mid-rises, heights by cause, corner shops with awnings,\n"
    "  walk-ups with fire escapes, a city block's trees.\n"
    "- **Philadelphia's streets** (roadmap 240): the pole line and its wires,\n"
    "  rowhomes on stoops with railings and tar roofs, the street's drains\n"
    "  (roadmap 179).\n"
    "- **The body** (roadmap 197): every walkable door at least 1.25 m, the\n"
    "  contract read wherever a body-sized number was.\n"
    "- **The bots** (roadmaps 242, 246): they keep to the mesh, guards step up,\n"
    "  and an arrival is at the point.\n"
    "- **Light and cost:** the sun baked while the lightmap shows (-1,854 draws,\n"
    "  -3 ms); the reflection atlas 314.6 -> 65.6 MiB; a package carries only\n"
    "  what its scene stands.\n"
    "- **The same bytes twice** (roadmap 247): two runs of one command build\n"
    "  every GLB and the lightmap alike.\n"
    "- **The walker's walk of 2026-10-14** (roadmap 250): a shop's room glows\n"
    "  under its goods, desks face their sitters, a banded door says its trade,\n"
    "  a ground under the backdrop, the second flight of a stair stands on the\n"
    "  floor, the delis' basement closed with the utility room's door.\n"
    "\n"
    "Certified by install test 9: the set's package, unzipped into a fresh\n"
    "folder, made restaurant_row_001 with START_HERE.md's commands, the\n"
    "PyPI download included. " + RESULT + "\n"
    "\n"
    "Not certified: Linux; the backdrop's ground is unpriced (roadmap 252); the\n"
    "versions of the nine packages the venv's three pins bring (roadmap 256).\n"
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
    assert m["factory_version"] == "1.39.0", m["factory_version"]
    assert not m["description"].startswith("1.40.0"), "already promoted"
    assert m["description"].startswith("1.39.0 certifies"), m["description"][:40]
    result = pathlib.Path(__file__).with_name("factory_1_40_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 9 result to certify from (factory_1_40_0_result.txt)"
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
    m["factory_version"] = "1.40.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.39.0] - 2026-10-12\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.39.0 -> 1.40.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
