"""Roadmap 202 NARROWED: a stranger's path exists, and its first install test made 9222's level.

Replaces 202's status block and adds what shipped and what the test found to its body. Each anchor
must match exactly once; nothing is written on a miss. The generated index is regenerated
afterwards by `tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_202_install.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-07 -- measured, not started. The walker's bar: a consumer installs "
    "Blender and Godot and nothing else. Today a stranger's first hour with the factory package "
    "would cost interventions before any level is built. The certified set is six weeks stale "
    "(`level-factory verify-manifest`: 8 DRIFT, 1 INCOMPATIBLE, 1 OK); `level_factory init` "
    "writes all ten tool paths blank and the cold driver copies the previous run's instead "
    "(cold run 9194 stopped there); the driver hardcodes the factory root; 7 of 11 repos "
    "declare no dependencies; no page says how to install. The level-making code itself is "
    "portable.*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- a stranger's path exists, and its first install test made "
    "cold run 9222's level from a fresh unpack, figure for figure (`docs/findings/"
    "stranger_install/`). Level Factory 0.167.0 to 0.171.0 (tool discovery, `setup` and "
    "`setup --venv`, the doctor asking the tools' interpreter, `make` and `pick`, a re-grounded "
    "certified table, hints that name what the person has, a walk preview that starts at the "
    "player_start and a visual check that can see); `START_HERE.md` with `factory.cmd` and "
    "`factory.sh`; a 72 MB package that carries the building library. Left: the real `setup "
    "--venv` (a download, the walker's yes), a Linux run, the factory manifest and tags, and a "
    "second install test at these releases.*\n"
)

BODY_ANCHOR = (
    "- *As first filed:* \"Does the collaborator make levels ... or change tools?\" and \"What "
    "is their machine? A Mac turns this item into a port.\"\n"
)
PROOF = (
    "\n**SHIPPED, 2026-10-10** (`docs/findings/stranger_install/`, measured first):\n"
    "- **The library did not travel:** 0 of 146 shells in a tracked-files package, so a "
    "stranger's every level would have placed one generated shell N times. "
    "`tools/make_factory_package.ps1` now carries Deli Counter's `build/` less `floorplans/` "
    "(837 files), only when Deli Counter is clean and its `build_freshness.py` calls it up to "
    "date, stamped later than the sources `git archive` dates; and leaves the run record out "
    "(`-WithRecord` keeps it). First package 72.1 MB.\n"
    "- **Level Factory 0.167.0:** `init` fills `tools.local.json` (the manifest's checkouts; "
    "Blender and Godot from a flag, `factory.local.json`, the environment, PATH, Blender's "
    "installs); `setup` records them; a blank `python_executable` is the interpreter running "
    "Level Factory everywhere (jobs ran `python3`, two probes `python`); the doctor's "
    "`tools_python` asks THAT interpreter its version and imports. Under Blender's own Python "
    "3.13.9 it names the gap: Pillow, pygltflib, jsonschema.\n"
    "- **Level Factory 0.168.0:** `setup --venv` makes `<factory>/.venv` from Blender's Python "
    "and installs the three, pinned to what every suite here ran on.\n"
    "- **Level Factory 0.169.0:** `make` runs a batch start to finish as the cold driver does, "
    "each leg its own process, stopping at the first failure or open blocker; `pick` moves the "
    "driver's candidate rule in, and agrees with it on all 46 cold workspaces.\n"
    "- **The front door:** `START_HERE.md` (install, `.\\factory setup --venv`, one `make`, "
    "`walk`); `factory.cmd` and `factory.sh` find Blender's Python; `docs/first_level/` is "
    "9222's batch. The cold driver now derives its root, takes its tools from `init` and stops "
    "on the doctor.\n"
    "\n"
    "**INSTALL TEST 1** (`docs/findings/stranger_install/install_test_1/`). The package "
    "unzipped into `C:\\stranger_202\\gabagool` and `START_HERE.md` typed into cmd.exe: `setup` "
    "0, `make` 0 in 31.8 minutes, `walk` 0. One deviation, counted: `setup --python` stood in "
    "for `--venv`, whose download waits for the walker's yes. The level matched 9222's: 0 of 52 "
    "and 0 of 74 blockers, seed_9104 on the same lines, the same deal, 479 models and 4,259 "
    "users baked. It also found, each fixed: `factory` not run from the current folder (the "
    "page now says `.\\factory`); eight stale-certification WARNs (0.170.0 re-grounds); hints "
    "naming `level-factory`, `godot`, `python tools/walk_export.py` and PowerShell's `&` "
    "(0.170.0, 0.171.0); the walk preview's player at the origin, and its visual check passing "
    "five 100% black frames shot under the shader warm-up's cover (0.171.0, which then FAILS "
    "two of 9222's ladder stations on jitter, 3.60% and 2.33%: a defect the blind check had "
    "hidden, cause not established).\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for name, anchor in (("status", OLD_STATUS), ("body", BODY_ANCHOR)):
        n = text.count(anchor)
        assert n == 1, (name, "anchor matches", n, "times")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(BODY_ANCHOR, BODY_ANCHOR + PROOF)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**202. "), "202's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 202: NARROWED, the install path built and tested once")


if __name__ == "__main__":
    main()
