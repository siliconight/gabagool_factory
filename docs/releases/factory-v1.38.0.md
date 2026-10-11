# Gabagool Factory 1.38.0

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup --venv`,
one `.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.38.0.zip`, 72,042,969 bytes,
sha256 `9089b92cab37af2e5628d8ae0aef294fa8a358efb36737036ad16536f1c2b7ee`.

**What is in it.** The tracked files of the factory root at `factory-v1.38.0`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (146 building shells), which git does not track.
Built by `tools/make_factory_package.ps1 -Tag factory-v1.38.0`; nothing from
the run record (cold runs, findings, patches) travels.

| tool | version | since 1.37.0 |
|---|---|---|
| Deli Counter | 0.208.0 | was 0.207.1 |
| Dispatch | 0.5.2 | |
| Laser Tag | 0.25.0 | |
| Level Factory | 0.178.6 | was 0.178.3 |
| Lot | 0.116.0 | was 0.115.0 |
| Lux | 0.75.0 | was 0.74.0 |
| Patina | 0.30.0 | |
| Pipeline | 0.6.0 | |
| Pixelcoat | 0.62.0 | |
| Zoo | 1.100.0 | was 1.97.0 |

**What a level gets that 1.37.0's did not.**
- **A home's rooms hang a dome.** A flush-mount dome where an office troffer
  hung, lit warm from under its bowl; it costs what the troffer did.
- **Fewer draws for the same fixtures.** A light fixture's parts that share
  a material are one mesh -- inside each fixture, never across two -- so a
  pendant's cord and socket, a sign box's arms and cabinet and a wall pack's
  arm and body each draw once: on one test level, 26 fewer draw calls a view
  at the median and up to 49, with no frame time the harness can see.
- **A service lane with its own lamps**, evenly spread, the street's own
  fixture, pools of light with dark between.
- **Caps on top.** The bollard, the rooftop exhaust fan, the soda cup and
  the helmet carry the domed caps their recipes always meant; they had been
  built hanging inside their bodies.

**What the first hour gets that 1.37.0's did not.** The light bake no
longer gives up when its editor window lacks focus -- a bake runs while you
use the machine, and an unfocused editor slows itself tenfold -- and a bake
that fails is tried once more on a fresh copy. Before this, a level could
ship unbaked with only a warning to say so.

**How it was certified.** By the thing the package is for: install test 7
(`docs/findings/stranger_install/`) built this set's package, unzipped it
into a folder that had never held a factory, and typed `START_HERE.md`'s
commands into a terminal -- `setup --venv` and its three pins included
(from pip's cache, which test 6's download had filled). `setup` exited 0
with every doctor row passing at this set's versions and 0 drift lines;
`make` exited 0 in 34.1 minutes and built the same level install tests 3 to
6 had built (0 of 79 and 0 of 111 blockers, baked on the bake's first
attempt, the closure clean); `walk` exited 0 in 10.9 minutes with both
ladders climbed and all five review stations passing, and the package was
still baked after it; and the package's fixture layers carry Zoo 1.100.0's
merge -- the deli's 23 pendants, 23 metal meshes. No deviation from the
page.

**What this set does not certify.** Linux, which nobody has run; and every
item the roadmap names as open.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; the package finds them (`setup --blender`, `--godot` when it cannot),
and `setup --venv` downloads three Python packages once, into the factory's
own folder. The first `make` takes about half an hour on a 2020-class
desktop; the walk copy it offers is a Godot project you can open and play.
