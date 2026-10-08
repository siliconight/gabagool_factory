"""Roadmap 213: decided -- the walker left live or baked to us and asked for a
brighter stage; the call is live, and Level Factory 0.159.0's bake-aware
census measures the 8-lights-a-mesh cap clear with the four stage lamps live.

    python patch_roadmap_213_decided.py

Anchored on PIPELINE_ROADMAP.md as commit 2bcbb3c's tree left it (1,319,059
bytes, LF, as read 2026-10-08): 213's status line by its unique prefix,
directly above its heading; 213's second and third NEXT bullets; the "Not
measured" bullet of its price, which is followed by "The look". Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S213_PREFIX = "*STATUS: OPEN 2026-10-08 -- priced, the walker's call: Level Factory's light bake bakes"
S213_NEW = (
    "*STATUS: OPEN 2026-10-08 -- decided, not built. The walker: \"Stage can be brighter, im ok with live or "
    "baked, whatever you think is the best\". The call is LIVE, and brighter. Live costs no draw calls and 0.11 "
    "to 0.17 ms at a view facing a stage, on frames of about 3 ms (`docs/findings/club_stage_live_price/`). With "
    "the four stage lamps live, no mesh is over the 8-lights-a-mesh cap: Level Factory 0.159.0's paired census "
    "reads 0 over, worst 6, the same as baked (`docs/findings/light_census_pairs/`). Next: the bake keeps a "
    "cycling stage rig live, Lux lights the stage brighter, and a cold run on club_block_014 shows both.*\n")

OLD_NEXT = (
    "- The walker chooses: live, or baked and frozen with the choice recorded. And, separately, whether the stage "
    "should read brighter than Lux's solve: at that energy it does not read lit either way.\n"
    "- If live: the bake keeps a rig with `cycle_period_s > 0` live, as it keeps a failing one, with a test that "
    "fails while it bakes one. The stage then loses whatever part of its baked wash is the stage lamps'.\n")
NEW_NEXT = (
    "- The walker chooses: live, or baked and frozen with the choice recorded. And, separately, whether the stage "
    "should read brighter than Lux's solve: at that energy it does not read lit either way. *Answered "
    "2026-10-08: \"Stage can be brighter, im ok with live or baked, whatever you think is the best\". The call: "
    "live, because the colour cycle is the show and its price is small and local; and brighter.*\n"
    "- If live: the bake keeps a rig with `cycle_period_s > 0` live, as it keeps a failing one, with a test that "
    "fails while it bakes one. The stage then loses whatever part of its baked wash is the stage lamps'.\n"
    "  - **The trap in that sentence.** The cycle is the rig NODE's -- `cycle_period_s` and `colors` are "
    "`LuxStageLightRig` exports -- while `mark_steady_rigs` reads the rig RESOURCE, which carries only "
    "`bake_mode` and the lamp numbers. So the bake has to map each resource to the nodes that use it, or Lux "
    "has to flag the resource when it builds a cycling rig.\n"
    "- Brighter: Lux's stage solve (`lux_light_loader.gd`, the `stage_light` branch), judged by frames of the "
    "live stage. Pairing reads range, not energy, so a brighter stage at the same range keeps the census's "
    "counts.\n")

OLD_CAP = (
    "- **Not measured: the 8-lights-a-mesh cap.** The harness's light census counts every positional light by "
    "its reach, baked or live. So it reads the same in all four runs (33 of 3,954 meshes over 8), and cannot say "
    "whether the live lamps put a stage mesh over the lights the renderer pairs with it.\n")
NEW_CAP = OLD_CAP + (
    "  - *Measured since* (Level Factory 0.159.0, `docs/findings/light_census_pairs/`). Godot 4.7's culler "
    "never pairs a light masked off a mesh's layers, nor a BAKE_STATIC light with a lightmapped mesh "
    "(`renderer_scene_cull.cpp`, `_scene_cull`), and the census now counts that too, as `paired`. On this "
    "package: by reach 33 of 3,954 over 8, worst 31; paired 0 over, worst 6. With the stage rigs live, paired "
    "gains 420 light-mesh pairs and is still 0 over, worst 6; the reach count does not move.\n")


def main():
    data = RM.read_bytes()
    assert len(data) == 1319059, "PIPELINE_ROADMAP.md is %d bytes, read at 1,319,059" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, what in ((OLD_NEXT, "213's NEXT"), (OLD_CAP, "the price's cap bullet")):
        assert text.count(old) == 1, "%s found %d times" % (what, text.count(old))
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(S213_PREFIX)]
    assert len(hits) == 1, "213's status found %d times" % len(hits)
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith("**213. "), "213's status is not above its heading"
    lines[i] = S213_NEW.rstrip("\n")
    text = "\n".join(lines).replace(OLD_NEXT, NEW_NEXT).replace(OLD_CAP, NEW_CAP)
    RM.write_bytes(text.encode("utf-8"))
    print("213 decided; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
