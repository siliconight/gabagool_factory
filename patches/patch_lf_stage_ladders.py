"""The Dispatch staging carries a building's LADDERS, so an off-mesh link ships.

THE THIRD LINK IN A CHAIN THIS HAS NOW BEEN WRONG ABOUT TWICE. The capability
is "an AI can path up a ladder the player climbs", and it has been claimed and
falsified twice by the falsifier its own brief wrote down -- a package whose
buildings carry ladders and whose `navigation_hints.json` `links[]` is empty:

  * Dispatch 0.5.0 taught the DELI COUNTER importer to read ladders. Cold run
    9075 shipped a site mission, which runs the LOT importer, and read LINKS 0.
  * Lot 0.76.0 concatenated its buildings' ladders into the site and Dispatch
    0.5.1 taught the Lot importer to read them. Cold run 9076 read LINKS 0
    again.

WHY 9076 STILL READ ZERO, traced rather than guessed. The chain is four hops
and only the middle two had been fixed:

    deli_counter/build/arena_a03.gameplay.json      ladders: 1   OK
    lot .../seed_9177/1/out/site.site.gameplay.json ladders: 1   OK (Lot 0.76.0)
    .../dispatch_inputs/lot/lot.gameplay.json       no `ladders` KEY AT ALL
    navigation_hints.json                           links: 0

`stage_dispatch_inputs` does not copy Lot's file; it PROJECTS it into a literal
dict whose keys are `schema, license, up_axis, anchors, props, interactives`.
Anything else Lot emits is dropped silently, because a whitelist that drops is
indistinguishable from an upstream that never sent. Both the deli_counter and
lot sides do it, so a single-building mission was equally affected.

NOT `derive_nav`'s `links`, and this was checked before patching. That function
also emits a key called `links`, and it would have been the obvious place to
put these. It is a different quantity: `[[node_id, node_id], ...]` edges
chaining the coarse anchor graph so reachability passes. An off-mesh link is a
`nav_link` object with start and end positions. Two things called links, and
merging them because the names match is the mistake `WALKOFF_CLEAR`'s own note
warns about in the other repo.

VERBATIM, like `interactives` beside it. Deli Counter computes the link and Lot
has already moved every position into site space, refusing rather than carrying
a field it does not recognise. Nothing here re-derives geometry; re-projecting
it is how a nav link and a route node end up disagreeing about where the same
ladder is.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "packages" / "staging" / "dispatch_inputs.py"

# ---------------------------------------------------------------- anchor 1
A1 = '''        # Verbatim pass-through (see the lot side below); on a mission with
        # a Lot site the site-level concatenation wins in Dispatch.
        "interactives": list(dc_gp.get("interactives", []) or []),
    }, indent=2), encoding="utf-8")
'''

N1 = '''        # Verbatim pass-through (see the lot side below); on a mission with
        # a Lot site the site-level concatenation wins in Dispatch.
        "interactives": list(dc_gp.get("interactives", []) or []),
        # LADDERS, for the same reason and with the same rule: verbatim. Deli
        # Counter files an off-mesh `nav_link` on each one, and Dispatch's
        # importer turns it into a link the AI can path over. This projection
        # is a whitelist, so a key it does not name is dropped in a way that
        # looks exactly like an upstream that never sent it -- which is why
        # the capability was claimed and falsified twice (roadmap 172).
        "ladders": list(dc_gp.get("ladders", []) or []),
    }, indent=2), encoding="utf-8")
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''        "interactives": list(lot_gp.get("interactives", []) or []),
    }, indent=2), encoding="utf-8")
'''

N2 = '''        "interactives": list(lot_gp.get("interactives", []) or []),
        # LADDERS, concatenated by Lot from every building with every position
        # already moved into site space (Lot 0.76.0's `_ladder_to_site`, which
        # refuses on a numeric triple it does not recognise rather than
        # shipping one in the building's frame). Verbatim for the same reason
        # as `interactives`: re-projecting geometry here is how a nav link and
        # a route node end up disagreeing about where one ladder is.
        #
        # THIS LINE IS THE ONE THAT WAS MISSING. Cold run 9076 measured
        # ladders 1 in Lot's `site.site.gameplay.json` and no `ladders` key at
        # all in the file this writes, so Dispatch's Lot importer -- which had
        # been taught to read them in 0.5.1 -- found nothing and the package
        # shipped `links: 0` for the second run running.
        "ladders": list(lot_gp.get("ladders", []) or []),
    }, indent=2), encoding="utf-8")
'''

EDITS = ((A1, N1), (A2, N2))


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
