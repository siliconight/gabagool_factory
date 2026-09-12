"""Roadmap batch 34, 2026-09-12: the 179 (item 44 REPLACE, old kept) and the
style half (item 150 REPLACE, old kept). Asserts every anchor once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 (evening) -- STEP 3 IN A COLD PACKAGE: cold
run 9010's bank carries its 10 m teller counter as a counter run and its
auto shop a turned 5 m parts rack, a workbench counter and a desk, zero
fallbacks across the lot (item 17).""",
"""*STATUS: NARROWED 2026-09-12 (night) -- THE 179 WORKED DOWN TO 52, AND
THOSE ARE REGIONS, NOT FURNITURE: 728 OF 780 HINTED PLACEMENTS PLAN AS
THEIR SPECIES. Zoo 0.64.0, from the 179's own shapes: tables and seating
run in bays (a 4 x 2 count table, a 5 x 2 x 0.6 waiting bench as a row of
joined seats); ranges opened by measurement -- racks to 20 x 1.4 x 4.5,
safes to 1.2 x 1.0 x 1.5, tanks to 3 x 3 x 4.5, desks 1.2 deep, counters
2.0 deep; and an ALTERNATE of the same family before the box -- `desk` ->
`counter` -- because 25 "desks" (front, check-in, manager, boss) stand
1.1-1.2 m tall and are counters by any name, each reported in
`species_alternates`. Two exact-fit refutations kept: the 3.0 m tank came
out 2.925 (a 14-gon's flat width) and builds with sixteen segments under
`fit_exact`. Probe of seven shapes through Blender, 7 of 7 pass. What
falls back now (52): `cubicles_w/e` 8 x 6 blocks (28), `gaming_tables`
12 x 6 floors (10), a 7 x 3 x 1.6 counting-table block, a 10 x 7 stadium
seating arc -- a region wearing a furniture name, which is a spec
authoring question (one block standing for a room's worth of desks) and
not a species' failure to be a desk. The pump keyword added 60 hinted
placements (720 -> 780). Not yet in a package: cold run 9011 (a gas
station) is running. Previously: STEP 3 IN A COLD PACKAGE: cold
run 9010's bank carries its 10 m teller counter as a counter run and its
auto shop a turned 5 m parts rack, a workbench counter and a desk, zero
fallbacks across the lot (item 17)."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (later) -- THE PROP HALF (ZOO 0.63.0) AND THE
TEXTURE HALF (PIXELCOAT 0.29.0) SHIPPED AND WIRED TO EACH OTHER; THE STYLE
HALF IS NAMED AND UNBUILT.""",
"""*STATUS: NARROWED 2026-09-12 (night) -- ALL THREE HALVES SHIPPED: PROPS
(ZOO 0.63.0), TEXTURES (PIXELCOAT 0.29.0), STYLES (ZOO 0.64.0); ONE WORKED
EXAMPLE OF EACH IN A COLD PACKAGE IS WHAT REMAINS. `zoo/tools/new_species.py
style <theme>` reports which species resolve a theme to the uncoloured
`default` -- measured: 0 of 57 carry `delco_1997` by name, 43 resolve to
`delco` through the family walk, 14 to `default` (atm, briefcase,
cash_stack, chair, cheesesteak, crt_tv, desk, filing_cabinet,
flat_top_grill, ...) and wear no colour in a delco level -- and with
`--write` mints a row under the theme's own name, copied from the ancestor
each resolves to or from `--like`, with material / wear / ambient / colour
overrides. A copied row is the ancestor's look under a new name, which is
the honest state of a style nobody has tuned; the genome's `styles` block
is where the tuning goes. The three tools share one shape -- report the
queue, mint from a template, prove it validates, register it, say what
the next repo needs -- and a page in USING_THE_FACTORY.md walking "the
brief wants a planter" through all three is the last piece. Previously:
THE PROP HALF (ZOO 0.63.0) AND THE
TEXTURE HALF (PIXELCOAT 0.29.0) SHIPPED AND WIRED TO EACH OTHER; THE STYLE
HALF IS NAMED AND UNBUILT."""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: {old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 44, 150 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
