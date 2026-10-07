"""Roadmap: item 202, handing the factory to a stranger.

    python patch_roadmap_202.py

Appends after item 201, anchored on 201's last line as patch_roadmap_201.py
left it (1,238,378 bytes, LF, as read 2026-10-07). Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

#: Item 201's LAST line, which is the file's last line.
TAIL = ("- A test pins it, and a cold run of a library brief shows the score where the brief put it.\n")

ADD = r"""
*STATUS: OPEN 2026-10-07 -- measured, not started: a stranger's first hour with the factory package would cost interventions before any level is built. The certified set is six weeks stale (`level-factory verify-manifest`: 8 DRIFT, 1 INCOMPATIBLE, 1 OK); `level_factory init` writes all ten tool paths blank and the cold driver copies the previous run's instead (cold run 9194 stopped there); the driver hardcodes the factory root; 7 of 11 repos declare no dependencies; no page says how to install. The level-making code itself is portable.*

**202. Handing the factory to a stranger.** Measured 2026-10-07, when the walker said a collaborator gets "a full export of the tools" in about two weeks. CLAUDE.md's first paragraph says the deliverable is that somebody who has never seen this repo points these tools at their own game and gets levels out. Every zero-intervention run so far (9189; the breadth sweep's 8 of 10, then 10 of 10) was earned on this machine, by a driver that knows the workarounds. A stranger's setup steps are interventions too, and nobody has counted them.

**WHAT TRAVELS.** `tools/make_factory_package.ps1` zips every tracked file of all eleven repos at their checked-out HEADs (`git archive`; uncommitted work does not travel). Tracked bytes on 2026-10-07: the root 856 MB (`docs/cold_runs` 518, `docs/findings` 306, `patches` 20), Lux 48, Deli Counter 40, Lot 27, Zoo 7, Level Factory 4, the other five under 3 each -- about 987 MB, of which 824 MB is the run record.

**THE CERTIFIED SET IS SIX WEEKS STALE.** The factory already has a handoff mechanism (README, "Two-layer versioning"): `factory.manifest.json` pins the tool versions certified together, each tool is tagged, and the factory is tagged `factory-vX.Y.Z`. It last ran 2026-08-22 (factory 1.34.1, commit 2bb1911). `level-factory verify-manifest --factory .` on 2026-10-07: DRIFT on Deli Counter (certified 0.94.0, installed 0.202.0), Dispatch, Laser Tag, Level Factory (0.48.0, 0.152.0), Lot, Lux (0.16.0, 0.68.2), Patina and Pixelcoat; INCOMPATIBLE on Zoo (0.48.0, 1.81.0, a major bump); OK on Pipeline only. Tagging stopped with it: the newest tags are Deli Counter v0.101.0, Level Factory v0.53.0, Lux v0.27.0, Zoo v0.50.0, Lot v0.49.0, Pixelcoat v0.16.0, Laser Tag v0.9.0, Patina v0.21.0, Dispatch v0.4.2, and only Pipeline's HEAD is tagged. `docs/CERTIFY.md` is the runbook -- Zoo's walkabout, Pixelcoat's signage packs, Level Factory's suites with the real-tool smoke, the engine leg, then promote the manifest and tag -- written for 1.1.0 -> 1.2.0 with this machine's paths. The README tells a newcomer to run the lockstep check, which today tells them their install is broken.

