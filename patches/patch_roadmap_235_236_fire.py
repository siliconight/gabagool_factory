"""Roadmap 235 and 236: the factory's scope for effects is emitters and hooks; the fire techniques are Calibria's.

235: one paragraph appended to its body -- what the hooks must allow, from two fire techniques the
walker brought on 2026-10-11 -- and its status's opening names the walker's scope. 236 opened at the
end: the techniques themselves, owned by Calibria (outside the factory), the factory's part being
235's hooks. Every anchor asserted once; nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_235_236_fire.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = "*STATUS: OPEN 2026-10-11 -- designed in conversation with the walker, not started. Where would"
STATUS_NEW = ("*STATUS: OPEN 2026-10-11 -- designed in conversation with the walker, not started; THE FACTORY'S "
              "SCOPE IS THE EMITTERS AND THE HOOKS, NOT THE EFFECTS (the walker: \"i dont want to scope creep, "
              "but ensure this factory has the fx emitters and hooks to allow for this type of stuff\"; "
              "the techniques are roadmap 236, Calibria's). Where would")
TAIL_235 = ("The walker's own example, a building on fire, is the second: Deli Counter's anchors at a "
            "building's openings, the same contract.\n")
ADD_235 = """
**WHAT THE HOOKS MUST ALLOW, measured against two fire techniques** (2026-10-11; the techniques are roadmap 236). A contract is good enough when a consumer the factory has never seen can do its job from the markers alone. Two the walker brought:
- **A flipbook fire or smoke** -- a few camera-facing sprites stepping through a pre-rendered 8 x 8 sheet -- needs the effect's origin, the direction out of its surface, its extent (an opening's width and height, `fx_scale`), a seed so neighbouring fires are out of phase (`fx_seed`), an ambient loop (`fx_mode` `ambient`), and a way to ask for light (`fx_light`).
- **A procedural fire texture** -- the PSX Doom fire, a palette-index automaton -- needs the same, plus the width of the line it burns along, which `fx_scale` carries; and it wants ONE texture shared by every fire on screen, which is the consumer's business but asks the contract for a kind the consumer can group by (`fx_kind`).
So the factory owes, and owes nothing more: the `FxEmit_<kind>` markers in the art layer with that payload; one well-known node group the markers join, so a consumer finds them in one call instead of walking a 26,000-node tree; the interactive-state binding (`fx_interactive_id`, `fx_state`), so a burning state can start and stop its effects; a marker Lux can read for the firelight, the way `LuxEmit_*` carries the fixtures' lamps; the gate; and the shot bot's animated mask. Everything that draws a flame stays outside the factory."""

TAIL_END = TAIL_235
ITEM_236 = """
*STATUS: OPEN 2026-10-11 -- filed from the walker's references, owned OUTSIDE the factory: Calibria (`gabagool_studio_tools/calibria`), as the walker agreed ("if you think this should live in Calibria, that is ok with me"). Not factory work: the factory's part is roadmap 235's emitters and hooks, and this item is here so a fire built for the factory's levels starts from what was already found.*

**236. Fire and smoke for a real-time game: flipbooks from offline simulations, and the Doom fire.** Two techniques, 2026-10-11. **The flipbook** (a short video the walker pasted, its frames showing Unreal's Niagara): run the fluid simulation offline in Blender, Houdini or Maya, where a voxel grid of density, temperature and velocity is far too slow and too large to run in a frame; render the first 64 frames facing the camera; pack them 8 x 8 into one PNG; and in the engine emit a handful of camera-facing sprites that step through the sheet -- no fluid dynamics at run time. In Godot that is `GPUParticles3D` with a billboard quad, `ParticleProcessMaterial`'s animation speed and the material's `particles_anim_h_frames` / `v_frames`; Calibria's `psx_explosion` already plays a 4 x 4 sheet that way, and GL Compatibility supports it (Lux measured what Compatibility lacks -- particle trails, sub-emitters, volumetric fog -- and a flipbook needs none of them). **The Doom fire** (`github.com/StanislavPetrovV/DOOM-Fire-Algorithm`, MIT, Python and Pygame; the PSX Doom technique): a 100 x 225 grid of palette indices into 37 colours from black through red, orange and yellow to near-white; the bottom row held at the hottest index; each frame every cell writes upward with a decay of 0 or 1 at even odds and a sideways drift of -2 to +1 columns. Cheap enough to run on the CPU into a small texture, or as a shader, and one texture can feed every fire on screen, so its per-frame cost does not grow with the number of fires.

**Where each fits.** The walker moved the look from retro to realism (Zoo 1.46.0's trial): a simulated flipbook is the near fire; the Doom fire's palette reads PSX, so it is the stylised, the far-LOD or the on-screen fire (a CRT in a den), or an emission mask retinted -- the walker's call when it is built.

**What Calibria would build:** (1) a flipbook baker, Blender headless as Zoo builds -- seeded, CC0, our own simulations, never the video's or anyone's sheets -- writing the 8 x 8 sheet and its alpha; (2) fire, smoke and ember recipes on the sheets, with Calibria's near/far LOD and budgets; (3) an ambient loop and a marker scan, which roadmap 235 already asks of it; (4) a price at the factory's fixed stations on GL Compatibility. **Costs to price:** a 1,024 x 1,024 sheet is 4 MB as raw RGBA and about 1 MB block-compressed, plus mipmaps; smoke's overdraw grows with screen area; a fire's light is a live light under the eight-lights-per-mesh cap."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "WHAT THE HOOKS MUST ALLOW" not in text and "\n**236. " not in text, "already applied"
    assert text.count(STATUS_OLD) == 1, ("235's status", text.count(STATUS_OLD))
    assert text.endswith(TAIL_END), ("the roadmap does not end with 235's body", text[-160:])
    text = text.replace(STATUS_OLD, STATUS_NEW)
    # a blank line before 235's new paragraph, one before 236's status, and the file's last newline
    text = text + "\n" + ADD_235.lstrip("\n") + "\n" + ITEM_236 + "\n"
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 235's scope and hooks paragraph, 236 opened; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
