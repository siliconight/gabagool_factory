"""The texts make_rm_review_1020.py writes into the roadmap patch."""

REVIEW = "the look review of 2026-10-20, `docs/findings/walker_review_2026-10-20/verdicts_2026-10-20.json`"

HEADS = [
    (79, 'NARROWED 2026-10-20 -- THE WALKER ON THE STACKED FRONTS: "Better", and where stacking and symmetry trade, '
         '"Symmetry" (' + REVIEW + ', on cold run 9348\'s fronts against 9282\'s). Symmetry is the rule Deli Counter '
         '0.238.0 shipped as its default -- `stack_mirrored` moves an upper window only together with its mirrored '
         'pair -- and it is now the walker\'s call rather than the factory\'s. Left: the primary bay, corners and masses '
         'as designed conditions, piers chosen rather than left (74), and a family re-planned whole with its ground '
         'floor (step 4, the walker\'s choice).'),
    (148, 'NARROWED 2026-10-20 -- THE WALKER ON THE SCREENS: "Looks right" (' + REVIEW + ', on cold run 9350\'s office '
          'against 9349\'s). Left: denser rooms from the kinds already made; a clock, a ceiling vent, a smoke detector, a '
          'light switch and an exit sign, which no species draws; the no-collision dressing layer; and whether a room '
          'reads as inhabited, the walker\'s eye.'),
    (170, 'NARROWED 2026-10-20 -- THE WALKER ON THE MATCH: "Looks right" (' + REVIEW + ', on cold run 9352\'s bank roof '
          'against 9348\'s, in the inspection light). Left: the bulkhead below.'),
    (210, 'NARROWED 2026-10-20 -- THE BOOTH\'S MARKS ARE SMALL, AND MOSTLY WEATHER: the walker\'s look review of 2026-10-20 (`docs/findings/walker_review_2026-10-20/verdicts_2026-10-20.json`) -- the phones facing the sidewalk "Looks right"; the marks "Needs work": "more subtle graffiti/weathering....a large shapie squigle doesn\'t look like anything". Zoo 1.117.0 (48fdc71, `patches/patch_zoo_booth_marks.py`) marks every booth, the plain look too, with what hands and weather leave: tags in Delco words in a marker\'s 7 mm line, each in its own hand; keyed initials; rain runs; scuffs; scratches; torn sticker paper; a tag the phone company painted over -- each side panel its own, nothing behind the phone, no dark stroke 3 px across, nothing inked past 0.75 of the way to black; the geometry unchanged to a hash. Cold run 9355 (restaurant_row_001, seed 9003, 9351\'s level, 0 interventions, findings 108 -> 108; `docs/cold_runs/cold_9355/`): from 1.5 m the booths show words where 9351\'s showed marker waves, and from 4 m they read clean; priced against a control rebuilt in the same session, 90,168 bytes of texture memory and nothing else measurable. Left: the city / rural / special rule for where phones stand (the walker: "you decide"), the indoor wall units\' marks by place (Deli Counter\'s slots carry no variant), and the walker\'s eye on the new marks -- and on the hood lamp washing a booth\'s inside nearly white at 1.5 m.'),
    (217, 'NARROWED 2026-10-20 -- THE WALKER ON THE TWO DAYS: the morning "Looks right" and the high noon "Looks right" '
          '(' + REVIEW + ', on cold runs 9353 and 9354). Left: the rainy night ("Needs work", 2026-10-19), the rainy '
          'day\'s weak sun, and the window light\'s dial.'),
    (261, 'CLOSED 2026-10-20 -- THE PANEL SAYS WHAT IT COUNTS: Level Factory 0.226.0 (7a83a9a, '
          '`patches/patch_lf_prims_label.py`) prints `draw <n> calls  <n> prims (all passes)  <n> objects`, and '
          '`test_the_primitives_monitor_is_not_called_triangles` holds its format string, failing on 0.225.0 '
          '(`patches/lf_prims_label/prove_tests_on_0225.out.txt`); the suite 2,551 passed. `docs/DRAW_CALL_BUDGET.md`\'s '
          '9088 table, read off that panel, and the two sentences that read it say primitives across all passes '
          '(`patches/patch_doc_draw_budget_prims.py`); the finding they support does not move: frame time followed the '
          'draws while this figure barely did. Left on purpose: CLAUDE.md\'s "1.4M triangles" sentence is the walker\'s '
          'text, theirs to change.'),
    (267, 'NARROWED 2026-10-20 -- THE WALKER ON ARENA_A02\'S BARRIER: "Crowd rails (a new model)" (' + REVIEW + '), '
          'not the jersey barrier: a new Zoo species, the steel crowd-control barricade on its flat feet, and Deli '
          'Counter\'s `barrier` routed to it -- queued, not started. Left: that; `container` -> `cargo_container` behind '
          'a rule for depth-long species; the stair guards (1,025) once a frame shows how a box reads as a guard; the '
          'runs and the new species the rest want; and the share in a cold run\'s package.'),
]

