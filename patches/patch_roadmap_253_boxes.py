"""Roadmap 253: the walker walked the asset flags and asked for boxes, now shipped -- its status, the earlier kept.

Anchored on item 253's whole status block, which must stand once and directly above the item's heading; nothing is
written on a miss. Then `python tools/roadmap_status.py --write` and `--check`.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
HEADING = "\n**253. "
OLD = '*STATUS: NARROWED 2026-10-19 -- BUILT, and in every walk copy since cold run 9323; what closes it is the walker\'s walk. `tools/walk_asset_flags.gd` (root f7e7a76; debug builds only, like F3 and the work light): G marks what the crosshair rests on as looking good, P as needing love, and a banner says what was flagged. It picks BY RENDER first -- collision here is Deli Counter\'s greybox and the asset the eye sees is the Zoo module over it, so the F3 ray names `slab_col_1` and never the tile -- names the asset by its nearest instanced ancestor\'s file (module and building) with the physics hit beside it, and appends a record and a 640-wide frame beside the copy. `tools/asset_flags.py` gathers every copy\'s flags into one ledger per asset, needs-love first, frames copied beside it so it outlives the walk copy (`docs/findings/asset_flags_253/`). Proven headless (`tools/walk_asset_flags_selftest.gd`, 14 checks) and by the ledger\'s selftest. Known gaps: a MultiMesh (Lot\'s dressing) falls to the physics hit; merged Empties carry their merged name. Earlier status kept: OPEN 2026-10-14 -- THE WALKER\'S ASK: "I want a way to flag assets that look good and assets that need more polish/love". Proposed: two keys in every walk copy recording the asset under the crosshair, the verdict and a frame into a ledger the factory reads. Not started; the shape is the walker\'s to confirm.*\n'
NEW = '*STATUS: NARROWED 2026-10-19 -- THE WALKER WALKED IT, AND ASKED FOR BOXES, NOW SHIPPED. Their first walk with the keys (cold run 9334\'s copy, county_hospital_001 on a rainy night) put five flags on one parked car, all recorded with their frames; pressed G and meant P (the walker: "oh yes i meant to use the needs work"; the records carry `verdict_pressed`), so the ledger\'s first entry is the car as needs love (`docs/findings/asset_flags_253/LEDGER.md`). Nothing on screen had stayed to say the presses landed -- the banner drew under the F3 overlay\'s panel -- and the walker asked for "a red line around an item that is flagged", "green for looks good, red for needs more work", "and it persists for that session". `patches/patch_walk_asset_flag_outlines.py`: each flagged thing is boxed in its verdict\'s colour until the walk quits, round the model it was instanced from or else the node picked, and the banner hangs from the foot of the screen; the selftest holds 43 checks (24 fail on the unpatched handler, and three handlers each missing one fix fail 1, 9 and 6), and `outline_frames/` shows six presses from where the walker stood. Found doing it and fixed: a pick could take a mesh 405 m off, Lux\'s horizon glow, past the 60 m its comment promised. Refuted and kept in the handler: boxing the ancestor "unless it is a scene at the package\'s root" boxed the whole 760 m site, which is `presentation/lux.applied.tscn`. What is left: a walk with the boxes whose ledger names each flag rightly; and a pick in the level\'s own scene (a sidewalk, a kerb, a road) is boxed by itself but still RECORDED under the level\'s file, so the ledger lumps such flags under `lux.applied`. Earlier status kept: NARROWED 2026-10-19 -- BUILT, and in every walk copy since cold run 9323; what closes it is the walker\'s walk. `tools/walk_asset_flags.gd` (root f7e7a76; debug builds only, like F3 and the work light): G marks what the crosshair rests on as looking good, P as needing love, and a banner says what was flagged. It picks BY RENDER first -- collision here is Deli Counter\'s greybox and the asset the eye sees is the Zoo module over it, so the F3 ray names `slab_col_1` and never the tile -- names the asset by its nearest instanced ancestor\'s file (module and building) with the physics hit beside it, and appends a record and a 640-wide frame beside the copy. `tools/asset_flags.py` gathers every copy\'s flags into one ledger per asset, needs-love first, frames copied beside it so it outlives the walk copy (`docs/findings/asset_flags_253/`). Proven headless (`tools/walk_asset_flags_selftest.gd`, 14 checks) and by the ledger\'s selftest. Known gaps: a MultiMesh (Lot\'s dressing) falls to the physics hit; merged Empties carry their merged name. Earlier status kept: OPEN 2026-10-14 -- THE WALKER\'S ASK: "I want a way to flag assets that look good and assets that need more polish/love". Proposed: two keys in every walk copy recording the asset under the crosshair, the verdict and a frame into a ledger the factory reads. Not started; the shape is the walker\'s to confirm.*\n'


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = data.decode("utf-8")
    if text.count(NEW + HEADING) == 1:
        print("already applied")
        return 0
    if text.count(OLD) != 1 or text.count(OLD + HEADING) != 1:
        raise SystemExit("REFUSED: item 253's status block is not there once, above its heading; nothing written")
    out = text.replace(OLD, NEW).encode("utf-8")
    ROADMAP.write_bytes(out)
    print("item 253's status replaced, the earlier kept: %d -> %d bytes" % (len(data), len(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
