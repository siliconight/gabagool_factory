# Gabagool Factory 1.40.0

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup --venv`,
one `.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.40.0.zip`, 73,006,203 bytes,
sha256 `039e504a2af66a2b89e136008419d7a8fa9804cf26cd059379b222a108a24f00`.

**What is in it.** The tracked files of the factory root at `factory-v1.40.0`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (159 building shells), which git does not track.
Built by `tools/make_factory_package.ps1 -Tag factory-v1.40.0`; nothing from
the run record (cold runs, findings, patches) travels. It is the package
install test 9 certified, file for file -- 4,975 of its 4,978 files the same
bytes, the other three the ones the certification itself wrote (the
manifest, the changelog and the roadmap).

| tool | version | since 1.39.0 |
|---|---|---|
| Deli Counter | 0.222.0 | was 0.209.1 |
| Dispatch | 0.5.2 | |
| Laser Tag | 0.32.0 | was 0.27.0 |
| Level Factory | 0.211.1 | was 0.193.1 |
| Lot | 0.123.0 | was 0.117.0 |
| Lux | 0.77.0 | was 0.75.0 |
| Patina | 0.31.0 | was 0.30.0 |
| Pipeline | 0.6.0 | |
| Pixelcoat | 0.62.0 | |
| Zoo | 1.112.0 | was 1.103.0 |

Seven tools moved, over 51 of the factory's own end-to-end runs (cold runs
9262 to 9312), every one with no hand-edits.

**A new kind of level: the city street.** An urban brief stands a
continuous wall of brick mid-rises across the street, puts the mission's
buildings among mid-rises on the near side, keeps the wall's lowest blocks
across from the action and lets it rise away from it, and opens and closes
each run of the wall on a corner block: a shop on its ground floor under a
canvas awning. Walk-ups carry steel fire escapes on their fronts, and a
city block's street trees stand one every 30 ft.

**Philadelphia's streets.** A wooden pole line along one kerb of every
street carries the street lamps and its wires; rowhomes stand three steps up
on a stoop, with an iron railing each side and a tar roof; the street has
its manhole covers and storm inlets.

**Built to the body.** Every walkable door is at least the agent contract's
1.25 m, and the stair landing, the vault's opening and the census's
body-sized numbers read the contract too, so a change to the body re-sizes
them with it.

**Bots that move like the crew.** Laser Tag's crew and guards keep to the
navigation mesh they plan on and step up as a body does; a guard held by
another bot is blocked rather than stuck; and an arrival counts at the
point, not at the end of a path that stops short of it.

**Cheaper to draw, smaller to ship.** The sun is baked while the lightmap
shows: about 1,850 fewer draw calls and 3 ms on the level it was priced on.
The reflection atlas is sized to the level's own probes, 314.6 to 65.6 MiB of
texture memory. A walk-up's fire escape draws as part of its front, and a
package carries only the buildings its scene stands, without the kit
modules its merged buildings were built from.

**The same level twice.** Two runs of one command now build every model and
the lightmap byte for byte the same, so a change's effect is a comparison of
two runs rather than an argument over noise.

**The walk of 2026-10-14, each fix the walker's call.**
- A lit shop's window shows its goods up close, not a room glowing brighter
  than they are.
- Every desk's computer, keyboard and phone face whoever sits at it.
- A shop's door says its trade instead of repeating the name on the band
  above it.
- There is ground under the backdrop past the fence.
- A switchback stair is filled to the ground under its second flight
  instead of hanging a storey over it.
- The delis' basement wall runs wall to wall, with a door into the utility
  room.

**How it was certified.** By the thing the package is for: install test 9
(`docs/findings/stranger_install/`) built this set's package, unzipped it
into a folder that had never held a factory, and typed `START_HERE.md`'s
commands into a terminal -- `setup --venv` and its three pins included
(from pip's cache). `setup` exited 0 with every doctor row passing at this
set's versions and 0 drift lines. `make` exited 0 in 7.9 minutes, as
1.39.0's did, with 0 blockers, three roofs dressed, the bake on its first
attempt and the closure clean; it built another of the level's three
candidates than 1.39.0's test had, because a pick now breaks a tie on the
grade and then on the lower seed. `walk` exited 0 in 5.2 minutes with all
four of the level's ladders climbed and all nine review stations passing,
and the package was still baked after it. Every finding that moved since
1.39.0's test is accounted for, the grader's share by grading each test's
scenes with each version of the grader. No deviation from the page.

**What this set does not certify.** Linux, which nobody has run; the cost of
the ground under the backdrop, shipped unpriced; the exact versions of the
nine Python packages `setup --venv`'s three pins bring with them, which pip
picks afresh each install (one, wrapt, moved between 1.39.0's test and this
one); and every item the roadmap names as open.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; the package finds them (`setup --blender`, `--godot` when it cannot),
and `setup --venv` downloads three Python packages and what they need once,
into the factory's own folder. The first `make` takes about eight minutes on
a 2020-class desktop; the walk copy it offers is a Godot project you can
open and play.