BODY_210 = '**THE MARKS, SMALL AND MOSTLY WEATHER, 2026-10-20** (Zoo 1.117.0, 48fdc71; `patches/zoo_booth_marks/`; `docs/cold_runs/cold_9355/`). The walker read 9351\'s booths on the look-review page: the facing right, the marks not -- "a large shapie squigle doesn\'t look like anything". 1.116.0 drew a tag as a sine wave of discs 3 px (19 mm) across over as much as 74 % of a side panel, laid disc over disc at 0.85 so that it inked all but opaque, and one tile showed on both side panels, so a booth\'s two sides carried the same marks facing each other. 1.117.0 writes words -- JAWN, JEET, ARDY, YOUSE, WOODER, DRAWL, JABRONI, WIT, in stroke letters, each tag in its own lean, width, spacing, shake and tilt, 5 to 8 cm tall, faded to 0.45-0.75, each word and pair of initials once in a booth, a word too long for its panel written smaller and never shortened -- and lays the weather under them. Measured against the unmarked paint rebuilt with the module\'s own helpers, over every form and variant at the default slot and the genome\'s extreme corners: pixels the marks darkened by more than 40 that sit in a 3 x 3 block of them, at most 1 a panel (1.116.0: 92 on the default booth\'s back panel, 230 on its side panel, 987 at a corner); the strongest mark on a white booth 0.75 of the way to black (1.116.0: 1.0). Found on the way and fixed before it shipped: the first painting wrote the same two words on two panels of one booth, and the torn sticker\'s ragged pieces, laid one over another, stacked into a patch as heavy as a tag. **The price, and what it taught about the instrument:** the first read against 9351\'s stored price showed 184 fewer draws, +0.7 to +1.0 ms a heading and 14 MiB less video memory for a change that only adds texture. A control rebuilt in the session -- 9355\'s package with 1.116.0\'s booths swapped back -- read 9355\'s draws at all 53 headings and its p95 within 0.030 ms against a 0.151 ms floor, and 9351\'s own bytes, rebuilt the same way, read 9355\'s draws too. On identical bytes the session had moved the evening draws at two headings (92 each), the frame time (+0.61 ms a heading on the morning package) and the buffer memory (61.6 MB -> 44.6-48.8 MB); texture memory never moved, and it is what the booths cost: 90,168 bytes. What moved the rest is not attributed.'

DOC = '''"""Roadmap: the walker's look-review answers of 2026-10-20 onto items 79, 148, 170, 210, 217 and 267, each in front
of the status it had; item 210's status and a dated paragraph for Zoo 1.117.0 and cold run 9355, the marks the walker
sent back; item 261 CLOSED.

The answers were saved on the review page (https://claude.ai/artifact/TSdXhvhicTf7o3keriGH6Z, collection `verdicts`)
and exported beside its finding (`docs/findings/walker_review_2026-10-20/verdicts_2026-10-20.json`). Anchored on each
item's whole status block, which must stand once and directly above its heading, and on the end of item 210's body;
nothing is written on a miss. Then `python tools/roadmap_status.py --write` and `--check`.

    python patches/patch_roadmap_look_review_2026_10_20.py
"""
'''
