"""Factory 1.36.0: certify the set install test 3 made a level with (roadmap 202).

Sets every tool's `version` and `tag` in `factory.manifest.json` to the checkout's VERSION, puts
1.36.0's story ahead of the description it keeps, and adds the factory CHANGELOG entry. Asserts the
manifest is 1.35.0, that each VERSION parses, and that the tools that moved are exactly the two
the story names; writes nothing on a miss. The repos are tagged afterwards, by hand, at the commits
this certifies:

    python patches/patch_factory_manifest_1_36_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_3"
MOVED = {"level_factory", "lot"}

STORY = (
    "1.36.0 certifies the set install test 3 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. TWO TOOLS MOVED FROM 1.35.0. level_factory: the walk preview's visual check fails a "
    "fight, not a sparkle (0.172.0, roadmap 225), the check that failed install test 2's walk; "
    "and its grounded table names Lot {lot} (0.172.1), so a stranger's first doctor reads no "
    "drift. lot: a lamp or a tree keeps out of a shop band's span (0.106.0, roadmap 226), proven "
    "by cold run 9223 with 0 interventions. Install test 3 "
    "(docs/findings/stranger_install/install_test_3/) made this set's package, unzipped it into a "
    "folder that had never held a factory, and typed START_HERE.md's commands into cmd.exe: "
    + RESULT + " The real-tool smoke (LF_TOOLS_DIR=<factory> pytest tests/real_tools, 11 of 12, "
    "exit 0) licenses Level Factory {level_factory}'s grounded table, which the doctor reads. WHAT "
    "THIS SET DOES NOT CERTIFY: setup --venv's download into Blender's own Python (a stand-in "
    "interpreter ran the tools; the download waits for the walker's yes); Linux (no Linux machine "
    "has run it); and every item earlier descriptions name as open that nobody has closed since. "
    "THE 1.35.0 STORY AND EVERYTHING BEFORE IT, unchanged: "
)

ENTRY = (
    "## [factory-v1.36.0] - 2026-10-10\n"
    "\n"
    "Two tools move:\n"
    "{table}\n"
    "\n"
    "- **level_factory:** the walk preview's visual check fails a fight, not a\n"
    "  sparkle (0.172.0, roadmap 225), and the grounded table names Lot\n"
    "  {lot} (0.172.1).\n"
    "- **lot:** a lamp or a tree keeps out of a shop band's span (0.106.0,\n"
    "  roadmap 226, proven by cold run 9223).\n"
    "\n"
    "Certified by install test 3: the set's package, unzipped into a fresh\n"
    "folder, made restaurant_row_001 with START_HERE.md's commands. " + RESULT + "\n"
    "\n"
    "Not certified: setup --venv's download (a stand-in interpreter ran the\n"
    "tools) and Linux.\n"
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
    assert m["factory_version"] == "1.35.0", m["factory_version"]
    assert not m["description"].startswith("1.36.0"), "already promoted"
    result = pathlib.Path(__file__).with_name("factory_1_36_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 3 result to certify from (factory_1_36_0_result.txt)"
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
    m["factory_version"] = "1.36.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.35.0] - 2026-10-10\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows), lot=versions["lot"]).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.35.0 -> 1.36.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
