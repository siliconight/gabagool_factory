# Gabagool Factory 1.39.0

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup --venv`,
one `.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.39.0.zip`, 72,209,878 bytes,
sha256 `c2aeb287c6e5aea5bb1e7535cc0ba44673c6cd5df5ebad396b5c9ca07dba9d85`.

**What is in it.** The tracked files of the factory root at `factory-v1.39.0`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (146 building shells), which git does not track.
Built by `tools/make_factory_package.ps1 -Tag factory-v1.39.0`; nothing from
the run record (cold runs, findings, patches) travels. It is the package
install test 8 certified, file for file -- 4,797 of its 4,800 files the same
bytes, the other three the ones the certification itself wrote (the
manifest, the changelog and the roadmap).

| tool | version | since 1.38.0 |
|---|---|---|
| Deli Counter | 0.209.1 | was 0.208.0 |
| Dispatch | 0.5.2 | |
| Laser Tag | 0.27.0 | was 0.25.0 |
| Level Factory | 0.193.1 | was 0.178.6 |
| Lot | 0.117.0 | was 0.116.0 |
| Lux | 0.75.0 | |
| Patina | 0.30.0 | |
| Pipeline | 0.6.0 | |
| Pixelcoat | 0.62.0 | |
| Zoo | 1.103.0 | was 1.100.0 |

**A level in a quarter of the time.** On the path a stranger types, the
first `make` took 7.9 minutes where 1.38.0's took 34.1, and `walk` 5.6 where
it took 10.9 -- the same level, on the same machine. The factory's own
end-to-end run of one level went from 30.4 minutes to 6.9 over cold runs
9245 to 9259, with no hand-edits, each cut measured against a control before
it shipped and none moving a finding:
- **The graders stop waiting on the clock.** Laser Tag's evaluations and the
  walk tests run on a fixed clock with their navigation updated on their own
  thread, three at a time: every grade and every finding as before on the
  fifteen candidates, over five missions, it was measured on.
- **The art builds side by side.** Blender builds three at a time; each
  building's composition runs beside the others.
- **The export imports each model once**, keeps its import cache for the
  walk copy, and gives the light bake's editor the scene groups it would
  otherwise spend twenty seconds reading.
- **The bake waits less and draws nothing while it bakes.**

**Two runs make one level.** Two exports of a level now bake the same
lightmap byte for byte, and two runs from scratch the same lightmap in all
but 15 of its 16.8 million texels: the bake no longer catches a failing
lamp's flicker at whatever moment it was pressed, and every model a run's
Zoo jobs build comes out byte for byte the same twice. A change's effect can
be shown by comparing two runs rather than argued over noise.

**What a level gets that 1.38.0's did not.**
- **Dressed roofs.** Roofs carry props for the first time, by what the
  building is: a kitchen a unit or two, a vent and its hood fan; a shop a
  unit or two and a vent; an office units and vent stacks; a warehouse or a
  market more, and skylights; a home a vent or two; a parking deck nothing.
  Across the library that is 5.7 props a roof, none on a hatch or where a
  ladder's climber steps off, no two roofs alike, a water tank only on a
  roof 12 m up, and each roof drawn about once a kind of prop.
- **Textures as an editor leaves them**: VRAM-compressed with mipmaps
  everywhere, the walker's call; less texture memory, and what every editor
  had shown anyway.

**What the graders see that 1.38.0's did not.** Laser Tag's enemies are the
agent contract's body -- the npc_standard capsule, 0.35 m, and the arrival
radius derived from it -- where they had kept a 0.40 m pill and jammed in
openings a real enemy passes. A layout that puts its enemies on the crew at
once now reads as one: in the certifying test, one candidate the picker
passed over went from PASS_WITH_TUNING, its crew surviving 75.7 s on
average, to WARN, its crew dying in 7.0 s, on the same scene byte for byte.
The old body under the new clock reads the old report, so the body moved
it, not the speed work.

**How it was certified.** By the thing the package is for: install test 8
(`docs/findings/stranger_install/`) built this set's package, unzipped it
into a folder that had never held a factory, and typed `START_HERE.md`'s
commands into a terminal -- `setup --venv` and its three pins included
(from pip's cache). `setup` exited 0 with every doctor row passing at this
set's versions and 0 drift lines; `make` exited 0 in 7.9 minutes and built
the same level install tests 3 to 7 had built (0 of 81 and 0 of 113
blockers, three roofs dressed, baked on the bake's first attempt, the
closure clean); `walk` exited 0 in 5.6 minutes with both ladders climbed and
all five review stations passing, and the package was still baked after it;
and the package's fixture layers are 1.38.0's -- the deli's 23 pendants, 23
metal meshes. No deviation from the page.

**What this set does not certify.** Linux, which nobody has run; and every
item the roadmap names as open -- among them the level a failing lamp's lens
should bake at, which is left at its cycle's first instant for now.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; the package finds them (`setup --blender`, `--godot` when it cannot),
and `setup --venv` downloads three Python packages once, into the factory's
own folder. The first `make` takes about eight minutes on a 2020-class
desktop; the walk copy it offers is a Godot project you can open and play.
