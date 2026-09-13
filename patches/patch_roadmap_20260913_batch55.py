"""Roadmap batch 55, 2026-09-13: cold runs 9035 and 9036 (17 REPLACE, old
kept); the five species per road and the 1990s American street kit (153
REPLACE, old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-13 (late night) -- COLD RUN 9034 SCORED ZERO WITH
THE TREE GROWN BY SPECIES.""",
"""*STATUS: NARROWED 2026-09-13 (morning) -- COLD RUNS 9035 AND 9036 SCORED
ZERO: FIVE TREE SPECIES, THEN THE 1990s AMERICAN STREET. 9035 on Zoo
0.71.0 / Lot 0.67.0 (12 minutes, every module `pass`): the five street
trees as species of their own, planted one per road -- and it drew red
maples on BOTH roads, which is the one hash collision in five that shows,
fixed in Lot 0.68.0. 9036 on Zoo 0.72.0 / Lot 0.68.0 (07:02, export exit
0, 16 of 16 modules `pass`): the 1990s street standing -- 32 parking
meters, a mast-arm traffic signal at the junction, 2 mailboxes, 4 news
racks, a payphone, callery pears on one road and red maples on the other.
Both zeros: 0 interventions, 0 retries, 0 unattributed changes. The
twenty-fifth and twenty-sixth. Frames: `docs/cold_runs/cold_9036/frames/`
-- the signal's arm over the near lane with its cobra luminaire the other
way, and the bus stop with a payphone, two news racks, a mailbox and a
meter beside the shelter. Previously: COLD RUN 9034 SCORED ZERO WITH
THE TREE GROWN BY SPECIES."""))

R.append(("""*STATUS: NARROWED 2026-09-13 (late night) -- THE TREE IS GROWN BY SPECIES,
IN A COLD PACKAGE (9034).""",
"""*STATUS: NARROWED 2026-09-13 (morning) -- THE STREET IS 1990s AMERICA, AND
EVERY ROAD HAS ITS OWN TREE. The walker: "the streets should look like
America in the 1990s -- USPS mailboxes, stop signs, traffic lights".
Zoo 0.72.0 mints the kit, each piece shaped: `stop_sign` (a 30-inch
octagonal blade on a u-channel post), `traffic_signal` (mast arm over the
near lanes, a three-lens head at its end, a second on the pole, and a
cobra luminaire arm the other way -- which is what puts the pole at the
module's centre so its greybox box is a pole and not 8 m of arm across the
carriageway), `mailbox`, `newspaper_box`, `parking_meter`, `payphone`.
Nothing reproduces anybody's markings. Lot 0.68.0 places them: a signal
where a leg meets an ARTERIAL (sidewalks and parking lanes) and a stop
sign at every other junction mouth facing the approaching driver, a meter
at every parking bay, and the mailbox, news racks and payphone at the bus
stop. THE TREES: Zoo 0.71.0 mints the five as species of their own, each
with its own slot dims, and Lot plants one species per road (`tree_for`,
a hash of the road's endpoints) with a road that meets another taking the
next species along. `geometry.fit_to` makes a detailed piece exact -- all
six of the kit missed their slot depth the first time they built, because
a door or a visor sits proud of a face. WHAT REMAINS: the generated spec
only makes signalised T junctions, so a stop sign has nowhere to stand in
a cold package yet -- the driveway a spur cuts is where that decade put
one. And the signage: nothing in the pipeline builds a sign today and no
building carries a storefront sign slot, so the parody brands the walker
asked for (a Wawa, a beer distributor, a bar) need Deli Counter to cut the
slot, a brand table per archetype, Pixelcoat to render the face and Zoo's
`sign_box` to wear it. Lux already lights that cabinet. Previously: THE
TREE IS GROWN BY SPECIES,
IN A COLD PACKAGE (9034)."""))


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
