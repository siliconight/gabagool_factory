# Gabagool Factory 1.42.1

**A correction of 1.42.0; use this one.** Everything 1.42.0 brought -- the
authoring panel, the supermarket, the bank inside and out -- with two things
1.42.0 got wrong put right:

- **Setup reads this set as certified.** 1.42.0 was certified with Level
  Factory's table of the tool versions it was grounded against still at
  1.41.0's, so `setup` warned that five tools had drifted and asked for
  re-certification. Level Factory 0.262.2 grounds all eight. 1.42.0's own
  record said promoting the manifest would clear that warning; it did not.
- **Every tool carries its MIT licence.** Dispatch, Laser Tag, Patina and
  Pipeline each committed theirs after the tag 1.42.0 named, so 1.42.0
  shipped them without it. Their new releases carry it and change nothing
  else.

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup --venv`,
one `.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.42.1.zip`, 74,851,169 bytes,
sha256 `1d8da53529a6286d56ac96eb2cfd29e0d3e43d9c1c3fd0e765ccfce3df75cc62`.

**What is in it.** The tracked files of the factory root at `factory-v1.42.1`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (159 building shells). Built by
`tools/make_factory_package.ps1 -Tag factory-v1.42.1`. It is the package
install test 15 certified, file for file -- 5,461 of its 5,464 files the same
bytes, the rest the ones the certification itself wrote: the manifest, the
changelog and the assistant's notes (one changed, one added).

| tool | version | since 1.42.0 |
|---|---|---|
| Deli Counter | 0.286.2 | was 0.286.1 |
| Dispatch | 0.5.4 | was 0.5.3 |
| Laser Tag | 0.32.1 | was 0.32.0 |
| Level Factory | 0.262.2 | was 0.262.0 |
| Lot | 0.135.0 | |
| Lux | 0.80.0 | |
| Patina | 0.32.1 | was 0.32.0 |
| Pipeline | 0.6.1 | was 0.6.0 |
| Pixelcoat | 0.63.0 | |
| Zoo | 1.142.0 | |

Deli Counter 0.286.2 releases a line in its migrations index that was
committed after 0.286.1's tag; nothing in a level moves.

**How it was certified.** Install test 15 built the set's package, unzipped
it into a folder that had never held a factory and typed `START_HERE.md`'s
commands. `setup --venv` passed with no drift and no warning at all, where
1.42.0's test read five drifted tools. `make` built the restaurant row in 8.5
minutes and shipped seed 9205 at PASS 100; `walk` took 5.1 minutes, climbed
both of the deli's ladders and passed all five camera stations. Every tool's
version then matched the manifest (`verify-manifest --strict`), every tool's
commit was its own version's tag, and this zip was built from those tags.
Install test 14 had passed the same way on a set that check then refused:
the migrations index line above, released by 0.286.2.

**What this set does not certify.** Linux, which nobody has run; the bank's
vault, which still needs work (pale wrapped bricks with blue straps, racks in
rows, deposit boxes on every wall); and every item the roadmap names as open.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; `setup --venv` downloads three Python packages and what they need
once, into the factory's own folder. The first `make` takes about eight to
nine minutes on a 2020-class desktop.
