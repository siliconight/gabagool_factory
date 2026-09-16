"""Roadmap batch 65: cold runs 9055-9060, the club's status, and the two
building types the walker named next.

Anchored: every anchor must match exactly once or the patch refuses to write.
Run from the factory root; then `python tools\\roadmap_status.py --write`.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"

# --- 1. item 17: the eight runs since the last entry -----------------------
#
# The status stack above item 17 has drifted into five blocks separated by
# blank lines, and `roadmap_status.py` reads only the block DIRECTLY above a
# heading -- which is why the index has carried item 17, the item this repo
# exists to answer, as "OPEN (inferred)" with no evidence. So this entry goes
# where the parser looks, as one block, and says where the history is.

A17 = """**17. The pipeline has never been run cold, so nobody knows what it costs to
make a level.** The item the other sixteen do not cover."""

B17 = """*STATUS: NARROWED 2026-09-16 -- FOUR MORE ZEROS AND THREE MORE REFUSALS IN
RUNS 9053-9060, AND EVERY REFUSAL WAS A GATE NAMING ITSELF RATHER THAN A RUN
FALLING OVER. Journals in `docs/cold_runs/cold_9053..9060/`, each with 0 rows:
no run in the set needed a hand-patch, including the four that produced no
package.
- **9055 and 9056 stopped at the same sentence**, graybox exit 5:
`functional_shell_locked REFUSED for club_block_001: the lock this would write
protects nothing`. The club preset existed in Deli Counter and not in the
vocabulary Level Factory checks against. 9056 repeated 9055 exactly because a
Deli Counter merge was taken on an agent's claim that "LF needs nothing"
instead of on a reading of the keyword fallback, which iterates Level
Factory's own preset list -- item 161's lesson, second instance. LF 0.87.1
added `strip_club` and `twin` plus a test comparing Level Factory's list
against Deli Counter's registry, so the next divergence fails in unit tests
rather than five stages into a cold run.
- **9057: a zero**, export exit 0, and the first GENERATED strip club and hero
vault room in a cold package.
- **9058: refused at export**, exit 2, `JOB_PREFLIGHT_REFUSED` --
"LT_ObjectivePoint is sealed off from the crew spawn": pre-flight and the
baked navmesh disagreeing about one level. Laser Tag 0.23.1 now takes the bake
settings from `agent_contract.json` rather than from its own constants, which
is the half of that disagreement this repo owns.
- **9059: a zero**, with dartboards, cigarette machines, CRTs showing a
ballgame, and every room dark.
- **9060: a zero**, with the club's back bar, the bartender's aisle at the
teller line's clearance, and the CRT sync roll.
The thesis holds and cuts both ways again: a zero says only that nothing was
hand-patched. WHERE THE REST OF THIS ITEM'S HISTORY IS: every status era
before this one is the stack of paragraphs ABOVE this line, newest first, back
to cold run 9003. That stack is prose the index cannot read -- `_block_above`
takes the nearest non-blank BLOCK, and five blank lines inside the stack mean
the block it finds does not start with `*STATUS:`. This line is that block; the
history above is unchanged, and the same drift affects the other nine items
`roadmap_status.py --unclassified` lists.*

**17. The pipeline has never been run cold, so nobody knows what it costs to
make a level.** The item the other sixteen do not cover."""

# --- 2. item 163: the club is generated -------------------------------------

A163 = """*STATUS: OPEN 2026-09-14 -- PIECES, SURFACES AND LIGHT TYPES SHIPPED; THE
ROOM IS NOT YET GENERATED, AND INTERIORS DO NOT YET READ DARK.*"""

B163 = """*STATUS: NARROWED 2026-09-16 -- THE CLUB IS GENERATED, IT IS DARK, AND THE
LIGHT NOW COMES OUT OF FIXTURES. WHAT REMAINS IS AIM AND TUNING. Cold run
9057 drew the first generated strip club (export exit 0, 0 interventions);
9059 added dartboards, cigarette machines and CRTs showing a ballgame with
every room dark; 9060 added the back bar, the bartender's aisle at the bank
teller line's clearance, and the CRT sync roll. Between them: Lux 0.38.0 and
LF 0.87.0 made interiors dark by default (per-room probes, sun shadows at the
cheapest cascade, fog kept); Zoo 0.94.0 gave the club's light visible
hardware after the walker asked "where is the light fixture giving that
light?"; Lux 0.39.0/0.40.0 added the back-bar lamp row and softened the
back-bar light from a sun to a glow; LF 0.89.0 attached the CRT roll as an
import-time `next_pass`, measured below the noise floor. Open, each with an
owner: Lot's `merge_lights` does not transform `stage_light.target`, so
9060's stage light baked to energy 0 and drew black; Deli Counter does not
yet write `room_drop` on club anchors or a building-local target; a01's
window still lights a windowless box; neon signs are occasionally not placed
at all; the room may still be too dark for the walker, which is a walk call
and not a measurement.*"""

# --- 3. two new items -------------------------------------------------------

TAIL_ANCHOR = """**WHAT WOULD CLOSE THIS:** the walker walks a generated strip club and calls
it dingy."""

NEW = TAIL_ANCHOR + """


