"""Roadmap 227, filed: the doctor's long-paths WARN is a constant, and the depth it warns about is real.

Appends item 227 after 226, the roadmap's last item, with its status block directly above its
heading. Asserts the file ends where 226's body ends; nothing is written on a miss. The generated
index is regenerated afterwards by `tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_227_long_paths.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

TAIL = (
    "(shell 0 of 52, art 0 of 74, findings 74 to 74). The facade right of the band is darker, "
    "its lamp now 5 m left; whether that stretch wants another light is a taste call.\n"
)
ITEM = (
    "\n*STATUS: OPEN 2026-10-10 -- measured, and the fix drafted: Level Factory 0.173.0 "
    "(`patches/patch_lf_long_paths.py`, 9 tests failing on 0.172.1) reads the flag, weighs the "
    "workspace's depth against the 217 a level writes, and PASSes where either is fine. Applied "
    "after factory 1.36.0's tags, not before: it would have moved the set the install test "
    "certified.*\n"
    "\n"
    "**227. The doctor's long-paths WARN is a constant, and the depth it warns about is real.** "
    "`docs/findings/long_paths/`. The one WARN left on a stranger's first `setup` (install tests 2 "
    "and 3) is `windows_long_paths: verify LongPathsEnabled registry flag for deep asset paths`. "
    "`level_factory/packages/tools/doctor.py:202` prints it on every Windows machine and reads "
    "nothing, so it cannot PASS where long paths are on, and where they are off it cannot say "
    "whether this workspace is deep enough to matter.\n"
    "- **Measured on cold runs 9222 and 9223** (`depth.py`): a level writes files 217 characters "
    "below its workspace, a Godot editor-state file in the lux_apply staging copy; the pipeline's "
    "own deepest output, a texture's provenance file, is 193 below. Those workspaces sit 69 "
    "characters deep and held 725 and 440 files past Windows' 260. The longest single name is "
    "151, under Linux's 255.\n"
    "- **So the budget with the flag off is a workspace of 42 characters,** and Explorer's "
    "Extract All into a stranger's Downloads puts one at about 70.\n"
    "- **What fails with the flag off is not measured:** this machine's flag is 1, and setting "
    "it is a system setting. It could be Python's `open`, Godot's import or Blender's export, and "
    "a Godot editor cache that cannot be written may be harmless where a provenance file is not.\n"
    "\n"
    "**The fix, drafted as Level Factory 0.173.0:** the row reads the flag; on, PASS; off or "
    "unreadable, PASS where the workspace's deepest file stays within 260, naming how far it "
    "reaches, and WARN past it, naming the reach, the 42-character budget and the two remedies, a "
    "shorter folder or an administrator turning long paths on. `setup` weighs `<factory>\\levels`, "
    "the workspace `START_HERE.md` makes; `doctor` its own. It stays a WARN, not a FAIL, until the "
    "failure itself is measured.\n"
    "\n"
    "Owner: Level Factory.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.endswith(TAIL), repr(text[-200:])
    assert "**227. " not in text, "227 is already filed"
    text = text + ITEM
    i = text.index(ITEM) + 1
    assert text[i:].startswith("*STATUS: OPEN 2026-10-10"), "227's status is not where it should be"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 227 filed")


if __name__ == "__main__":
    main()
