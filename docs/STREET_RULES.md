# Street rules: stop signs and crosswalks

The walker supplied these on 2026-09-13, after walking cold runs 9046 and 9048
and finding stop signs in pairs at footpath crossings and a crosswalk-width path
laid across the street from every building door (roadmap 155). They are the
standard Lot's street planner builds to. Summarised here in this repo's words,
with the sources named; read the sources for the full text.

Owner: **Lot** (`site_streets.py` crossings and markings, `site_furniture.py`
traffic control). **Level Factory** owns the spur paths it hands Lot.

## Stop signs

Sources: MUTCD placement guidance as summarised by the walker (Quora thread on
right-side placement; Crash Champions knowledge center; City of Napa stop sign
guidance).

- **One sign per approach, on the driver's right.** The sign serves the traffic
  arriving on that leg, and a driver looks right for regulatory signs.
- **Lateral offset:** at least 6 ft (1.83 m) from the edge of the pavement.
- **Longitudinal position:** no more than 50 ft (15.2 m) from the intersection,
  and about 4 ft (1.2 m) before a marked crosswalk line where one exists.
- **A second sign on the left** only for wide intersections or multi-lane
  approaches, where a driver could miss the right-hand one.
- **The plate faces the approaching driver, with the post behind it,** and the
  face carries the white STOP legend inside a white border.
- **A footpath is not an approach.** A pedestrian spur or a door path gets no
  stop sign; a parking-lot exit onto a public street may.

## Crosswalks

Source: NACTO, *Urban Street Design Guide*, "Crosswalks and Crossings".

- **Every leg of a signalised intersection gets a marked crosswalk,** unless
  pedestrians are prohibited there or there is no pedestrian access on either
  corner. Leaving one leg unmarked forces a three-stage crossing that people do
  not comply with.
- **Busier streets mark every intersection.** Above roughly 3,000 vehicles a
  day, above 20 mph, or on streets of two or more lanes, crosswalks are the norm
  at intersections. On quiet one-to-two-lane streets under 20 mph they are not
  always needed at intersections, except near schools, parks, plazas, senior
  centres, transit stops, hospitals, campuses and major public buildings, where
  they help regardless of traffic.
- **Unmarked is not a safety measure.** Leaving an uncontrolled crossing
  unmarked to discourage crossing encourages risk-taking instead; enhance the
  crossing (beacons, raised crossing, median) rather than hide it.
- **Mid-block signalised crossings** are typically spaced at least 200 ft
  (about 61 m, one short block); unsignalised crossings may be closer where
  demand exists.
- **Cross in one cycle, at grade.** No pedestrian overpasses or underpasses
  except over limited-access highways. Pedestrians should cross a whole
  intersection in a single signal cycle unless a transit median divides it.
- **Pedestrian signals with countdowns** on all new signalised crosswalks.
- **No channelised "porkchop" turning islands.** Turning traffic fails to yield
  to people crossing at them.
- **Delay drives non-compliance:** waits beyond about 40 s at signalised and
  20 s at unsignalised crossings push people to cross against the signal.

## What this means for the generator, as of 2026-09-13

- Level Factory's door-to-street spurs end on the road's centre line so Lot
  will cut the kerb there. A building door opens onto the sidewalk; a spur
  should end at the sidewalk, and a crossing belongs at an intersection or at
  a deliberate, spaced mid-block crossing -- not in front of every door.
- Lot treats any kerb cut 3.5 m or wider as a driveway and signs it. A spur is
  4 m wide, so every footpath got a pair of stop signs. Stop signs belong to
  junction approaches, placed by the rules above.
- Lot's signalised junctions should mark every leg; its unsignalised side-street
  junctions follow the volume and speed rule above.
