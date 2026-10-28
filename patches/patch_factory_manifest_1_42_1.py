"""Factory 1.42.1: certify the set install test 14 made a level with (roadmap 202).

Copied from `patch_factory_manifest_1_42_0.py`, as every release copies the one before: the manifest's description
is CUMULATIVE, and this puts 1.42.1's story ahead of the description it keeps. Sets every tool's `version` and `tag`
in `factory.manifest.json` to the checkout's VERSION and adds the factory CHANGELOG entry. Asserts the manifest is
1.42.0, that each VERSION parses, and that the tools that moved are exactly the six the story names; writes nothing
on a miss. The repos are tagged before this runs, at the commits install test 14 packaged.

1.42.1 IS A CORRECTION. 1.42.0 was certified with Level Factory's `contracts.GROUNDED` at 1.41.0's versions, so its
doctor reads five tools as drifted -- install test 13's setup said so, and 1.42.0's result said the promotion would
clear it, which it does not: the doctor reads that table, not this manifest. And four tools shipped without the MIT
`LICENSE` each committed after its tag.

    python patches/patch_factory_manifest_1_42_1.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_14"
MOVED = {"deli_counter", "dispatch", "laser_tag", "level_factory", "patina", "pipeline"}

STORY = (
    "1.42.1 certifies the set install test 14 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. A CORRECTION OF 1.42.0, SIX TOOLS MOVED. 1.42.0 was certified with level_factory's grounded "
    "table at 1.41.0's versions, so its doctor read deli_counter, lot, lux, pixelcoat and zoo as drifted "
    "and asked for re-certification; its result said the manifest's promotion would clear that, and it "
    "does not -- the doctor reads level_factory's table. level_factory {level_factory} re-grounds all "
    "eight rows. deli_counter {deli_counter} releases its migrations index line, committed after 1.42.0's tag, which verify-manifest read STALE. And dispatch, laser_tag, patina and pipeline each committed its MIT LICENSE after the tag "
    "1.42.0 named, so 1.42.0 shipped them without it: {dispatch}, {laser_tag}, {patina} and {pipeline} are "
    "the releases that carry it. Nothing else moved. " + RESULT + " "
)

ENTRY = (
    "## [factory-v1.42.1] - 2026-10-28\n"
    "\n"
    "Six tools move:\n"
    "{table}\n"
    "\n"
    "- **The doctor reads this set as certified.** 1.42.0 was certified with\n"
    "  Level Factory's grounded table still at 1.41.0's versions, so setup\n"
    "  warned that five tools had drifted and asked for re-certification. Its\n"
    "  record said promoting the manifest would clear that; it did not. Level\n"
    "  Factory 0.262.1 re-grounds all eight rows.\n"
    "- **Every tool carries its MIT licence.** Dispatch, Laser Tag, Patina and\n"
    "  Pipeline each committed theirs after the tag 1.42.0 named, so 1.42.0\n"
    "  shipped without them; these releases carry them, and change nothing else.\n"
    "\n"
    "Certified by install test 14: the set's package, unzipped into a fresh\n"
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
    assert m["factory_version"] == "1.42.0", m["factory_version"]
    assert not m["description"].startswith("1.42.1"), "already promoted"
    assert m["description"].startswith("1.42.0 certifies"), m["description"][:40]
    result = pathlib.Path(__file__).with_name("factory_1_42_1_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 14 result to certify from (factory_1_42_1_result.txt)"
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
    m["factory_version"] = "1.42.1"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.42.0] - 2026-10-28\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.42.0 -> 1.42.1")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
