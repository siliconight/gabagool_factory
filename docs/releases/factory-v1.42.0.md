# Gabagool Factory 1.42.0

> **Superseded by [1.42.1](https://github.com/siliconight/gabagool_factory/releases/tag/factory-v1.42.1); use that
> one.** This set's `setup` warns that five tools have drifted and asks for re-certification -- it was certified
> with Level Factory's grounded versions still at 1.41.0's -- and Dispatch, Laser Tag, Patina and Pipeline ship
> without their MIT licences. 1.42.1 corrects both and changes nothing in a level.

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup --venv`,
one `.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.42.0.zip`, 74,842,363 bytes,
sha256 `e0fe65f487bfa6ff177d77b99c83039498dfc721c4012ca122c58a9b2a6aa87f`.

**What is in it.** The tracked files of the factory root at `factory-v1.42.0`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (159 building shells), which git does not track.
Built by `tools/make_factory_package.ps1 -Tag factory-v1.42.0`; nothing from
the run record (cold runs, findings, patches) travels. It is the package
install test 13 certified, file for file -- 5,455 of its 5,463 files the same
bytes. Of the rest, four are the ones the certification itself wrote (the
manifest, the changelog, the roadmap and the assistant's release note); the
other four are licences: install test 13 packaged each tool's latest commit,
and Dispatch, Laser Tag, Pipeline and Patina each gained an MIT `LICENSE` on
2026-10-26, after the tags this set names. So this package carries them as
1.41.0 did -- no `LICENSE` of their own for the first three, Patina's earlier
one -- under the root's MIT `LICENSE`. 1.42.1 re-releases those four with
theirs.

| tool | version | since 1.41.0 |
|---|---|---|
| Deli Counter | 0.286.1 | was 0.241.0 |
| Dispatch | 0.5.3 | |
| Laser Tag | 0.32.0 | |
| Level Factory | 0.262.0 | was 0.227.0 |
| Lot | 0.135.0 | was 0.126.0 |
| Lux | 0.80.0 | was 0.79.0 |
| Patina | 0.32.0 | |
| Pipeline | 0.6.0 | |
| Pixelcoat | 0.63.0 | was 0.62.0 |
| Zoo | 1.142.0 | was 1.117.0 |

Six tools moved, over 37 of the factory's own end-to-end runs (cold runs
9358 to 9394).

**A level without a terminal.** Level Factory's Factory panel in Godot
checks the setup, generates a level's layouts, plans them top-down, walks
the chosen one, changes its settings and shows them in the next walk, and
exports it -- no terminal, no JSON, no AI.

**The supermarket.** Numbered aisles whose shelves sell what the markers
over them say, a produce section, a cooler wall, tile underfoot and a
store's lamp density, and a light bake that reaches the next lamp along.

**The bank, inside and out.** Lit and tiled, plastered over dark wood
panelling, with a glass storefront to the street framed in aluminium. A
check desk with its pens on chains, officers' desks with their CRTs, a
queue, waiting chairs, plants, a clock, cameras, the printed offers and
rate board, and a teller line naming the bank over numbered windows. A vault
of steel money racks -- strapped bricks banded by denomination, deposit
bags -- cash carts and a wall of numbered deposit boxes with brass locks.
Outside, a time-and-temperature sign, a night depository and a drive-up
lane with its tube station, canopy, clearance bar and painted lanes; one
name on every face of it.

**Every piece on what it is made of.** About 2,800 placed pieces in the
library asked for a material their kind does not offer, many of them street
rust; each now asks for its own.

**Also.** Civic rooms furnished as themselves; the scout model and the
exploded axonometric of every building; stairs solid underneath and stair
holes railed; queues and crowd barriers; no parking at a bus stop and a
signal facing every approach.

**How it was certified.** Install test 13 built the set's package, unzipped
it into a folder that had never held a factory and typed `START_HERE.md`'s
commands. `setup --venv` passed. `make` built the restaurant row in 8.5
minutes and shipped seed 9205 at PASS 100, the pick tests 10 to 12 made;
seed 9104 graded PASS_WITH_TUNING 89 where test 12 graded it PASS 90.
`walk` took 5.2 minutes, climbed both of the deli's ladders and passed all
five camera stations, and the package still carried its light bake after
it. Every tool's version then matched the manifest (`verify-manifest
--strict`), each was tagged at the commit tested, and this zip was built
from those tags.

**What this set does not certify.** Linux, which nobody has run; the
bank's vault, which the factory's own review of it says still needs work
(pale wrapped bricks with blue straps, racks in rows, deposit boxes on every
wall); and every item the roadmap names as open.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; the package finds them (`setup --blender`, `--godot` when it cannot),
and `setup --venv` downloads three Python packages and what they need once,
into the factory's own folder. The first `make` takes about eight to nine
minutes on a 2020-class desktop; the walk copy it offers is a Godot project
you can open and play.
