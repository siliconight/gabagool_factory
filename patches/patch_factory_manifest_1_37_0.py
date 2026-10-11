"""Factory 1.37.0: certify the set install test 5 made a level with (roadmap 202).

Sets every tool's `version` and `tag` in `factory.manifest.json` to the checkout's VERSION, puts
1.37.0's story ahead of the description it keeps, and adds the factory CHANGELOG entry. Asserts the
manifest is 1.36.0, that each VERSION parses, and that the tools that moved are exactly the five
the story names; writes nothing on a miss. The repos are tagged afterwards, at the commits this
certifies:

    python patches/patch_factory_manifest_1_37_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_5"
MOVED = {"deli_counter", "level_factory", "lot", "lux", "zoo"}

STORY = (
    "1.37.0 certifies the set install test 5 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. FIVE TOOLS MOVED FROM 1.36.0. level_factory: the doctor reads the long-paths flag "
    "(0.173.0); the backdrop beyond the plate's edge ships as MultiMeshes and the brief or the "
    "archetype names what stands there (0.174.0-0.175.1); the buildings beside the objective are "
    "drawn by a cluster template when the brief asks (0.176.0/0.176.1); the `block` road grammar, a "
    "second side street and a service lane behind the row, one loop (0.177.0); the road paint's "
    "meshes bake, are published and are carried into the package (0.177.1-0.177.3); the site spec "
    "tells Lot the lights bake (0.178.0); a venv made from Blender's Python starts without an "
    "error (0.178.1, install test 4's finding); its grounded table names this set (0.178.2). lot: "
    "the fence at the plate's edge and the backdrop beyond it by recipe (0.107.0-0.110.0); the "
    "adjacency and gameplay-target audits (0.111.0/0.112.0); a lane stops at a street (0.113.0); "
    "the road paint as one mesh a colour, then in 32 m cells, and the plate tile following the "
    "bake (0.114.0/0.115.0, roadmap 231: -360 draws and -0.75 ms p95 a heading median on 9233's "
    "lot, cold runs 9236/9237). deli_counter: ceiling rows laid to the work, over the aisles, and a "
    "home's room a fixture a bay (0.206.0-0.207.1, roadmap 229). zoo: the backdrop's rowhome, "
    "water tower, warehouse and a tree with a silhouette (1.95.0-1.97.0). lux: the glow at the "
    "horizon (0.73.0) and one bad tube a room, not a row (0.74.0). Install test 5 "
    "(docs/findings/stranger_install/install_test_5/) made this set's package, unzipped it into a "
    "folder that had never held a factory, and typed START_HERE.md's commands into cmd.exe, "
    "`setup --venv` and its PyPI download included: " + RESULT + " The real-tool smoke "
    "(LF_TOOLS_DIR=<factory> pytest tests/real_tools) licenses Level Factory {level_factory}'s "
    "grounded table, which the doctor reads. WHAT THIS SET DOES NOT CERTIFY: Linux (no Linux "
    "machine has run it; the walker has none), and every item earlier descriptions name as open "
    "that nobody has closed since. THE 1.36.0 STORY AND EVERYTHING BEFORE IT, unchanged: "
)

ENTRY = (
    "## [factory-v1.37.0] - 2026-10-11\n"
    "\n"
    "Five tools move:\n"
    "{table}\n"
    "\n"
    "- **level_factory:** the cluster-template draw, the `block` grammar's\n"
    "  service lane and loop, the backdrop as MultiMeshes, the road paint's\n"
    "  meshes baked and carried, the site spec telling Lot the lights bake,\n"
    "  a clean venv from Blender's Python, and the grounded table for this set.\n"
    "- **lot:** the fence and the backdrop by recipe, the adjacency and target\n"
    "  audits, the lane, and the street's draws (roadmap 231).\n"
    "- **deli_counter:** ceiling rows to the work (roadmap 229).\n"
    "- **zoo:** the backdrop's pieces and a tree with a silhouette.\n"
    "- **lux:** the horizon glow, and one bad tube a room.\n"
    "\n"
    "Certified by install test 5: the set's package, unzipped into a fresh\n"
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
    assert m["factory_version"] == "1.36.0", m["factory_version"]
    assert not m["description"].startswith("1.37.0"), "already promoted"
    result = pathlib.Path(__file__).with_name("factory_1_37_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 5 result to certify from (factory_1_37_0_result.txt)"
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
    m["factory_version"] = "1.37.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.36.0] - 2026-10-10\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.36.0 -> 1.37.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