*STATUS: OPEN 2026-09-16 -- SPECIFIED FROM THE WALKER'S OWN PHOTOS; THE FIRST
SLICE IS BEING BUILT.*

**164. The library has no card shop and no convenience store, which are the
two building types the walker asked for next.** The walker, 2026-09-15: "I
have 2 building types... 1. A 'Wawa' convenience store 2. A 90s Trader Card
Shop (Fake Pokemon, Fake Magic, Fake sports trading cards)", with nine
reference photos of each, then "convenience stores are usually connecting to
gas stations, so we already have the gas station pumps that we can use, now
with the understanding that cars should have clearance to use them
(connectivity to road, etc)". The photos did not reach disk; they are
transcribed in `docs/SET_DRESSING_REFERENCES.md` under "The walker's trading
card shop references", "convenience store references" and "pump forecourt
references", with the owner of each piece named.

Two things are already measured and are defects the forecourt work must fix,
not guesses:

- **The end aisles are 3.0 m wide and a car is 4.3-4.8 m long.** A forecourt
  a car cannot enter is scenery, and the reachability of a pump from the road
  is a Lot gate that does not exist yet.
- **Two canopy columns stand in the outer lanes' swept path.** Placed to the
  canopy's grid rather than to the lane's.

Every brand in either building is invented in the Delco voice, with a
denylist test, as the vending machines and the neon signs already are -- no
real mark reaches a texture.

**WHAT WOULD CLOSE THIS:** a cold package whose lot draws a card shop and a
convenience store with a forecourt, and the walker walks in, buys nothing,
and does not ask what either building is.


*STATUS: ANALYSIS 2026-09-16 -- A STANDING CONSTRAINT ON EVERY LOOK THIS
PIPELINE SHIPS, NOT A DEFECT.*

**165. This is a multiplayer online game, so every frame is spent on
somebody else's machine.** The walker, 2026-09-16: "I will always choose
performance over look/graphics as this game will be multiplayer online so we
don't need more bottlenecks where things could fall over", then, in the same
breath, "you can present the tradeoffs when you think we are leaving
something on the table we could have, so don't be so binary...but we lean
towards performance when we can" and "we can always optimize later once we
have better data from runtime tests".

That is an ordering, not a veto, and it has a method attached which this
repo has already used twice: LF 0.89.0's CRT roll shipped because it was
priced on/off across several stations with a no-change control and landed
below the noise floor; Lux 0.38.0's sun shadows were chosen at the cheapest
cascade for the same reason. The rule now lives in `CLAUDE.md` ("Every frame
is spent on somebody else's machine") and says: price a look before shipping
it; when the cheap version loses something real, ship the cheap version AND
state what the expensive one would have bought, with figures, because the
spend is the walker's call; never refuse a look on an unmeasured guess; and
record the budget rather than closing the question, because no runtime
telemetry from real sessions exists yet.

The shapes already deferred on this ground: screen-space post-processes and
depth-texture reads (item 157's puddle reference), more than
`max_lights_per_object` (8) lights reaching one mesh, and per-frame CPU work
that scales with prop count. Zoo's per-species triangle budgets are the
existing instrument and the model for the rest.

**WHAT THIS IS NOT:** a reason to narrow a look quietly. An undocumented
narrowing is not a performance decision."""


def _apply(text, anchor, replacement, label):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"REFUSED: anchor {label} matched {n} times, expected 1")
    return text.replace(anchor, replacement)


def main():
    data = ROADMAP.read_bytes()
    if data.count(b"\r\n"):
        raise SystemExit("REFUSED: roadmap is LF; CRLF found")
    text = data.decode("utf-8")
    before = len(data)
    text = _apply(text, A17, B17, "item 17 status")
    text = _apply(text, A163, B163, "item 163 status")
    text = _apply(text, TAIL_ANCHOR, NEW, "tail / new items")
    ROADMAP.write_bytes(text.encode("utf-8"))
    after = len(ROADMAP.read_bytes())
    print(f"roadmap {before} -> {after} bytes (+{after - before})")


if __name__ == "__main__":
    main()
