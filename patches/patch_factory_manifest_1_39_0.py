"""Factory 1.39.0: certify the set install test 8 made a level with (roadmap 202 and 239).

Sets every tool's `version` and `tag` in `factory.manifest.json` to the checkout's VERSION, puts
1.39.0's story ahead of the description it keeps, and adds the factory CHANGELOG entry. Asserts the
manifest is 1.38.0, that each VERSION parses, and that the tools that moved are exactly the five
the story names; writes nothing on a miss. The repos are tagged afterwards, at the commits this
certifies:

    python patches/patch_factory_manifest_1_39_0.py [--result-pending]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PENDING = "--result-pending" in sys.argv
RESULT = "RESULT_INSTALL_8"
MOVED = {"deli_counter", "laser_tag", "level_factory", "lot", "zoo"}

STORY = (
    "1.39.0 certifies the set install test 8 made a level with (roadmap 202): deli_counter "
    "{deli_counter}, dispatch {dispatch}, laser_tag {laser_tag}, level_factory {level_factory}, "
    "lot {lot}, lux {lux}, patina {patina}, pipeline {pipeline}, pixelcoat {pixelcoat}, zoo "
    "{zoo}. FIVE TOOLS MOVED FROM 1.38.0, most of it roadmap 239's cold-run speed work: the "
    "factory's own end-to-end run of one level went from 30.4 minutes to 6.9 (cold runs 9245 to "
    "9259) with no hand-edits, each cut measured against a control before it shipped and none "
    "moving a finding (125 -> 122 across the series, every item attributed in cold run 9247: an "
    "enemy no longer jams, Laser Tag 0.26.0, and two gate conflicts were the gate's, Deli "
    "Counter 0.209.1). laser_tag: an enemy is the agent contract's body too (0.26.0, roadmap 197); the "
    "navigation map updates on the evaluation's thread, so its clock need not wait on real "
    "seconds (0.27.0). lot: the walk test likewise, its navigation on its own thread and its "
    "clock fixed (0.117.0). level_factory: roof props reach a level, a job of their own per "
    "enterable building (0.179.0); the Godot cap follows the machine and the width the graders "
    "were proven at (0.179.1); Laser Tag's evaluation and the walk test on a clock that does not "
    "wait (0.180.0, 0.180.1); the greybox census reads the bake's import cache, the shared "
    "textures' pins are applied again after the last import, the editor's import of the "
    "lightmap is kept (0.181.0 to 0.183.0); the scheduler's caps overridable for one invocation, "
    "Blender jobs three at a time, a job's independent commands side by side (0.184.0 to "
    "0.186.0); the bake's lightmap requests ride the export's second import pass, the export "
    "keeps its import cache for the walk copy, every model is imported once with its final "
    "settings (0.187.0 to 0.189.0); every texture VRAM-compressed as an editor leaves it, the "
    "walker's call (0.190.0); the bake's editor is given the scene groups it would read first, "
    "stops its clock so two exports of one workspace bake the same bytes, and stops drawing for "
    "the bake, its work copy copied on threads and removed behind it (0.191.0 to 0.193.0); "
    "re-grounded to this set (0.193.1). zoo: a roof's props keep off its hatches and landings, "
    "stand in the box they occupy and draw as one roof (1.101.0); what a roof carries follows "
    "what the building is, and fewer, 16.2 props a roof to 5.7 across the library (1.102.0); a "
    "mesh leaves with its faces in one order, so every Zoo job builds the same bytes twice and "
    "two cold runs bake one lightmap -- 9260 and 9261 alike in all but 15 of 16,777,216 texels "
    "(1.103.0). deli_counter: a roof slot says where a body steps off a ladder, and a building "
    "carries a roof-props layer (0.209.0); a stair's column ends at the ceiling of the top floor "
    "it serves, so the circulation gate stops counting a roof prop over a stair two slabs down "
    "(0.209.1). Install test 8 "
    "(docs/findings/stranger_install/install_test_8/) made this set's package, unzipped it into a "
    "folder that had never held a factory, and typed START_HERE.md's commands into cmd.exe, "
    "`setup --venv` and its PyPI download included: " + RESULT + " The real-tool smoke "
    "(LF_TOOLS_DIR=<factory> pytest tests/real_tools) licenses Level Factory {level_factory}'s "
    "grounded table, which the doctor reads. WHAT THIS SET DOES NOT CERTIFY: Linux (no Linux "
    "machine has run it; the walker has none), the level a failing lamp's lens should bake at "
    "(left at its cycle's first instant until the walker calls it), and every item earlier "
    "descriptions name as open that nobody has closed since. THE 1.38.0 STORY AND EVERYTHING "
    "BEFORE IT, unchanged: "
)

ENTRY = (
    "## [factory-v1.39.0] - 2026-10-12\n"
    "\n"
    "Five tools move:\n"
    "{table}\n"
    "\n"
    "- **level_factory, laser_tag, lot:** roadmap 239's cold-run speed work --\n"
    "  the graders on a clock that does not wait on real seconds, three at a\n"
    "  time; Blender jobs three at a time and a job's commands side by side;\n"
    "  every model imported once and the import cache kept for the walk copy;\n"
    "  the bake's editor given its scene groups, its clock and its drawing\n"
    "  stopped: one level's end-to-end run 30.4 -> 6.9 minutes, no cut\n"
    "  moving a finding. Every texture VRAM-compressed as an editor leaves it\n"
    "  (the walker's call); roof props reach a level.\n"
    "- **laser_tag:** an enemy is the agent contract's body too (roadmap 197).\n"
    "- **zoo:** a roof's props keep off its hatches and landings and follow\n"
    "  what the building is (roadmap 181); every mesh's faces in one order, so\n"
    "  two cold runs bake one lightmap.\n"
    "- **deli_counter:** a roof slot says where a body steps off a ladder; a\n"
    "  stair's column ends at the ceiling of the top floor it serves.\n"
    "\n"
    "Certified by install test 8: the set's package, unzipped into a fresh\n"
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
    assert m["factory_version"] == "1.38.0", m["factory_version"]
    assert not m["description"].startswith("1.39.0"), "already promoted"
    assert m["description"].startswith("1.38.0 certifies"), m["description"][:40]
    result = pathlib.Path(__file__).with_name("factory_1_39_0_result.txt")
    result_text = result.read_text(encoding="utf-8").strip() if result.is_file() else ""
    if not result_text:
        assert PENDING, "no install test 8 result to certify from (factory_1_39_0_result.txt)"
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
    m["factory_version"] = "1.39.0"
    m["description"] = STORY.format(**versions).replace(RESULT, result_text) + m["description"]
    out = (json.dumps(m, indent=2, ensure_ascii=True) + "\n").replace("\n", eol)
    cl_raw = CHANGELOG.read_bytes()
    cl_eol = b"\r\n" if b"\r\n" in cl_raw else b"\n"
    cl = cl_raw.decode("utf-8").replace("\r\n", "\n")
    head = "## [factory-v1.38.0] - 2026-10-11\n"
    assert cl.count(head) == 1
    entry_text = ENTRY.format(table="\n".join(rows)).replace(RESULT, result_text)
    cl = cl.replace(head, entry_text + head)
    MANIFEST.write_bytes(out.encode("utf-8"))
    CHANGELOG.write_bytes(cl.encode("utf-8").replace(b"\n", cl_eol))
    print("factory 1.38.0 -> 1.39.0")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