**WHAT A STRANGER HITS, in the order they would hit it.**
- **No setup page.** `docs/PACKAGE_README.md` is the readme of one exported level (lot_demo_001), not of the factory. The package script's last line points the recipient at `USING_THE_FACTORY.md`, the operator's charter (the routing table, the gap protocol), which does not say how to install anything.
- **Dependencies.** Four repos declare theirs in a `pyproject.toml`: Level Factory (nothing at runtime; PySide6 is its optional desktop GUI), Pixelcoat, Patina and Dispatch. Seven declare none, and between them import Pillow, numpy, pygltflib, jsonschema, PyYAML and cairosvg (Deli Counter's `migrations/ai_review.py` also imports `anthropic`; it is advisory and never gates). Nothing installs the set in one step. Python: Level Factory asks >= 3.11; this machine runs 3.14.4. Blender: Zoo's README says 4.2+ or 5.x, Deli Counter's says 4.x, this machine runs 5.1.1. Godot: 4.7.
- **Tool paths.** `level_factory init` writes `tools.local.json` with all ten paths blank -- eight tool repos, Blender and Godot -- and tells the user to fill them in and run `doctor`. The cold driver (`tools/cold_drive/cold_drive.sh`) never does that: it copies `workspaces/cold-$PREV-ws/tools.local.json`. A stranger has no previous run. Cold run 9194 stopped exactly there on 2026-10-07, because 9168's workspace had been retired.
- **The driver's root.** `cold_drive.sh` and `sweep_one.sh` `cd /c/Projects/gabagool_studios/gabagool_factory`; `stage_batch.py` writes to `C:/Projects/gabagool_studios/gabagool_factory/docs/cold_runs`.
- **Developer scripts.** 23 PowerShell scripts carry this machine's paths: 14 in the tool repos (Level Factory 2, Lot 3, Lux 2, Patina 1, Pixelcoat 2, Zoo 4 -- previews, smoke walks, theme rebuilds, and Zoo's walkabout, which CERTIFY.md runs) and 9 in the root's `scripts/`.
- **Four brief fields reach nothing** (item 200). A stranger filling in the request template (`docs/LEVEL_STANDARD.md`, Appendix A) sets them and hears nothing back.

**WHAT IS ALREADY PORTABLE: the level-making code.** Searched every tracked text file in the ten tool repos for `C:/Projects`, `C:/blender`, `C:/Godot`, `C:/Users` and `/c/Projects`, either slash. Level Factory's `packages/` and `apps/` name such paths only in docstrings about catching non-portable `res://` paths. The tools find each other through `tools.local.json`. Godot and Blender resolve from a flag, then the environment, then the usual installs, then PATH. Lot's `cater.py` tries `$DELI_COUNTER` and a relative `../deli_counter` before any absolute guess. The test hits are deliberate fixtures (Dispatch's leak detector, Patina's Windows temp paths, Level Factory's non-portable `res://C:/` cases).

**REFUTED, kept:** the first search, restricted to `.py .sh .ps1 .gd .json .cfg .toml` and without the `/c/` spelling, read zero files in every tool repo. It missed the PowerShell scripts' `C:\` paths and the test fixtures, and the wider search above replaced it.

**NEXT.** The measure is a cold run of the install itself.
- Re-certify the set and tag every repo. Every cold run's `_runs/cold/<label>/before.json` already records each tool's version at `--begin`, so a run that ends at 0 interventions is stronger evidence of "verified together" than CERTIFY.md's smoke; promoting the manifest from one is worth weighing against running the runbook.
- `init` fills `tools.local.json` from `factory.manifest.json`'s tool list and the Godot and Blender resolution chain, and `doctor` passes before the first run. The driver derives its root from its own path and stops copying.
- One install step for the Python packages, with the Python, Godot and Blender versions stated once.
- One "first level" page: install, doctor, request, run, walk, score.
- A lean package: tools and docs, with the run record optional.
- **The test:** unpack into a fresh path (not `C:\Projects\gabagool_studios`), follow only that page, and count every question or edit as an intervention. Fix until zero, then zip at the tags.

**OPEN DECISIONS (the walker's).**
- Does the collaborator make levels (a zip at the certified tags is enough) or change tools (they need the remotes and `docs/SHIPPING_A_CHANGE.md`)?
- What is their machine? A Mac turns this item into a port: the drivers are bash and PowerShell over Windows paths.
"""


def main():
    data = RM.read_bytes()
    assert len(data) == 1238378, "PIPELINE_ROADMAP.md is %d bytes, read at 1,238,378" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(TAIL) and text.count(TAIL) == 1, "the tail anchor is not the file's end"
    RM.write_bytes((text + ADD).encode("utf-8"))
    print("roadmap: 202 appended")


if __name__ == "__main__":
    main()
