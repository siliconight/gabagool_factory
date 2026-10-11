"""Roadmap 235: an FX marker contract -- effect anchors ship in the art layer; playing them is the
game's, or an optional layer.

Appends item 235 at the end of the roadmap, its status adjoining its heading. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_235_fx_markers.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
TAIL = ("(4) floaters baked into a normal map for detail too flat to model and for a distant LOD -- a "
        "channel Zoo does not ship, priced (texture memory per module) before it is built.\n")
ITEM = """
*STATUS: OPEN 2026-10-11 -- designed in conversation with the walker, not started. Where would "a building on fire" live? Not in Level Factory's content and not in a new factory tool: the effect anchors are geometry's business and ship in the art layer, as the light fixtures' `LuxEmit_*` markers do (roadmap 47), and playing an effect belongs to the game's effects system -- the studio's Calibria (`gabagool_studio_tools/calibria`) -- or, if the factory ever plays one itself, to an optional layer after light that a recipient can decline. Owner: Level Factory for the contract (its schema, the package's carriage, a gate), with Deli Counter, Lot and Zoo as producers; Calibria, outside the factory, for playback.*

**235. An FX marker contract: effect anchors ship in the art layer, and playing them is the game's.** The walker asked, 2026-10-11, whether a building on fire wants a Godot VFX tool or belongs in Level Factory. Three things in the repos answer it.

**THE LAYERS ALREADY DRAW THE LINE** (roadmap 47, CLOSED 2026-08-16; Level Factory 0.35.0-0.37.0). Graybox always runs; art adds Zoo, Pixelcoat and Patina; light is Lux's apply pass alone and requires art (`_LAYER_REQUIRES`); gameplay is advisory. An unlit package (`--unlit`, `art-unlit`) still ships the validated light fixtures and their markers -- in 47's words, a contract another lighting system can read -- and drops only the render solution. Effects take the same shape: the WHERE ships with the art, the HOW is declinable.

**THE MARKER CONTRACT TO MIRROR is `LuxEmit_*`.** Zoo exports one empty per lamp at the emitter point (`core.fixtures.marker_name`), its payload in glTF extras that Godot imports as node metadata (`lux_type`, `lux_anchor_id`, `lux_slot`, `lux_reacts_to_alarm`, `lux_drop`, `lux_reach`), and `LuxFixtureSpawner.spawn(level_root)` puts the matching rig at each one after the level loads. Its own division of labour: Zoo owns where, Lux owns how bright.

**THE CONSUMER EXISTS, outside the factory.** Calibria v0.6.0 (2026-07-10, three commits) is the studio's game-side effects library: recipes of particles, audio, decals, lights and camera shake that gameplay code plays through a network-safe API (server-authoritative, cosmetic events over unreliable RPC, spoofed and unknown events refused, dedicated servers spawning nothing), with budgets, pooling, near/far LOD, accessibility settings and persistent decals; 40 core checks, 22 integration checks and a three-process ENet smoke. It already reads Deli Counter's and Patina's surface manifests to route impacts, and registers its lights with Lux: the `lux_root` group, `register_lux_light`, `unregister_lux_light` and `get_quality_profile().max_dynamic_lights` all still exist at Lux 0.75.0 (read, not run), and a shipped package carries a LuxRoot (cold run 9241's `presentation/lux.applied.tscn`).

**THE CONTRACT, as proposed:**
- **Name and frame:** an `FxEmit_<kind>` empty (kind: fire, smoke, steam, sparks, embers, ...) at the effect's origin, its -Z in Godot's frame pointing out of the surface it comes from, as `CalibriaEmitter3D` reads its own.
- **Payload, in glTF extras:** `fx_kind`; `fx_anchor_id`, stable across rebuilds and unique across the site as `lux_anchor_id` is; `fx_mode` -- `ambient` plays for the level's life, `state` plays while an interactive state is active (`fx_interactive_id` and `fx_state` name it, the way a breach wall's two states ship side by side), `gameplay` is placed for the game to trigger and never plays by itself; `fx_scale`, the opening's or source's size in metres; `fx_seed`, for deterministic variation; `fx_light`, whether the effect wants light, so a consumer can ask Lux for it.
- **Layer:** art. Markers ship in every package that has art, lit or unlit; a graybox-only package carries none.
- **Producers, each owning WHERE in its own grammar:** Deli Counter (a burning building's windows, doors and roof openings; a kitchen hood's steam), Lot (site fires such as a barrel or a dumpster; steam from the manhole grates of roadmap 179), Zoo (hardware-bound points: a vent's steam, a broken sign's sparks).
- **Consumers:** the game's effects system through a spawner like `LuxFixtureSpawner`, and optional by construction: a package with markers and no consumer is a level without effects, never an error.
- **What the factory checks:** a gate in the shape of `lux_fixture_gate` -- every marker in the open rather than inside a wall, on its producer's surface, ids unique, counts inside a per-level budget -- and the walk's shot bot counting effect pixels as animated, Level Factory 0.178.3's mask.

**WHAT CALIBRIA NEEDS BEFORE IT CAN CONSUME IT**, read off v0.6.0 on 2026-10-11:
- an ambient mode: recipes have a fixed lifetime, `CalibriaEmitter3D` plays only when code calls it, and the storm pack keeps its rain falling by re-triggering every 12 s;
- a marker scan at level load that maps `fx_kind` to recipes;
- measurements on GL Compatibility: its project runs Godot's default Forward+, and Lux measured Compatibility without particle trails, sub-emitters or volumetric fog (`lux_rain.gd`);
- one owner for weather: its `storm_rain` duplicates Lux's rain, so both could run at once -- the proposed split keeps level-wide atmosphere with Lux and localized effects with Calibria;
- a price at the factory's fixed stations: smoke's cost is overdraw, which grows with screen area rather than count, and a fire's light is a live light under the eight-lights-per-mesh cap that should cast no shadow.

**First proof, when it is taken up:** one producer and one kind -- the cheapest is a Lot site fire, a burning barrel -- carried through art in a lit and an unlit package, read by a Calibria spawner in a scratch project, framed and priced. The walker's own example, a building on fire, is the second: Deli Counter's anchors at a building's openings, the same contract.
"""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**235. " not in text, "already applied"
    assert text.endswith(TAIL), ("the roadmap does not end where this patch read it", text[-160:])
    text = text + ITEM
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: item 235 opened; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
