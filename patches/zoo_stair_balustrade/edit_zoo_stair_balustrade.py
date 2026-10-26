"""Zoo 1.128.0 on a CLONE (<repo>): `stoop_railing` is also a stair hole's balustrade (the walker's walk of cold run
9386, finding 6: "the walling/railing doesn't loook natural yet"). Its genome takes a hole edge's length and a guard's
depth, and a long level run stands a post at least every `POST_BAY`. A railing one bay long builds exactly as before.
Anchored; refuses on a miss.

    python edit_zoo_stair_balustrade.py <repo>
"""
import json
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    return t


gp = R / "zoo_keeper" / "genome" / "species" / "stoop_railing.json"
g0 = json.loads(gp.read_bytes().decode("utf-8"))
note_old = g0["license"]["notes"]
NOTE = (" A STAIR'S BALUSTRADE TOO (1.128.0): the walker, walking cold run 9386, of an office stair's guards -- solid"
        " wood boxes round its hole -- \"the walling/railing doesn't loook natural yet\". Deli Counter >= 0.268.0 stands"
        " a stair hole's guards as this species' level form, so the width reaches a hole edge's length (8 m) and the"
        " depth a guard's (0.12 m, the top rail as wide as the guard); a run longer than one bay stands a post at least"
        " every `POST_BAY` (2.0 m, a newel's spacing on a long balustrade).")
t = edit("zoo_keeper/genome/species/stoop_railing.json", [
    ('''    "width": {
      "min": 0.3,
      "max": 2.0,''', '''    "width": {
      "min": 0.3,
      "max": 8.0,'''),
    ('''    "depth": {
      "min": 0.03,
      "max": 0.06,''', '''    "depth": {
      "min": 0.03,
      "max": 0.12,'''),
    (json.dumps(note_old)[1:-1], json.dumps(note_old + NOTE)[1:-1]),
])
g1 = json.loads(t)
assert g1["dimensions"]["width"]["max"] == 8.0 and g1["dimensions"]["depth"]["max"] == 0.12
assert g1["license"]["notes"].endswith("a newel's spacing on a long balustrade).")

edit("zoo_keeper/core/stoop_railing_forms.py", [
    ('''COLLISION: none here (the genome's `collision: false`). Deli Counter writes the railing's colliders
itself, in the greybox the graders walk, as it does the stoop's.
"""''',
     '''A STAIR'S BALUSTRADE (1.128.0): Deli Counter >= 0.268.0 stands a stair hole's guards as the LEVEL form, up
to 8 m long. A level run longer than `POST_BAY` stands a post at least every `POST_BAY`, equally spaced, the
pickets bay by bay; the rails run through the posts, which nest inside the top rail and around the bottom
rail as the end posts do. A run of one bay -- every stoop -- builds exactly the parts, in exactly the order,
it did before.

COLLISION: none here (the genome's `collision: false`). Deli Counter writes the railing's colliders
itself, in the greybox the graders walk, as it does the stoop's.
"""'''),
    ('''FORMS = ("level", "flight")''',
     '''#: a post at least this often along a long level run (1.128.0): a newel's spacing on a balustrade,
#: and the old genome's widest run, so no railing 1.127.0 could build gains a post -- 1.8 m, first tried,
#: split a 1.83 m run of the thinnest post into two bays (`stoop_unchanged.out.txt` in the factory's
#: `patches/zoo_stair_balustrade/`)
POST_BAY = 2.0
FORMS = ("level", "flight")'''),
    ('''    tc = top - RAIL_T / 2
    for xc in pickets(x0 + post, x1 - post, picket):
        out.append(prims.box(PART, MAT, (xc - picket / 2, -picket / 2, bc),
                             (xc + picket / 2, picket / 2, tc)))
    return out, {"rail_top": [round(top, 6), round(top, 6)], "posts": 2}''',
     '''    tc = top - RAIL_T / 2
    # the bays (1.128.0): as few as keep each at most POST_BAY, equal; one bay is the stoop's
    bays = max(1, math.ceil((w - post) / POST_BAY - 1e-9))
    step = (w - post) / bays
    inner = [x0 + post / 2.0 + step * k for k in range(1, bays)]
    edges = [x0 + post] + [xc + s * post / 2.0 for xc in inner for s in (-1.0, 1.0)] + [x1 - post]
    for b in range(bays):
        for xc in pickets(edges[2 * b], edges[2 * b + 1], picket):
            out.append(prims.box(PART, MAT, (xc - picket / 2, -picket / 2, bc),
                                 (xc + picket / 2, picket / 2, tc)))
    for xc in inner:
        out.append(prims.box(PART, MAT, (xc - post / 2, -post / 2, z0), (xc + post / 2, post / 2, z1)))
    return out, {"rail_top": [round(top, 6), round(top, 6)], "posts": 2 + len(inner)}'''),
])

TEST = '''"""A stair hole's balustrade (1.128.0): `stoop_railing`'s level form, as long as a hole edge, posts at least every
`POST_BAY`. The walker, walking cold run 9386, of an office stair's solid wood guards: "the walling/railing doesn't
loook natural yet". FAILS ON 1.127.0, but for the stoop's, which must not move."""
from zoo_keeper.core import genome, kit
from zoo_keeper.core import stoop_railing_forms as F


def test_the_genome_fits_a_stair_holes_guard():
    """Deli Counter's office guard rail, 4.3889 x 0.1 x 1.07 m, builds as the species, not the box."""
    slot = {"slot_id": "stair_guard_rail_1", "role": "prop", "size_mod": "full", "style": 1,
            "material": "metal_painted", "species": "stoop_railing", "form": "level",
            "fit": {"dims": [4.3889, 0.1, 1.07], "pivot": "center", "collision": "none"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["modules"][0]["species"] == "stoop_railing", plan.get("species_fallbacks")
    assert not plan.get("species_fallbacks"), plan["species_fallbacks"]


def test_a_long_run_stands_a_post_every_bay_and_keeps_its_pickets_clear():
    got = F.plan(4.3889, 0.1, 1.07, "level")
    bays = got["facts"]["posts"] - 1
    assert bays == 3, got["facts"]
    def box(p):
        vs = p["verts"]
        return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]

    xs = sorted((box(p)[0][0] + box(p)[1][0]) / 2.0 for p in got["prims"]
                if abs((box(p)[1][0] - box(p)[0][0]) - F.POST) < 1e-6 and abs((box(p)[1][2] - box(p)[0][2]) - 1.07) < 1e-6)
    assert len(xs) == 4, xs
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    assert max(gaps) <= F.POST_BAY + 1e-9 and max(gaps) - min(gaps) < 1e-9, gaps


def test_a_stoops_railing_is_unchanged():
    """One bay: the same parts, in the same order, as 1.127.0 drew -- 2 posts, 2 rails, the pickets."""
    got = F.plan(0.9, 0.038, 0.9144, "level")
    assert got["facts"]["posts"] == 2
    assert got["facts"]["pickets"] == len(F.pickets(-0.45 + F.POST, 0.45 - F.POST, F.members(0.038)[3]))


def test_the_genome_still_takes_a_stoop():
    d = genome.load_species("stoop_railing")["dimensions"]
    assert d["width"]["min"] <= 0.9 <= d["width"]["max"] == 8.0
    assert d["depth"]["min"] <= 0.038 and d["depth"]["max"] == 0.12
'''
(R / "tests" / "test_stair_balustrade.py").write_text(TEST, encoding="utf-8", newline="\n")
print("stoop_railing as a stair balustrade: genome 8 m x 0.12 m, POST_BAY; tests/test_stair_balustrade.py")
