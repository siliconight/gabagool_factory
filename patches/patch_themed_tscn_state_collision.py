"""A hidden interactive state ships with its collision off.

THE WALKER'S RULE, 2026-09-23: "If I see collision, I expect collision." And,
on breachable areas: "we don't know if we have breachable areas in the game
yet... would rather have a fallback to solid walls."

MEASURED with a physics probe on cold run 9070's package, not reasoned from the
engine's documentation: all 11 `breached` nodes ship `visible = false` with a
LIVE collider, and a ray at two of six sampled walls hits `Breach` where a
player sees brick. Grepped the whole scene for a collision override --
`disabled`, `process_mode`, `collision_layer`, `collision_mask` -- and found
zero lines.

THE DEFAULT IS STILL SOLID, and that is worth saying before the fix. The two
colliders are coincident, so their union is the intact wall and nothing walks
through. The fallback the walker wants already holds -- by accident. What it
costs is a surface query returning the wrong collider, a physics-parsed navmesh
baking both states superimposed, and a future breach implemented the obvious
way (flip `visible`) producing a visible hole that is still solid, with no
error anywhere.

THE CONTRACT ALREADY SAID SO. `interactives._DEFAULTS` gives every kind a
`collision_per_state` -- `{"intact": True, "breached": False}` -- and this
file's own comment on the block below already says the game "swaps state by
flipping visibility (and toggling collision per interactive.collision_per_state)".
It referenced a field that `gameplay_interactive` dropped; Deli Counter 0.144.0
carries it, and this honours it.

THE SYNTAX WAS TESTED BEFORE IT WAS GENERATED. A collider lives inside the
instanced GLB scene, so the override is an editable-instance block. Both forms
were loaded headless in a scratch project first -- with and without `index=` --
and the body read `layer=0 mask=0` either way, so the index is omitted and
nodes match by name. Getting this wrong produces scenes that do not load, which
is not a thing to find out across a whole library.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "deli_counter" / \
    "themed_tscn.py"

# ---------------------------------------------------------------- anchor 1
A1 = '''def _glb_extent(glb_path):
'''

N1 = '''_COLBODY_CACHE = {}


def _glb_collision_bodies(glb_path):
    """The names Godot will give this GLB's collision bodies, cached.

    Godot strips the `-colonly` / `-convcolonly` suffix and makes a
    StaticBody3D of what is left, so `Breach-colonly` arrives as `Breach`.
    Verified by importing a real breach module headless and dumping the tree:
    `b (Node3D) -> Breach (StaticBody3D) -> CollisionShape3D`.

    The same suffixes `_glb_extent` skips are the ones this looks FOR -- one
    spelling of the convention, read from the same file.
    """
    if glb_path in _COLBODY_CACHE:
        return _COLBODY_CACHE[glb_path]
    out = []
    try:
        from pygltflib import GLTF2
        g = GLTF2().load(glb_path)
        for n in g.nodes or []:
            nm = n.name or ""
            low = nm.lower()
            for suffix in ("-convcolonly", "-colonly", "-convcol", "-col"):
                if low.endswith(suffix):
                    stem = nm[: -len(suffix)]
                    if stem and stem not in out:
                        out.append(stem)
                    break
    except Exception:
        out = []
    _COLBODY_CACHE[glb_path] = out
    return out


def _glb_extent(glb_path):
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''        for st, vref in state_refs.get(id(sl), []):
            out.append(f'[node name="{name}_{st}" parent="." '
                       f'instance=ExtResource("{ids[vref]}")]')
            out.append(f"transform = {xform}")
            out.append("visible = false")
            if inter.get("id"):
                out.append(f'metadata/interactive_id = "{inter["id"]}"')
            out.append(f'metadata/interactive_state = "{st}"')
            state_variants += 1
            out.append("")
'''

N2 = '''        for st, vref in state_refs.get(id(sl), []):
            out.append(f'[node name="{name}_{st}" parent="." '
                       f'instance=ExtResource("{ids[vref]}")]')
            out.append(f"transform = {xform}")
            out.append("visible = false")
            if inter.get("id"):
                out.append(f'metadata/interactive_id = "{inter["id"]}"')
            out.append(f'metadata/interactive_state = "{st}"')
            state_variants += 1
            out.append("")
            # COLLISION FOLLOWS VISIBILITY, because the walker's rule is "if I
            # see collision, I expect collision" and the two are independent in
            # Godot. A state that is hidden and solid is collision nobody can
            # see: measured on cold run 9070's package, a ray at two of six
            # sampled breach walls hit the hidden `Breach` body rather than the
            # brick in front of it, so a surface query reports the wrong
            # material. `collision_per_state` says which states are solid --
            # `interactives._DEFAULTS` has always defined it and Deli Counter
            # 0.144.0 carries it through.
            #
            # Silent when the contract says nothing: an absent
            # `collision_per_state`, or a state it does not mention, keeps
            # today's behaviour. This turns collision OFF only where the
            # contract states the state is not solid.
            cps = (inter.get("collision_per_state") or {})
            if cps.get(st) is False:
                bodies = _glb_collision_bodies(
                    os.path.join(library_dir, vref + ".glb"))
                if bodies:
                    inst = f"{name}_{st}"
                    out.append(f'[editable path="{inst}"]')
                    out.append("")
                    for body in bodies:
                        out.append(f'[node name="{body}" parent="{inst}"]')
                        out.append("collision_layer = 0")
                        out.append("collision_mask = 0")
                        out.append("")
                    state_collision_off += 1
'''

# ---------------------------------------------------------------- anchor 3
A3 = '''    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\\n".join(out) + "\\n")
    return out_path, {"themed": themed, "greybox_fallback": fell_back,
'''

N3 = '''    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\\n".join(out) + "\\n")
    return out_path, {"state_collision_off": state_collision_off,
                      "themed": themed, "greybox_fallback": fell_back,
'''

EDITS = ((A1, N1), (A2, N2), (A3, N3))


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
