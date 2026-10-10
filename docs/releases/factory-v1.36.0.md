# Gabagool Factory 1.36.0

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup`, one
`.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.36.0.zip`, 71,707,131 bytes,
sha256 `34654895350a402513930165c7a77cd662f858045ae6e80ea1105970c4702832`.

**What is in it.** The tracked files of the factory root at `factory-v1.36.0`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (146 building shells), which git does not track.
Built by `tools/make_factory_package.ps1 -Tag factory-v1.36.0`; nothing from
the run record (cold runs, findings, patches) travels.

| tool | version |
|---|---|
| Deli Counter | 0.205.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.172.1 |
| Lot | 0.106.0 |
| Lux | 0.72.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.94.0 |

**How it was certified.** Not by a smoke test but by the thing the package
is for: install test 3 (`docs/findings/stranger_install/`) built this set's
package, unzipped it into a folder that had never held a factory, and typed
`START_HERE.md`'s commands into a terminal. `setup` exited 0 with every tool
passing the doctor; `make` exited 0 in 32.1 minutes and built the same level
cold run 9223 had built (0 of 52 and 0 of 74 blockers); `walk` exited 0 with
all five review stations passing. One counted deviation: the tester's own
Python stood in for `setup --venv`'s download.

**What this set does not certify.** `setup --venv`'s download of Pillow,
pygltflib and jsonschema into Blender's own Python (untested here); Linux;
and every item the roadmap names as open.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; the package finds them (`setup --blender`, `--godot` when it cannot).
The first `make` takes about half an hour on a 2020-class desktop; the walk
copy it offers is a Godot project you can open and play.
