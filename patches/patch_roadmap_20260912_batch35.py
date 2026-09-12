"""Roadmap batch 35, 2026-09-12: cold run 9011 (17 REPLACE, old kept) and the
teller line from the walker's references (44 REPLACE, old kept); 150 gets
the reference step and the page (REPLACE, old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 (later) -- COLD RUN 9010 SCORED ZERO ON THE
BANK BRIEF WITH THE RUNS IN THE PACKAGE:""",
"""*STATUS: NARROWED 2026-09-12 (night) -- COLD RUN 9011 SCORED ZERO ON A GAS
STATION BRIEF NEVER RUN, THE ANCHOR HELD, AND THE PUMP DID NOT SHIP BECAUSE
THE VARIANT THE ANCHOR DREW HAS NO PUMPS. `gas_stop_001`, archetype
`gas_station`, three buildings, delco_1997, crew 4, on DC 0.118.0 / Zoo
0.64.0 / LF 0.73.1: 0 interventions, 0 retries, 0 unattributed changes,
every tool repo clean at --begin, all stages succeeded, export exit 0, 12
minutes (08:28 -> 08:40). Lot `gas_station_a03` / auto_shop_a01 /
clinic_a02 -- the anchor family led. Kit indexes: the station's register
counter, two 7 m aisles, a 6 m cooler backstock and a stock shelf built as
counter and shelving runs, the shop's desk / counter / shelving as before;
zero fallbacks, zero alternates. The minted `pump` (item 150) is in seven
shells -- gas_station_a01, gas_station_a02, gas_street, gs_corner_station,
cr_gas, fuel_stop_heist, gas_station -- and not in `gas_station_a03`,
which the seed drew; the family anchor picks a variant, not a volume. The
eighth zero. Log and journal: `docs/cold_runs/cold_9011/`. Previously:
COLD RUN 9010 SCORED ZERO ON THE
BANK BRIEF WITH THE RUNS IN THE PACKAGE:"""))

R.append(("""*STATUS: NARROWED 2026-09-12 (night) -- THE 179 WORKED DOWN TO 52, AND
THOSE ARE REGIONS, NOT FURNITURE: 728 OF 780 HINTED PLACEMENTS PLAN AS
THEIR SPECIES.""",
"""*STATUS: NARROWED 2026-09-12 (late) -- THE TELLER LINE IS A GLASS BARRIER
WITH A WINDOW PER STATION, FROM THE WALKER'S REFERENCES; COLD RUN 9012 IS
THE PACKAGE. The walker, on 9010's teller counter frame: "teller windows
are usually facing a glass where people would be behind it", with four
photographs, and "simple google searches of the zoo species can inform the
design before we hit blender". What the references say: a continuous
counter at waist height, a glass barrier over it to a header, one service
window per station with a pass-through at the counter, posts between
stations. Zoo's `teller_line` had the counter, posts, header, bulletproof
glass and slot since it was written and NEVER FIRED, because every
`teller_counter` volume was authored as the counter alone (1.0-1.2 m
tall) and the barrier starts at 2.0 -- so 0.118.0 routed the name to
`counter` and the bank shipped a wooden run. The volume was the
placeholder for the counter; the line is what the name meant. DC
0.119.0: the bank preset authors the line at 12 x 0.8 x 2.4 (a barrier
on purpose: the lobby is 30 m wide, the line 12, the crew walks around
either end) and the 37 committed specs with a waist-high teller are
migrated the same way; `teller` routes to `teller_line` again. Zoo
0.65.0: the recipe builds in bays of 2.0 m -- counter and header the full
run, a post at every station boundary, each station's glass with its own
service opening and a tray attachment -- its docstring saying what it is
a drawing of; a teller still at counter height falls to `counter` by the
alternate rule. Built through Blender: a 12 x 0.8 x 2.4 line, seven
posts, six windows, PASS; the bank tower's 3.2 x 1.2 x 2.4 (depth opened
to 1.2). The process note is now the tool's: `new_species.py new
--reference` writes what the real thing looks like into the genome, and
the minting page in USING_THE_FACTORY.md opens with "look at the real
thing first". Previously: THE 179 WORKED DOWN TO 52, AND
THOSE ARE REGIONS, NOT FURNITURE: 728 OF 780 HINTED PLACEMENTS PLAN AS
THEIR SPECIES."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (night) -- ALL THREE HALVES SHIPPED: PROPS
(ZOO 0.63.0), TEXTURES (PIXELCOAT 0.29.0), STYLES (ZOO 0.64.0); ONE WORKED
EXAMPLE OF EACH IN A COLD PACKAGE IS WHAT REMAINS.""",
"""*STATUS: NARROWED 2026-09-12 (late) -- THE PAGE IS WRITTEN AND THE
REFERENCE STEP IS IN THE TOOL; THE WORKED EXAMPLES IN A COLD PACKAGE
REMAIN. `USING_THE_FACTORY.md`, "Minting, step by step: from 'the brief
wants a planter' to the planter": step 0 is look at the real thing (the
walker: "simple google searches of the zoo species can inform the design
before we hit blender" -- the teller line shipped as a plain counter for a
day because nobody had), then report / mint the prop / route the name /
mint the texture / mint the style / run it cold, each with the command.
`new_species.py new --reference "..."` carries the looking into the
genome. The minted pump is in seven shells and reached no package yet:
9011's anchor drew `gas_station_a03`, which authors no pumps -- item 149's
anchor picks a family's variant, not the volume a brief wants, and that
is the next thing to say on 149. Previously: ALL THREE HALVES SHIPPED: PROPS
(ZOO 0.63.0), TEXTURES (PIXELCOAT 0.29.0), STYLES (ZOO 0.64.0); ONE WORKED
EXAMPLE OF EACH IN A COLD PACKAGE IS WHAT REMAINS."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 44, 150 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
