"""Factory 1.41.0: certify the set install test 12 made a level with (roadmap 202).

Copied from `patch_factory_manifest_1_40_0.py`, as every release copies the one before: the manifest's description
is CUMULATIVE, and this puts 1.41.0's story ahead of the description it keeps. Sets every tool's `version` and `tag`
in `factory.manifest.json` to the checkout's VERSION and adds the factory CHANGELOG entry. Asserts the manifest is
1.40.0, that each VERSION parses, and that the tools that moved are exactly the seven the story names; writes
nothing on a miss. The repos are tagged afterwards, at the commits this certifies. The walker, 2026-10-20: "a fresh
new upload of our package so if we needed to start from a new PC we wouldn't lose any progress".

    python patches/patch_factory_manifest_1_41_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_12"
MOVED = {"deli_counter", "dispatch", "level_factory", "lot", "lux", "patina", "zoo"}

STORY = (
    "1.41.0 certifies the set install test 12 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. SEVEN TOOLS MOVED FROM 1.40.0, over cold runs 9313 to 9357: every run that finished at 0 "
    "interventions, six stopped by a gate whose finding a tool then answered (9315, 9320, 9321, 9334, "
    "9335, 9342), and 9319 void, the disk full. A BODY WALKS OFF AN EDGE ONLY WHERE THE LEVEL SAYS IT "
    "MAY (roadmap 173): level_factory's gate over undeclared drops, its lattice laid off the round "
    "coordinates and its probe the body's size (0.216.0, 0.216.1, 0.219.0, 0.222.0); deli_counter's "
    "declared drops carry their own off-mesh links and a stacked shaft's holes are declared (0.226.0, "
    "0.232.0); lot and dispatch carry the link to the package (0.125.0; 0.5.3). HOLES IN FLOORS, RARE "
    "AND CAUSED (roadmaps 255, 260, 264, 265, 269): the walker's open-floor table and no wall under a "
    "hole (deli_counter 0.223.0, 0.234.0, 0.235.0); every hole a cause -- a torn edge, the spoil, the "
    "crew's kit, a floor hatch (deli_counter 0.236.0, 0.236.1; zoo 1.114.0, 1.114.1); a hole an optional "
    "route, in one level in four (deli_counter 0.237.0, level_factory 0.221.0). THE ROOF HATCH (roadmap "
    "170): a lid on every roof hatch, its hole the lid's own (zoo 1.113.0, 1.113.1; deli_counter 0.224.0, "
    "0.224.1, 0.239.0). A RAMP'S CUT STOPS AT ITS HEAD (deli_counter 0.241.0): install test 10, this "
    "set's first, stopped at the export -- its pick, seed 9205, stood a parking garage whose ramp's slab cut ran "
    "half a run past the ramp's head, 33 edges the drop-edge gate refused, and every library ramp did the same; "
    "the cut now stops at the head, railed, with a landing past it, and cold run 9356 made that level at 0 "
    "interventions. INTERIORS MERGED (roadmap 266): an enterable building's static modules merged per "
    "room cell and material, a lit face kept whole, 11 % fewer draws (level_factory 0.223.0, 0.224.0). "
    "A BUILDING'S LADDERS AND MARKERS SURVIVE THE MERGE (level_factory 0.227.0): install test 11, this set's "
    "second, "
    "made that level and its walk found no ladder -- the buildings' merge had removed every building's ladders "
    "and gameplay markers with the slots it took apart, from 0.223.0 on and in no release; a slot holding what "
    "the merge cannot carry now stays whole, and cold run 9357 made the level with them. "
    "THE WALKER'S LOOK REVIEWS OF 2026-10-19 AND 2026-10-20: a desk's computer is on (roadmap 148, zoo "
    "1.115.0); a street phone faces the sidewalk in one of four booths, its marks small and mostly "
    "weather (roadmap 210, lot 0.126.0, zoo 1.116.0, 1.117.0); a face's upper windows stand over the "
    "openings below them, mirrored pairs together (roadmap 79, deli_counter 0.238.0); a morning and a "
    "high noon, each time of day its own preset (roadmap 217, lux 0.79.0, level_factory 0.225.0). GATES "
    "THAT READ WHAT GODOT READS: any greybox in a themed package refused, the legacy fire escape and the "
    "vehicle ramp skinned (roadmap 168: level_factory 0.218.0, 0.220.0); the z-fight gate at WARN and "
    "reading a scene's transforms as Godot does (roadmap 177: level_factory 0.218.1, 0.218.2, "
    "deli_counter 0.230.0); an isolated building a major finding (roadmap 178: lot 0.124.0); a build's "
    "freshness watches every module it writes with, and reads nothing from the layout lint (roadmap 259: "
    "deli_counter 0.229.0, 0.233.0). A STRANGER'S PATH (roadmaps 251, 252, 256, 257): the light bake "
    "counts only the scenes it draws, the output layers shown, what the venv's three pins bring held, "
    "the backdrop's ground unshaded (level_factory 0.212.0 to 0.215.1). SMALLER: a store's video poker "
    "cabinets (roadmap 196: deli_counter 0.228.0, 0.231.0, 0.231.1); a vault ledge the furniture's own "
    "look, and skinned (deli_counter 0.227.0, level_factory 0.217.0); a switchback's top leg (deli_counter "
    "0.225.0); a roof AC unit and a club bar built as their species (roadmap 267: deli_counter 0.240.0); "
    "lux's runtime scaffolding ownerless in the editor (0.78.0); patina's Godot half removed (0.32.0); the "
    "perf panel's primitives no longer called triangles (roadmap 261: level_factory 0.226.0). "
    "level_factory 0.226.1 and 0.226.2 re-ground the doctor's certified table to this set. Install test 12 "
    "(docs/findings/stranger_install/install_test_12/) made this set's package, unzipped it into a folder "
    "that had never held a factory, and typed START_HERE.md's commands into cmd.exe, `setup --venv` and "
    "its PyPI download included: " + RESULT + " The real-tool smoke (LF_TOOLS_DIR=<factory> pytest "
    "tests/real_tools) licenses Level Factory {level_factory}'s grounded table, which the doctor reads. "
    "WHAT THIS SET DOES NOT CERTIFY: Linux (no Linux machine has run it; the walker has none); and every "
    "item earlier descriptions name as open that nobody has closed since. THE 1.40.0 STORY AND EVERYTHING "
    "BEFORE IT, unchanged: "
)

ENTRY = (
    "## [factory-v1.41.0] - 2026-10-20\n"
    "\n"
    "Seven tools move:\n"
    "{table}\n"
    "\n"
    "- **A body walks off an edge only where the level says it may** (roadmap\n"
    "  173): undeclared drops are refused, declared ones carry their own\n"
    "  navigation links into the package.\n"
    "- **Holes in floors, rare and caused** (roadmaps 255, 260, 264, 265, 269):\n"
    "  the open-floor table; every hole a torn edge, a broken floor or a floor\n"
    "  hatch, with what came down below it; one level in four carries one.\n"
    "- **The roof hatch** (roadmap 170): a lid on every one, its hole the lid's.\n"
    "- **A ramp's cut stops at its head**, railed, with a landing past it: found\n"
    "  by install test 10, which stopped on a parking garage's ramp.\n"
    "- **A building's ladders and markers survive the merge**: found by install\n"
    "  test 11, whose walk found no ladder -- the interiors' merge had removed\n"
    "  them, in no release.\n"
    "- **Interiors merged** (roadmap 266): 11 % fewer draws.\n"
    "- **The walker's look reviews:** desks' computers on (148); street phones\n"
    "  facing the sidewalk in four booths, their marks small and mostly weather\n"
    "  (210); upper windows over the openings below (79); a morning and a high\n"
    "  noon (217).\n"
    "- **Gates that read what Godot reads** (roadmaps 168, 177, 178, 259).\n"
    "- **A stranger's path** (roadmaps 251, 252, 256, 257): the bake counts\n"
    "  what it draws, the layers shown, the pins' packages held, the ground\n"
    "  unshaded.\n"
    "\n"
    "Certified by install test 12: the set's package, unzipped into a fresh\n"
    "folder, made restaurant_row_001 with START_HERE.md's commands, the\n"
    "PyPI download included. " + RESULT + "\n"
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
    assert m["factory_version"] == "1.40.0", m["factory_version"]
    assert not m["description"].startswith("1.41.0"), "already promoted"
    assert m["description"].startswith("1.40.0 certifies"), m["description"][:40]
    result = pathlib.Path(__file__).with_name("factory_1_41_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 12 result to certify from (factory_1_41_0_result.txt)"
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
    m["factory_version"] = "1.41.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.40.0] - 2026-10-14\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.40.0 -> 1.41.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
