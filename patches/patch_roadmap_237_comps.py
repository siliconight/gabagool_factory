"""Roadmap 237: the walker's painted-brick comps (2026-10-11) and the first recipe they set. Appends
one paragraph to 237's body, which ends the roadmap; nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_237_comps.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL_237 = ("The guide's acceptance table (§17) is the look check; `tools/wear_probe.py` is the "
            "instrument that says whether a mask reached the package at all.\n")
ADD = """

**THE WALKER'S COMPS, 2026-10-11** (`docs/reference/PAINTED_BRICK_WEAR_COMPS.md`): two frames of another studio's storage-yard map, "white paint on bricks that fading through wear of time/erosion/rain" -- whitewash over red-brown brick, the paint following the courses and going first at the mortar joints, worn where weather reaches it (the corner, the top course under the coping, the splash band above an unpainted plinth, around the wall boxes) and intact across most of each field; rust streaks from each box's lower corners; a stencilled numeral under the same wear; a wire between the boxes. Read by layer, each one lands on a tool this factory has: the coat and the joint-first wear are a Pixelcoat pack (tier A); the exposure by module is `Wear` (B1); the lattice opening to patches is the worldskin shader (B2); the plinth is `base_course`'s family grown to a band or a ground-storey pack with a storey-tall tile under world projection (open); the streak is a floater under every wall box, placed by Patina and merged into the side's dressing (B, no new draw); the stencil is the poster path with the wall's wear in its alpha. **The first recipe:** one wall family -- a `brick_whitewash` pack, the plinth, the streak cover, the exposure value -- measured against the pack it replaces at the fixed stations, then the walker's eye."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE WALKER'S COMPS, 2026-10-11" not in text, "already applied"
    assert text.endswith(TAIL_237), ("the roadmap does not end with 237's body", text[-160:])
    text = text.rstrip("\n") + ADD + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 237's comps paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
