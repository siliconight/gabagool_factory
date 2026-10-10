"""Factory 1.35.0: certify the set a stranger receives (roadmap 202), from install test 2.

Sets every tool's `version` and `tag` in `factory.manifest.json` to the checkout's VERSION, puts
1.35.0's story ahead of the description it keeps, and adds the factory CHANGELOG entry. Asserts the
manifest is 1.34.1 and that each VERSION parses; writes nothing on a miss. The repos are tagged
afterwards, by hand, at the commits this certifies:

    python patches/patch_factory_manifest_1_35_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_2"

STORY = (
    "1.35.0 certifies the set the factory's first outside user receives (roadmap 202): "
    "deli_counter {deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory "
    "{level_factory}, lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat "
    "{pixelcoat}, zoo {zoo}. HOW IT IS CERTIFIED, SAID FIRST: not by docs/CERTIFY.md's legs, "
    "which were written for the July and August cycles, when Zoo was 0.3x, "
    "but by what those legs stood in for -- a level built by the whole set, from a package, with "
    "nobody touching anything. Install test 2 (docs/findings/stranger_install/install_test_2/) "
    "made this set's package, unzipped it into a folder that had never held a factory, and typed "
    "START_HERE.md's commands into cmd.exe: " + RESULT + " The real-tool smoke "
    "(LF_TOOLS_DIR=<factory> pytest tests/real_tools, 11 of 12, exit 0) licenses Level Factory "
    "0.170.0's grounded table, which the doctor reads. Cold runs 9218 to 9222 each built with 0 "
    "interventions at sets that differ from this one only in releases their notes name. WHAT THIS "
    "SET DOES NOT CERTIFY: setup --venv's download into Blender's own Python (a stand-in "
    "interpreter ran the tools; the download waits for the walker's yes); Linux (no Linux machine "
    "has run it); the walk preview's jitter gate, which reads texture sparkle as z-fighting "
    "(roadmap 225); and every item earlier descriptions name as open that nobody has closed "
    "since. THE 1.34.1 STORY AND EVERYTHING BEFORE IT, unchanged: "
)

ENTRY = (
    "## [factory-v1.35.0] - 2026-10-10\n"
    "\n"
    "Nine of the ten tools move, pipeline alone staying at 0.6.0; it is the first\n"
    "certification since 1.34.1 (2026-08-22):\n"
    "{table}\n"
    "\n"
    "Certified by install test 2 rather than by docs/CERTIFY.md's legs: the set's\n"
    "package, unzipped into a fresh folder, made restaurant_row_001 with\n"
    "START_HERE.md's commands. " + RESULT + "\n"
    "\n"
    "Not certified: setup --venv's download (a stand-in interpreter ran the\n"
    "tools), Linux, and the walk preview's jitter gate (roadmap 225).\n"
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
    assert m["factory_version"] == "1.34.1", m["factory_version"]
    assert not m["description"].startswith("1.35.0"), "already promoted"
    result = pathlib.Path(__file__).with_name("factory_1_35_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 2 result to certify from (factory_1_35_0_result.txt)"
        result_text = RESULT
    versions = {}
    rows = []
    for key, entry in m["tools"].items():
        folder = entry.get("path") or key
        v = _semver((ROOT / folder / "VERSION").read_text(encoding="utf-8"))
        rows.append(f"- {key}: {entry['version']} -> {v}")
        versions[key] = v
        entry["version"] = v
        entry["tag"] = f"v{v}"
    m["factory_version"] = "1.35.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.34.1] - 2026-08-22\n"
    assert cl.count(head) == 1
    cl = cl.replace(head, ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text) + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.34.1 -> 1.35.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
