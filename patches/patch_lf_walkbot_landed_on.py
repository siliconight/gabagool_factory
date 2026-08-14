r"""The walk bot names what it landed on, and whether anything is overhead.

    python patch_lf_walkbot_landed_on.py --check
    python patch_lf_walkbot_landed_on.py
    python patch_lf_walkbot_landed_on.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

Roadmap addendum item E, "instruments that cannot distinguish three states":

    `walkbot.json` reports `climb: true, top_exit: true` for both a fixed
    ladder and a ladder into open sky. Missing geometry and extra geometry are
    opposite failure modes; one scalar cannot carry both. Either add a presence
    term, or make the bot report what it *landed on* by name. This misled the
    diagnosis twice in one session.

It does both, because they are two questions:

    landed_on      the collider the bot's feet came to rest on, by NAME
    overhead       the collider above the exit point, by NAME, "" for sky

`top_exit` is `bot.is_on_floor() and rel.y > climb_h - 1.2`. A ladder through a
correctly-holed roof exits onto the roof; a ladder with no roof at all exits
onto the top-storey floor. Both are on a floor at climb height, so both scored
`top_exit: true` and the report could not tell a fixed level from a level
missing a surface.

WHY THIS IS URGENT ON 2026-08-12. The archetype library was rebuilt today and
every roof slot now carries `fit.voids`, so every ladder in the library is
about to be re-judged -- by an instrument that cannot distinguish "the roof now
has its hole" from "there is no roof". The fix and the ambiguity would land in
the same run.

THE FILE ALREADY KNEW HOW. `_diagnose_stall` names the collider in the way --
`d["blocker"] = String((hit["collider"] as Node).name)` -- and that name is
what closed the ladder investigation. The FAILURE path named things and the
SUCCESS path named nothing. Both new probes are the same idiom, cast the same
way, excluding the bot the same way.

Explicitly typed throughout: `gdscript/warnings/inference_on_variant` is an
error under engine defaults, which is why the export and now the preview both
set it to warn. A new `var x := <Variant>` here would be a load failure on a
consumer's default config.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

BOT = Path("level_factory/assets/godot/walk_bot.gd")
SIDECAR = ".pre_landedon"


OLD = '''	rel = linv * bot.global_position
	v["top_exit"] = bot.is_on_floor() and rel.y > climb_h - 1.2
	v["final_rel_y"] = snappedf(rel.y, 0.01)'''

NEW = '''	rel = linv * bot.global_position
	v["top_exit"] = bot.is_on_floor() and rel.y > climb_h - 1.2
	v["final_rel_y"] = snappedf(rel.y, 0.01)
	# WHAT it exited onto, and whether anything is above -- not just that it
	# stood somewhere. `top_exit` alone reads true for a ladder through a
	# correctly-holed roof AND for a ladder with no roof at all, because both
	# end on a floor at climb height. Roadmap addendum item E: "missing
	# geometry and extra geometry are opposite failure modes; one scalar
	# cannot carry both." `_diagnose_stall` has always named its blocker; the
	# success path named nothing, and that asymmetry misled two diagnoses.
	v["landed_on"] = _name_below(bot)
	v["overhead"] = _name_above(bot)'''


OLD_FUNC = '''func _diagnose_stall(bot: CharacterBody3D, l: Area3D, lt: Transform3D,
		linv: Transform3D) -> Dictionary:'''

NEW_FUNC = '''func _name_below(bot: CharacterBody3D) -> String:
	## The collider the bot is standing on, by node name; "" for nothing.
	## Same idiom as `_diagnose_stall`'s blocker ray, pointed the other way.
	var space: PhysicsDirectSpaceState3D = bot.get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(
		bot.global_position + Vector3.UP * 0.2,
		bot.global_position + Vector3.DOWN * 1.5)
	q.exclude = [bot.get_rid()]
	var hit: Dictionary = space.intersect_ray(q)
	if hit.is_empty():
		return ""
	return String((hit["collider"] as Node).name)


func _name_above(bot: CharacterBody3D) -> String:
	## The collider above the exit point, by node name; "" is open sky.
	## THE PRESENCE TERM. A roof with its ladder void cut still has roof either
	## side of the hole, so stepping off the ladder and looking up finds one.
	## A building with no roof at all finds nothing. That is the difference
	## `top_exit` could not carry, and `void %` could not either -- it reads
	## 52.66% for a correctly-open roof and 52.66% for no roof.
	var space: PhysicsDirectSpaceState3D = bot.get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(
		bot.global_position + Vector3.UP * 0.2,
		bot.global_position + Vector3.UP * 6.0)
	q.exclude = [bot.get_rid()]
	var hit: Dictionary = space.intersect_ray(q)
	if hit.is_empty():
		return ""
	return String((hit["collider"] as Node).name)


func _diagnose_stall(bot: CharacterBody3D, l: Area3D, lt: Transform3D,
		linv: Transform3D) -> Dictionary:'''


OLD_DOC = '''##   top_exit      stepping away at the top lands on standable upper floor'''

NEW_DOC = '''##   top_exit      stepping away at the top lands on standable upper floor
##   landed_on     the collider it came to rest on, by name ("" = nothing)
##   overhead      the collider above the exit, by name ("" = open sky)'''


EDITS = {BOT: ((OLD_DOC, NEW_DOC), (OLD_FUNC, NEW_FUNC), (OLD, NEW))}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


#: GDScript this patch introduces that MUST stay explicitly typed. Engine
#: defaults escalate inference-on-Variant to a load-killing error; the export
#: and the preview both set it to warn, and a consumer's project may not.
_MUST_TYPE = ("var space: PhysicsDirectSpaceState3D",
              "var hit: Dictionary")


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
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    for frag in _MUST_TYPE:
        if out.count(frag) < 2:
            print(f"REFUSING: {path.name} -- expected both new probes to "
                  f"declare {frag!r}; inference from Variant is a load-killing "
                  f"error under engine defaults.")
            return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        print(f"  both probes explicitly typed")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    print(f"  NOTE: the preview copies this file in; re-run `walk` to pick it up")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
