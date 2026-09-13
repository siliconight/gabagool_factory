"""Roadmap batch 56, 2026-09-13: cold run 9037 counted SEVEN interventions,
all mine -- a tool repo edited while it ran (17 REPLACE, old kept); the
walker's Call of Duty frames and what they ask for (153 REPLACE, old kept).
Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (morning) -- COLD RUNS 9035 AND 9036 SCORED
ZERO: FIVE TREE SPECIES, THEN THE 1990s AMERICAN STREET.""",
"""*STATUS: NARROWED 2026-09-13 (morning) -- COLD RUN 9037 COUNTED SEVEN
INTERVENTIONS AND EVERY ONE WAS MINE. The run itself was clean by every
other measure -- all stages succeeded, 0 blockers, export exit 0, and its
own question answered: 8 stop signs stood at the driveway cuts where 9036
had none. But `cold_run.py --end` found seven tool source files changed
that nothing wrote down: `pixelcoat/` at 0.33.0, edited and committed
WHILE THE RUN WAS IN FLIGHT, which is the one thing this repo's own rules
forbid ("a tool-repo edit during a cold run counts as an intervention").
The art stage then ran on a Pixelcoat the --begin snapshot had never
seen. Nothing about the pipeline failed; the operator did, and the
instrument caught it, which is what it is for. 9037 is recorded as SEVEN,
not as a zero, and cold run 9038 re-asks its question on a clean tree.
The habit that prevents it is the one already written down: check that no
run is in flight before touching a tool repo, and when one is, draft in
the scratchpad. Previously: COLD RUNS 9035 AND 9036 SCORED
ZERO: FIVE TREE SPECIES, THEN THE 1990s AMERICAN STREET."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (morning) -- THE STREET IS 1990s AMERICA, AND
EVERY ROAD HAS ITS OWN TREE.""",
"""*STATUS: NARROWED 2026-09-13 (morning) -- THE SIGNS ARE RENDERED AND THE
WALKER'S FRAMES NAME WHAT THE FORECOURT STILL LACKS. Pixelcoat 0.33.0:
`theme-signs` builds one pack per business a theme names --
`profiles/signs/delco_1997.json`, 22 of them: GOOSE MART, HOAGIE HUT,
BEER WORLD, STATE WINE + SPIRITS, THE RUSTY TAP, CLUB VELVET, VIDEO STOP,
APEX MARKETS, KEYSTONE SAVINGS, LUBE-N-GO, DELCO STORAGE -- with an index
of slug, text and the families of business each suits. EVERY NAME IS
INVENTED and the profile says so in a line a test asserts. `fit_scale`
makes a name fit its panel: the first build read GOOSE MART as "OOSE MAR",
because the default glyph scale puts a ten-character name 360 px wide on
a 256 px tile. The walker: "those are fine for placeholders", and "the
fonts are lazy for now" -- the 5x7 bitmap face is accepted as a
placeholder and is residue, not a finding.

THE CALL OF DUTY FRAMES (docs/SET_DRESSING_REFERENCES.md, digested): a
shop's name is a BAND ACROSS ITS FRONTAGE, not a plaque; a PYLON SIGN
stands at the kerb where a driver reads it first; NUMBERS sit on things
(each pump bay numbered on its column); CLUTTER COMES IN CLUSTERS of
cheap objects (four blue drums, stacked pallets, a concrete barrier
across a lane, banded bollards at every column base); and walls, fences
and hoardings divide a lot from the street at knee-to-eye height. Held
against them, what this pipeline has right is the street -- road, kerbs,
paint, parking, trees, furniture, junction -- and what it lacks is the
FORECOURT. Drafted and not yet landed: Lot hanging the band on the facade
that faces the street (`sign_placement`, sized from the facade), and four
Zoo species for the clusters (`jersey_barrier`, `water_barrel`,
`bollard`, `pallet_stack`). Not drafted: the pylon sign, the numbers, the
fences. Previously: THE STREET IS 1990s AMERICA, AND
EVERY ROAD HAS ITS OWN TREE."""))


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
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 153 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
