r"""The fixture gate compares markers to RIG ROOTS, not to bulbs.

    python patch_lux_colocation_anchor.py --check
    python patch_lux_colocation_anchor.py
    python patch_lux_colocation_anchor.py --revert

Run from the FACTORY ROOT (the directory holding `lux/`). Proof is
`lux/tools/colocation_selftest.gd`, which needs Godot and so cannot run here:

    godot --headless --path lux --import
    godot --headless --path lux -s res://tools/colocation_selftest.gd

THE IMPORT PASS IS NOT OPTIONAL. Lux's runtime scripts refer to each other by
`class_name`, and a `-s` script in a never-imported project has no global
script class cache, so `lux_validator.gd` will not compile and the output is a
wall of "Could not find type LuxRoot" that says nothing about this patch.

Roadmap item 71, which was filed as a Lux bug and is not one.

WHAT WAS WRONG, and it was the ruler. `check_fixture_colocation` measured
from each `LuxEmit_*` marker to the nearest `Light3D` and called anything past
0.10 m dark hardware -- then measured back from each spawned `Light3D` and
called the same distance a floating light. But a spawned light is not supposed
to sit on its marker. `lux_light_loader.gd` gives the `"fluorescent"` branch,
and only that branch:

    r.mount_height = -0.25
    # A hand's width BELOW the anchor: a lamp sitting on the ceiling
    # plane spends half its sphere grazing the ceiling -- streaks at
    # glancing angles and a scorched ring around the fixture (same
    # walk). Real tubes hang; ours do now too.

`LuxFixtureSpawner` puts the RIG ROOT on the marker exactly
(`rig.global_transform = mk.global_transform`); `LuxFluorescentRig` then hangs
its bulb at `Vector3(start, r.mount_height, 0.0)`, and markers are per-lamp so
count is 1 and start is 0 -- exactly (0, -0.25, 0). The check measured
bracket-to-bulb and reported a decision as a defect.

MEASURED on two cold runs, which is how it surfaced:

    cold_7001   markers=37 spawned=37   20 unmatched   worst 0.25 m
    cold_7002   markers=19 spawned=19   12 unmatched   worst 0.25 m

Two themes, two archetypes, two building counts, two Zoo kits -- and the worst
distance identical to the centimetre, because it IS a constant. The counts
differ because only fluorescents hang; pendant, streetlight and wall_pack all
set `mount_height = 0.0` and always passed. `markers == spawned` in both runs
because nothing was ever missing.

WHAT CHANGES. The contract the gate means to enforce is "a rig landed on every
marker, and no rig is floating unattached to hardware". That is a statement
about rig roots. Where a bulb sits inside its own rig is Lux's business, tuned
per type. So:

  * a light's ANCHOR is its rig root when it was spawned into the
    `LuxFixtureLights` container, and the light itself otherwise
  * dark-hardware measures marker -> nearest anchor
  * floating measures each spawned RIG ROOT -> nearest marker

WHY NOT A PER-TYPE TOLERANCE. It would work and it is worse: it needs
updating every time a rig's mount height is tuned, which is the coupling that
produced this. A mount height is art direction; the gate should not have an
opinion about it.

WHAT THIS PRESERVES, deliberately. Manifest-baked lights still satisfy a
marker -- they have no rig, so they anchor to themselves, which keeps "or Bake
Lights for manifest scenes" a true answer to the dark-hardware message. And a
rig genuinely adrift is still caught, which the selftest proves by moving one
5 m and requiring the finding.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

VALIDATOR = Path("lux/addons/lux/runtime/lux_validator.gd")
SIDECAR = ".pre_coloc_anchor"

# The file is TAB-indented. Every anchor below is copied from it verbatim.
OLD_DOC = '''## (b) Every lamp under a LuxFixtureLights container must sit within
## `tolerance` of a marker — a miss is a FLOATING LIGHT (spawner output
## drifted from the hardware). Manifest-baked lights (LuxLights) are not
## judged here: window/area lamps legitimately sit far from any hardware.
## Returns Finding entries; empty array when there are no markers at all.'''

NEW_DOC = '''## (b) Every spawned RIG under a LuxFixtureLights container must sit within
## `tolerance` of a marker — a miss is a FLOATING LIGHT (spawner output
## drifted from the hardware). Manifest-baked lights (LuxLights) are not
## judged here: window/area lamps legitimately sit far from any hardware.
## Returns Finding entries; empty array when there are no markers at all.
##
## BOTH HALVES MEASURE TO THE RIG ROOT, NOT TO THE BULB (roadmap 71). A
## spawned light is not supposed to sit on its marker: `lux_light_loader`
## gives the fluorescent branch `mount_height = -0.25` so real tubes hang
## below the ceiling plane instead of grazing it. The rig root is what lands
## on the marker. Measuring the bulb reported every fluorescent in the factory
## as floating light at exactly 0.25 m and blocked two cold runs.'''

OLD_DARK = '''	var lamps: Array = []
	_collect_positional_lights(scene_root, lamps)
	var dark := 0
	var worst_dark := 0.0
	for m in markers:
		var mp: Vector3 = (m as Node3D).global_position
		var best := 1e9
		for l in lamps:
			var d: float = (mp - (l as Node3D).global_position).length()
			if d < best:
				best = d
		if best > tolerance:
			dark += 1
			worst_dark = maxf(worst_dark, best)'''

NEW_DARK = '''	var anchors: Array = []
	_collect_light_anchors(scene_root, anchors)
	var dark := 0
	var worst_dark := 0.0
	for m in markers:
		var mp: Vector3 = (m as Node3D).global_position
		var best := 1e9
		for a in anchors:
			var d: float = (mp - (a as Node3D).global_position).length()
			if d < best:
				best = d
		if best > tolerance:
			dark += 1
			worst_dark = maxf(worst_dark, best)'''

OLD_FLOAT = '''	var spawned: Array = []
	_collect_spawned_lights(scene_root, spawned)
	var floating := 0
	var worst_float := 0.0
	for l in spawned:
		var lp: Vector3 = (l as Node3D).global_position'''

NEW_FLOAT = '''	var spawned: Array = []
	_collect_spawned_rigs(scene_root, spawned)
	var floating := 0
	var worst_float := 0.0
	for l in spawned:
		var lp: Vector3 = (l as Node3D).global_position'''

OLD_OK = '''		findings.append(Finding.new(Severity.OK,
			"Fixture co-location: %d marker(s) lit, %d spawned lamp(s) on hardware (tolerance %.2f m)."
			% [markers.size(), spawned.size(), tolerance]))'''

NEW_OK = '''		findings.append(Finding.new(Severity.OK,
			"Fixture co-location: %d marker(s) lit, %d spawned rig(s) on hardware (tolerance %.2f m)."
			% [markers.size(), spawned.size(), tolerance]))'''

OLD_HELPERS = '''static func _collect_spawned_lights(node: Node, out: Array) -> void:
	if node is Node and String(node.name) == LuxFixtureSpawner.CONTAINER:
		_collect_positional_lights(node, out)
		return
	for c in node.get_children():
		_collect_spawned_lights(c, out)'''

NEW_HELPERS = '''static func _collect_spawned_lights(node: Node, out: Array) -> void:
	if node is Node and String(node.name) == LuxFixtureSpawner.CONTAINER:
		_collect_positional_lights(node, out)
		return
	for c in node.get_children():
		_collect_spawned_lights(c, out)


## The LuxFixtureLights container, or null when nothing has been spawned.
static func _spawn_container(node: Node) -> Node:
	if node is Node and String(node.name) == LuxFixtureSpawner.CONTAINER:
		return node
	for c in node.get_children():
		var found: Node = _spawn_container(c)
		if found != null:
			return found
	return null


## Every spawned RIG ROOT -- the container's direct children, which is what
## `LuxFixtureSpawner.spawn` lands on each marker. NOT their Light3D
## descendants: a rig hangs its own bulbs wherever its type says (roadmap 71).
static func _collect_spawned_rigs(scene_root: Node, out: Array) -> void:
	var container: Node = _spawn_container(scene_root)
	if container == null:
		return
	for c in container.get_children():
		if c is Node3D:
			out.append(c)


## The point each light is ANCHORED to, which is not always the light itself.
##
## A spawned fixture light anchors to its RIG ROOT, because that is what the
## spawner placed on the marker and the bulb's offset inside the rig is
## deliberate. Any other positional light -- a manifest bake, a hand-placed
## lamp -- anchors to itself, which keeps "or Bake Lights for manifest scenes"
## a true answer to the dark-hardware finding.
static func _collect_light_anchors(scene_root: Node, out: Array) -> void:
	var container: Node = _spawn_container(scene_root)
	if container != null:
		for c in container.get_children():
			if c is Node3D:
				out.append(c)
	var all_lights: Array = []
	_collect_positional_lights(scene_root, all_lights)
	for l in all_lights:
		if container != null and container.is_ancestor_of(l as Node):
			continue
		out.append(l)'''

EDITS = {VALIDATOR: ((OLD_DOC, NEW_DOC), (OLD_DARK, NEW_DARK),
                     (OLD_FLOAT, NEW_FLOAT), (OLD_OK, NEW_OK),
                     (OLD_HELPERS, NEW_HELPERS))}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    return _CRLF if _CRLF in body else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace("\n", eol) if eol == _CRLF else text


def _find(body: str, anchor: str):
    for cand in (anchor, _as(anchor, _CRLF)):
        n = body.count(cand)
        if n:
            return cand, n
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    if "\t" not in out:
        print(f"REFUSING: {path.name} -- no tabs left; indentation was "
              f"rewritten and GDScript will not parse.")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")
    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  Now PROVE it -- this patch is GDScript and nothing here ran:")
        print("    godot --headless --path lux --import")
        print("    godot --headless --path lux -s res://tools/colocation_selftest.gd")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
