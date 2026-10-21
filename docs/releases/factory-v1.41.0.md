# Gabagool Factory 1.41.0

The standalone package: every tool it takes to make a level, with the
building library, in one zip. Unzip it anywhere, install Blender 4.2+ and
Godot 4.7, and follow `START_HERE.md` inside it: `.\factory setup --venv`,
one `.\factory -C levels make`, and `walk` to play what came out. Windows and
Linux (`sh factory.sh`); Linux has not yet been run by anyone.

**Asset:** `gabagool_factory_package_factory-v1.41.0.zip`, 73,795,839 bytes,
sha256 `f992d92763689510646a322cd2b4dd7e25d4c8e16d2375ccd37c061d4e9ec7e0`.

**What is in it.** The tracked files of the factory root at `factory-v1.41.0`
and of each tool at the tag `factory.manifest.json` names, plus Deli
Counter's built library (159 building shells), which git does not track.
Built by `tools/make_factory_package.ps1 -Tag factory-v1.41.0`; nothing from
the run record (cold runs, findings, patches) travels. It is the package
install test 12 certified, file for file -- 5,181 of its 5,186 files the same
bytes, the rest the ones the certification itself wrote: the manifest, the
changelog, the roadmap, and the assistant's notes (two changed, one added).

| tool | version | since 1.40.0 |
|---|---|---|
| Deli Counter | 0.241.0 | was 0.222.0 |
| Dispatch | 0.5.3 | was 0.5.2 |
| Laser Tag | 0.32.0 | |
| Level Factory | 0.227.0 | was 0.211.1 |
| Lot | 0.126.0 | was 0.123.0 |
| Lux | 0.79.0 | was 0.77.0 |
| Patina | 0.32.0 | was 0.31.0 |
| Pipeline | 0.6.0 | |
| Pixelcoat | 0.62.0 | |
| Zoo | 1.117.0 | was 1.112.0 |

Seven tools moved, over 45 of the factory's own end-to-end runs (cold runs
9313 to 9357). Every run that finished needed no hand-edit; six were stopped
by a gate whose finding a tool then answered, and one was void when the disk
filled.

**Nothing to walk off by accident.** A body walks off an edge only where the
level says it may: an undeclared drop indoors stops the export, and a
declared one carries its own navigation link into the package for the
game's AI. A parking garage's ramp, a floor hatch's opening and a stair's
hole are each railed or declared.

**Holes in floors are rare, and say why.** Stairs and ladders are the way
between floors; about one level in four carries a hole, and each has a cause
you can see -- a cut with the crew's tarp, saw and work light beside it, a
floor that gave way with what came down below it, or a floor hatch with its
lid standing open. Roof hatches have lids, and their holes match them.

**Life in the rooms and on the street.** Office computers are on, each desk
on one of six period screens. Street payphones face the sidewalk, each booth
in one of four looks, marked small and mostly by weather -- a few hand tags,
initials keyed into the paint, rain run down from the roof. Shop and house
fronts stack their upper windows over the openings below, mirrored pairs
together.

**Five times of day.** Morning and high noon join afternoon, evening and
midnight, each its own sky and sun.

**Cheaper to draw.** An enterable building's interior is merged per room and
material: about 11 % fewer draw calls where it was priced. What the merge
cannot carry keeps its piece whole -- a building's ladders, its gameplay
markers (spawns, objectives, cover, found by group), a lamp's marker -- so the
package has everything the building was composed with.

**A stranger's path.** The light bake counts only what it draws, the output
layers are shown, what `setup --venv`'s three pins bring is held, and the
doctor's table names this set.

**How it was certified.** By the thing the package is for, three times. Install
test 10 built the set's first package, unzipped it into a folder that had
never held a factory and typed `START_HERE.md`'s commands: `setup` passed
and `make` stopped at the export, because the first level's pick stood a
parking garage whose ramp's floor opening ran 5 m past the top of the ramp.
Deli Counter 0.241.0 fixed it at the source, for every ramp in the library,
and a cold run made that exact level with no hand-edit. Install test 11 then
made that level from its package, and its walk found no ladder to climb: the
new interior merge had removed every building's ladders and gameplay markers
along with the pieces it merged -- in this set only, never in a release.
Level Factory 0.227.0 keeps them, and cold run 9357 made the level with them.
Install test 12 built the package again with that fix, unzipped it into a
fresh folder and typed the same commands: `setup` passed, `make` built the
garage level in 8 minutes, and `walk` climbed both of its ladders and passed
all five of its camera stations.

**What this set does not certify.** Linux, which nobody has run; the
parking garages' ramps carrying a body between floors -- where each ramp's
opening begins, the clearance under the floor above is under a body's height,
so a garage's stairs are the way up; and every item the roadmap names as
open.

**What it needs from you.** Blender 4.2 or later and Godot 4.7, nothing
else; the package finds them (`setup --blender`, `--godot` when it cannot),
and `setup --venv` downloads three Python packages and what they need once,
into the factory's own folder. The first `make` takes about eight minutes on
a 2020-class desktop; the walk copy it offers is a Godot project you can
open and play.
