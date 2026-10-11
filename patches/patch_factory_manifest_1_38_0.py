"""Factory 1.38.0: certify the set install test 7 made a level with (roadmap 202).

Sets every tool's `version` and `tag` in `factory.manifest.json` to the checkout's VERSION, puts
1.38.0's story ahead of the description it keeps, and adds the factory CHANGELOG entry. Asserts the
manifest is 1.37.0, that each VERSION parses, and that the tools that moved are exactly the five
the story names; writes nothing on a miss. The repos are tagged afterwards, at the commits this
certifies:

    python patches/patch_factory_manifest_1_38_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_7"
MOVED = {"deli_counter", "level_factory", "lot", "lux", "zoo"}

STORY = (
    "1.38.0 certifies the set install test 7 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. FIVE TOOLS MOVED FROM 1.37.0. deli_counter: a home's room hangs a flush-mount dome "
    "where it hung an office troffer, the same rows and positions (0.208.0, roadmap 229). lux: the "
    "dome's rig, warm, its lamp under the bowl and its pool to the bay's corner (0.75.0). zoo: the "
    "dome fixture (1.98.0) and its fix, the glass under the canopy and the dome two meshes as a "
    "troffer is (1.98.1; cold run 9241: +0 draws at 53 of 53 headings against the troffers it "
    "replaced); a cargo container's roof at the walls' valley shade (1.99.0, a look; its premise, "
    "9226's pale slab, was a backdrop warehouse's lit window and is retracted); the hemisphere "
    "helper keeping the upper half it names, so the bollard's, the exhaust fan's, the soda cup's "
    "and the helmet's caps stand on their bodies (1.99.1, roadmap 232); a fixture's same-material "
    "parts merged inside it and never across two (1.100.0, roadmap 233: 437 submissions to 402 "
    "over cold run 9239's three fixture layers). lot: a service lane lights its own length "
    "(0.116.0, roadmap 199). level_factory: re-grounded to this set (0.178.4), and the light bake "
    "keeps its editor awake, asks for the scene until it opens and keeps the editor's output (0.178.5; "
    "cold run 9242 shipped unbaked when an unfocused editor outlasted a bake counted in frames), and a "
    "bake that fails is tried once more on a fresh copy (0.178.6; cold run 9243's editor read its "
    "lightmap image back empty, and the same package baked on the next try). "
    "Install test 7 "
    "(docs/findings/stranger_install/install_test_7/) made this set's package, unzipped it into a "
    "folder that had never held a factory, and typed START_HERE.md's commands into cmd.exe, "
    "`setup --venv` and its PyPI download included: " + RESULT + " The real-tool smoke "
    "(LF_TOOLS_DIR=<factory> pytest tests/real_tools) licenses Level Factory {level_factory}'s "
    "grounded table, which the doctor reads. WHAT THIS SET DOES NOT CERTIFY: Linux (no Linux "
    "machine has run it; the walker has none), and every item earlier descriptions name as open "
    "that nobody has closed since. THE 1.37.0 STORY AND EVERYTHING BEFORE IT, unchanged: "
)

ENTRY = (
    "## [factory-v1.38.0] - 2026-10-11\n"
    "\n"
    "Five tools move:\n"
    "{table}\n"
    "\n"
    "- **deli_counter:** a home's room hangs a dome (roadmap 229).\n"
    "- **lux:** the dome's rig.\n"
    "- **zoo:** the dome and its fix; a container's roof at the valley shade;\n"
    "  the hemisphere's upper half, four props' caps on top (roadmap 232); a\n"
    "  fixture's same-material parts one mesh inside it (roadmap 233).\n"
    "- **lot:** a service lane lights its own length (roadmap 199).\n"
    "- **level_factory:** the grounded table for this set, and a light bake\n"
    "  that survives an unfocused editor (cold run 9242).\n"
    "\n"
    "Certified by install test 7: the set's package, unzipped into a fresh\n"
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
    assert m["factory_version"] == "1.37.0", m["factory_version"]
    assert not m["description"].startswith("1.38.0"), "already promoted"
    result = pathlib.Path(__file__).with_name("factory_1_38_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 7 result to certify from (factory_1_38_0_result.txt)"
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
    m["factory_version"] = "1.38.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.37.0] - 2026-10-11\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.37.0 -> 1.38.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
