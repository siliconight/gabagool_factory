"""Level Factory's ground-contact pre-flight on a cold run's scenes, twice: as it reads a Transform3D (the nine basis
numbers as COLUMNS, `ground_contact._transform` through Level Factory 0.218.1) and with them read as ROWS, as Godot
4.7 writes them (this folder's README). Both readings are defined here, so the probe means the same on either side
of 0.218.2; everything else is the module's own code, and only `_transform` differs. For
each scene: the problems `check_ground_contact` reports, the boxes it read, and the boxes whose centre moved. A
probe: prints and stops (roadmap 177's defect class, found in Deli Counter's z-fight gate).

    python docs/findings/zfight_rows_177/ground_contact_rows.py <level_factory dir> <scene.tscn> [...]
"""
import os
import sys

lf = os.path.abspath(sys.argv[1])
sys.path.insert(0, lf)
from packages.validation import ground_contact as G  # noqa: E402

shipped = G._transform


def columns(body):
    match = G._TRANSFORM.search(body)
    if match is None:
        return G._IDENTITY
    values = G._floats(match.group(1))
    if len(values) != 12:
        return G._IDENTITY
    return tuple(tuple(values[3 * col + row] for col in range(3)) + (values[9 + row],) for row in range(3))


def rows(body):
    match = G._TRANSFORM.search(body)
    if match is None:
        return G._IDENTITY
    values = G._floats(match.group(1))
    if len(values) != 12:
        return G._IDENTITY
    return tuple(tuple(values[3 * row + col] for col in range(3)) + (values[9 + row],) for row in range(3))


def run(fn, scene):
    G._transform = fn
    try:
        reading = G.read_scene(scene)
        problems = G.check_ground_contact(scene)
    finally:
        G._transform = shipped
    return reading, problems


for scene in sys.argv[2:]:
    p = os.path.abspath(scene)
    a, pa = run(columns, p)
    b, pb = run(rows, p)
    ca = {bx.name: tuple(round(v, 3) for v in bx.centre) for bx in a.boxes}
    cb = {bx.name: tuple(round(v, 3) for v in bx.centre) for bx in b.boxes}
    moved = sorted(n for n in set(ca) & set(cb) if ca[n] != cb[n])
    print("%s\n   columns: %d box(es), %d problem(s) | rows: %d box(es), %d problem(s) | centres moved: %d"
          % (scene, len(a.boxes), len(pa), len(b.boxes), len(pb), len(moved)))
    for n in moved[:5]:
        print("      %s  %s -> %s" % (n, ca[n], cb[n]))
    if pa != pb:
        print("   problems differ:\n      columns: %s\n      rows:    %s" % (pa, pb))
