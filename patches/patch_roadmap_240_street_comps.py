"""Roadmap 240: the walker's Philly street comps (2026-10-11) -- what a street is made of that the
factory does not make. Appends the item after 239 (asserting the roadmap still ends with 239's
body); nothing written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_240_street_comps.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL_239 = ("`realtime_ab.sh` runs one evaluation at 1x beside 4x, with 0.25.0's enemy and 0.26.0's, to "
            "say how far apart they read.\n")
STATUS_240 = (
    "*STATUS: OPEN 2026-10-11 -- filed, not started. Three comps read and mapped by owner "
    "(`docs/reference/PHILLY_STREET_COMPS.md`); the first three builds named: the utility pole line "
    "and its overhead wires (absent), the rowhouse front (stoop, railings, a dish on the front), the "
    "silver roofs. Level creation, after Zoo 1.102.0's roof profiles land.*")
ITEM_240 = """

**240. A Philly street is made of things the factory does not make yet.** The walker, 2026-10-11, with three photographs: "some really good comps that you need to learn from" -- a corner at a wide avenue under overcast sky, a neighbourhood seen from a tall building at golden hour, a rowhouse street on a block-party day. Read by layer and mapped by owner in `docs/reference/PHILLY_STREET_COMPS.md` (photographs not stored). What the factory has: streetlights, signals, sign posts and stop signs each on its own pole, hydrants, litter and bags, chain-link fences, folding chairs, dishes on Empty roofs. What it does not:

- **The pole line.** Wooden utility poles carrying the cobra-head lamps, the street-name signs and the side-street signals, and overhead wires along the block and across the street -- the strongest single line in two of the three frames, and no species, placement or wire exists. Zoo (a `utility_pole`, wire spans as generated thin meshes) and Lot (a pole line along the kerb, spans across at junctions, lamps and signs mounted on it where it stands). Priced as any look: spans merged one mesh per street per material, casting no shadow.
- **The rowhouse front.** Stoops of three or four steps with iron railings to a raised first floor, satellite dishes on the fronts at the second floor, parged fronts beside brick. The rowhome Empty stands its door at grade and its dish on the roof. Deli Counter (a raised floor and a stoop volume; a rise is gameplay geometry, so the contract's step limits decide its form), Zoo (the stoop and railing), Patina (facade anchors for dishes).
- **The roofscape.** Flat roofs, most silver-coated and some black tar, rear ells stepping down at the back. The rowhome roof is `concrete`, though its own comment says silver; Pixelcoat (a silver coating pack, a tar one) and Deli Counter (the ell). Players see roofs now (roadmap 181).
- **Then:** a mixed-use corridor (a shop at grade, homes above, a colour and a sign band per front); grit placed by cause (litter at kerb lines, fence bases and lot edges; patched asphalt as roadmap 237's tier A); vacant lots behind corrugated metal; a block party as a street state; brick towers, stacks and a ballfield in the backdrop recipes; an overcast sky.

**WHAT WOULD CLOSE IT.** Each build lands as a generator rule proven in a cold run with frames beside the comps, and the walker's eye on them; never a placement in a workspace."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**240. " not in text, "already applied"
    assert text.endswith(TAIL_239), ("the roadmap does not end with 239's body", text[-160:])
    text = text.rstrip("\n") + "\n\n" + STATUS_240 + ITEM_240 + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 240 appended after 239; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
