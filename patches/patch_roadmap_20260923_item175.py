"""Roadmap item 175: a hidden interactive state keeps its collider, so there
is collision where nothing is drawn.

Anchored on item 174's close, which must match exactly once.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = """be built on that inference.
"""

ITEM = """
*STATUS: OPEN 2026-09-23 -- MEASURED IN THE ENGINE. All 11 `breached` nodes
carry `visible = false` and a live collider; at 2 of 6 sampled walls a ray hits
`Breach` rather than `Wall`. The shipped default is still SOLID, which is what
the walker wants, but by coincidence rather than by construction.*

**175. A hidden interactive state keeps its collider, so there is collision
where nothing is drawn.** The walker's rule, 2026-09-23: "If I see collision, I
expect collision."

**WHAT SHIPS.** A breach wall ships both states, instanced side by side in the
building scene with the same `metadata/interactive_id`, each tagged with its
`metadata/interactive_state`, and the non-default one carrying `visible =
false`. Both GLBs carry collision: the intact one is `Wall_Panel` +
`Wall-colonly`, the breached one `Breach_brick_delco_1997` + `Breach-colonly`.

**VISIBILITY AND COLLISION ARE INDEPENDENT IN GODOT, and the scene sets only
visibility.** Measured with a physics probe on cold run 9070's package rather
than reasoned from the engine's documentation:

    every `_breached` node   visible=false, 1 collision body under it
    ext_0_N_open0_breached   a ray at its origin hits `Breach`
    int_-1_1_open1_breached  a ray at its origin hits `Breach`
    (the other four sampled hit `Wall` or the exterior segment)

Grepped the whole scene for a collision override -- `disabled`, `process_mode`,
`collision_layer`, `collision_mask` -- and found zero lines. Nothing turns the
hidden state's collider off.

**THE DEFAULT IS STILL SOLID, and that is worth stating before the defect.**
The two colliders are coincident, so their union is the intact wall and the
aperture is blocked. A body cannot walk through a breachable wall today. The
walker's preferred fallback already holds -- it simply holds by accident.

**WHAT IT COSTS.** A ray, a bullet or a surface query at those walls can hit
`Breach` where a player sees brick, so anything keying impact effects or
material off the collider gets the wrong surface. A navmesh baked from PHYSICS
geometry -- which Godot's own documentation recommends over visual meshes for
runtime cost -- bakes both states superimposed. And a future breach mechanic
implemented the obvious way, by flipping `visible` on the pair, would produce a
visible hole that is still solid, with no error anywhere.

**THE WALKER'S FRAMING RESOLVES ITEM 174, and is worth recording as the rule
rather than as a preference.** A breachable area is a door that has not been
added to a door frame yet. What ships should be VISUALLY TRUE, and collision
should match it:

    doorway, no door yet     you see a hole    -> passable   ships passable
    breach, no mechanic yet  you see a wall    -> solid      ships solid

Both are correct under "what you see is what you get". Item 174's apparent
inconsistency -- `interactive_state` labelling geometry on a breach and an
intention on a door -- is not an inconsistency in the geometry at all. The only
violation of the rule is the collider nobody can see.

**THE FIX.** Ship the non-default state hidden AND collision-disabled, so the
fallback is solid by construction. Nothing is removed: the breached geometry
stays in the package, and enabling a state later becomes one coherent
operation -- show it, enable its collider, disable the other's -- instead of
the visibility-only swap that silently leaves a solid hole.

**WHY THE TIMING IS RIGHT DESPITE THE UNCERTAINTY.** The walker: "we don't
know if we have breachable areas in the game yet... would rather have a
fallback to solid walls." That is an argument FOR doing this now rather than
waiting. The change costs nothing if breaching never ships -- the level is
solid either way -- and if it does ship, the trap above never gets built on.

**Owners.** Whichever pass writes the paired nodes into the building scene
(Lot's composer or Level Factory's presentation compose -- to be established
before patching, not guessed). The collider lives inside the instanced GLB, so
the override belongs on the instance in the `.tscn`, beside the `visible =
false` that is already there.

**What would falsify the framing:** a state whose collision is legitimately
wanted while hidden -- a trigger volume, or a breach that should stop bullets
but not sight. None of the 11 measured is that; all are wall panels. Worth a
look before the rule is written as unconditional.
"""


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: roadmap is LF; found CRLF")
    text = data.decode("utf-8")
    hits = text.count(ANCHOR)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    if not text.endswith(ANCHOR):
        raise SystemExit("REFUSED: anchor is not the end of the file")
    before = len(data)
    out = (text + ITEM).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"PIPELINE_ROADMAP.md: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), {out.count(10)} lines, LF")


if __name__ == "__main__":
    main()
