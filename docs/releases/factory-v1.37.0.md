# Gabagool Factory 1.37.0

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup --venv`,
one `.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.37.0.zip`, 71,993,074 bytes,
sha256 `1bef210373da15b002307c4db2bec31194448760380bbb6c2aa0e2e0cae0d294`.

**What is in it.** The tracked files of the factory root at `factory-v1.37.0`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (146 building shells), which git does not track.
Built by `tools/make_factory_package.ps1 -Tag factory-v1.37.0`; nothing from
the run record (cold runs, findings, patches) travels.

| tool | version | since 1.36.0 |
|---|---|---|
| Deli Counter | 0.207.1 | was 0.205.0 |
| Dispatch | 0.5.2 | |
| Laser Tag | 0.25.0 | |
| Level Factory | 0.178.3 | was 0.172.1 |
| Lot | 0.115.0 | was 0.106.0 |
| Lux | 0.74.0 | was 0.72.0 |
| Patina | 0.30.0 | |
| Pipeline | 0.6.0 | |
| Pixelcoat | 0.62.0 | |
| Zoo | 1.97.0 | was 1.94.0 |

**What a level gets that 1.36.0's did not.**
- **Neighbours drawn by a template.** A brief can ask for the buildings
  beside the objective to be drawn by a cluster template from the
  1990s-adjacency guide (`cluster: auto`), and the site audit reports the
  guide's adjacency rules and gameplay targets beside its own findings.
- **A block with a back lane.** The `block` road grammar adds a second
  side street and a service lane behind the row: one loop, a way in and a
  way back that is not the way in.
- **An edge.** A fence at the plate's edge and, beyond it, a backdrop laid
  by recipe (rowhomes, a water tower, warehouses, trees with silhouettes in
  clusters), with a glow at the horizon where a town would be.
- **Lights where the work is.** Ceiling rows laid to the work below them,
  over the aisles between shelf runs, and a fixture a bay in a home's
  rooms; one bad tube a room rather than a row.
- **A cheaper street.** The road paint is one mesh a colour, in 32 m cells,
  and the ground, slabs and sidewalks are cut to a 32 m tile where the
  package bakes its lights: on one test level, about 360 fewer draw calls
  and 0.75 ms less frame time a view at the median, no mesh over the
  engine's 8-light cap.

**What the first hour gets that 1.36.0's did not.** `setup --venv` makes
the factory's Python from Blender's without printing Blender's
`sitecustomize` error at every step, and the doctor reads every row PASS.
`walk` no longer strips the bake from the package `make` built: in 1.36.0
and before, walking a level left its package unbaked. And the walk's
visual check no longer fails a level for a failing fluorescent tube's
flicker.

**How it was certified.** By the thing the package is for: install test 6
(`docs/findings/stranger_install/`) built this set's package, unzipped it
into a folder that had never held a factory, and typed `START_HERE.md`'s
commands into a terminal -- `setup --venv` and its download of Pillow,
pygltflib and jsonschema included, for the first time with no stand-in.
`setup` exited 0 with every doctor row passing; `make` exited 0 in 32.3
minutes and built the same level install tests 3 to 5 had built (0 of 79
and 0 of 111 blockers, baked, the closure clean); `walk` exited 0 with all
five review stations passing, and the package was still baked after it.
No deviation from the page.

**What this set does not certify.** Linux, which nobody has run; and every
item the roadmap names as open.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; the package finds them (`setup --blender`, `--godot` when it cannot),
and `setup --venv` downloads three Python packages once, into the factory's
own folder. The first `make` takes about half an hour on a 2020-class
desktop; the walk copy it offers is a Godot project you can open and play.
