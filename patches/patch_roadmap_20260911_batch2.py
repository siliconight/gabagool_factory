"""Roadmap batch 2, 2026-09-11: narrow 111 and 112, close 113 and 95.

Same mechanics as patch_roadmap_20260911_batch.py: replace only the
`*STATUS:` block above each heading, walking backward from the heading and
normalising the blank run to one. Item 121's entry is appended by a later
edit once its A/B lands.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

STATUS = {
    111: """*STATUS: NARROWED 2026-09-11 -- EIGHT OF FOURTEEN NOW, MEASURED RATHER THAN
REMEMBERED. A census of every workspace on disk, counting a preset as exercised
only where a `lot_assemble` job exists for a brief that resolves to it: bank
(four missions), casino_tower, corner_deli, hospital, office, police_station,
rowhome, warehouse -- eight of the fourteen non-facade presets. Cold run 9005
added `hospital`, the largest in the registry, at zero interventions. NEVER
BUILT: auto_shop, compound, gas_station, parking_garage, pawn_shop,
suburban_safehouse -- six, and two of them (pawn_shop, suburban_safehouse) are
the presets roadmap 130 found with NO combat room that could be fought in, so
first contact there is likely to find more than a KeyError. The two defects
this item opened on are closed (118 for the alias; the KeyError with it).
WHAT REMAINS is the six, one cold run each.*""",

    112: """*STATUS: NARROWED 2026-09-11 -- THE AXIS IS EIGHT WIDE OF TWELVE, NOT TWO OF
NINE, AND THE FOUR THAT CANNOT BE BUILT ARE NAMED. Pixelcoat now ships twelve
profiles (delco_1997 and two rockay variants since this was filed). Measured
through `packages.tools.themes.resolve` against the shipped Zoo genome, species
resolving a style out of 56: delco_1997 56, rockay 56, rockay_civic 56,
rockay_retail 56, rockay_service 56, center_city 54, industrial_flats 54,
delco 42 -- and bank 0, casino 0, stadium 0, street 0. So eight themes build
with full or near-full species coverage and four render flat colour across the
whole kit. Zoo 0.57.0's `theme_style` (decade qualifier, then base name) is
what moved delco_1997 from 0 to 56 without a per-species pass. WHAT REMAINS:
the four at zero are content gaps in Zoo -- bank, casino, stadium and street
need species styles or a fallback rule that names them -- and delco's 14
missing species are the 1990s-only set roadmap 112 first counted.*""",

    113: """*STATUS: CLOSED 2026-09-11 -- ALL THREE RE-ADMITTED BY FIXING THE GENERATOR,
AND THE QUARANTINE IS EMPTY AND KEPT. `deli_counter/build.py` records it beside
the empty dict: `night_pawn` and `cbp_town_finale_midbalanced_schemafixed`
came out with DC 0.105.0 (a partition stood where the stair goes, item 114,
14 of 129 shells), and `primos_pizza` -- the one this status still counted --
came out with DC 0.108.0, refused at spec time by `layout_lint` L19 measuring
to the wall's inner face (item 115). `_QUARANTINE = {}` on 2026-09-11, and
`check.py`'s stair regression sweep passes in the pre-commit hook today. The
count on this item is 0, and the mechanism -- quarantine with the reason
written beside the id, re-admit only on a passing `nav_gate` -- stays so the
next failing shell has somewhere honest to go.*""",

    95: """*STATUS: CLOSED 2026-09-11 -- THE ENVELOPE IS STAMPED FROM THE FILES IT
MERGES. Lot 0.55.0: `merge_lights` collects each building manifest's
`light_manifest_version`, stamps the HIGHEST on the site envelope -- because
that is the contract the anchors actually need a reader to understand -- and
records the full set as `light_manifest_versions_merged` so a mix is visible
rather than averaged away. A file with no version field is 1.0.0 by
definition; a site with no building manifests is Lot's streetlights alone and
stays 1.0.0. Reproduced first on cold run 9005's build of 2026-09-10 --
building envelope 1.1.0, site envelope 1.0.0, `drop` on the ceiling anchors --
then fixed. The test that pinned `== "1.0.0"` was the same bare literal as the
defect, one file over, and is replaced by an assertion on the merged set.*""",
}


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    lines = raw.decode("utf-8").split("\n")
    for num, block in STATUS.items():
        heading = re.compile(r"^\*\*%d\. " % num)
        hits = [i for i, l in enumerate(lines) if heading.match(l)]
        if len(hits) != 1:
            print(f"item {num}: heading matched {len(hits)} times", file=sys.stderr)
            return 1
        h = hits[0]
        if h < 3 or lines[h - 1].strip() != "":
            print(f"item {num}: no blank line above heading", file=sys.stderr)
            return 1
        e = h - 1
        while e > 0 and lines[e].strip() == "":
            e -= 1
        blanks = h - 1 - e
        if not lines[e].rstrip().endswith("*"):
            print(f"item {num}: line above the blank does not close a status "
                  f"block: {lines[e][:60]!r}", file=sys.stderr)
            return 1
        s = None
        for i in range(e, max(-1, e - 40), -1):
            if lines[i].startswith("*STATUS:"):
                s = i
                break
        if s is None:
            print(f"item {num}: no *STATUS: within 40 lines", file=sys.stderr)
            return 1
        lines[s:e + 1 + blanks] = block.split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); {len(STATUS)} statuses replaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
