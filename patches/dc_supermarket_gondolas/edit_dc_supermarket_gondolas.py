"""Deli Counter 0.272.0 on a clone: a supermarket's aisles are gondolas too. Anchored; refuses on a miss.

    python edit_dc_supermarket_gondolas.py <clone>

Copies the migration and its test from `src/`, RUNS the migration (it rewrites specs/supermarket_a01.json and
supermarket_a03.json), narrows test_store_gondolas' "left alone" to the pharmacy, and updates prop_species' note.
"""
import pathlib
import shutil
import subprocess
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("migrations/migrate_supermarket_gondolas.py", "tests/test_supermarket_gondolas.py"):
    assert not (C / rel).exists(), rel
    shutil.copyfile(HERE / "src" / rel, C / rel)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("edited", rel, len(edits))


edit("tests/test_store_gondolas.py", [
    ('''def test_the_supermarkets_and_the_pharmacy_are_left_alone():
    for name in ("supermarket_a01", "supermarket_a03"):
        d = json.load(open(os.path.join(HERE, "specs", name + ".json"), encoding="utf-8"))
        assert any(v["name"].startswith("aisle_") for v in d["volumes"]), name
    assert prop_species.species_for_name("gondola_a") is None
''', '''def test_the_pharmacy_is_left_alone():
    # the supermarkets were left alone here until 0.272.0 (`test_supermarket_gondolas.py`)
    assert prop_species.species_for_name("gondola_a") is None
'''),
])

edit("prop_species.py", [
    ('''    # built as plain boxes; `migrate_store_gondolas.py` renames the other
    # stores' `aisle_N` and `aisle_shelf_N` to it. The supermarkets' `aisle_N`
    # and the pharmacy's `gondola_a/b` are not a snack aisle and stay.
''', '''    # built as plain boxes; `migrate_store_gondolas.py` renames the other
    # stores' `aisle_N` and `aisle_shelf_N` to it. The pharmacy's `gondola_a/b`
    # are not a snack aisle and stay. The supermarkets' `aisle_N` stayed boxes
    # too until 0.272.0 (`migrate_supermarket_gondolas.py`): the walker read the
    # five 14 m blocks down seed 9205's sales floor as dark and unfinished, and
    # they fit the species; grocery stock is a Zoo variant for later.
'''),
])

edit("migrate_slush_machine.py", [
    ('''def is_store(spec):
    rooms = {r.get("id") for r in spec.get("rooms") or []}
    return ROOM in rooms and any(str(v.get("name", "")).startswith("gondola_aisle")
                                 for v in spec.get("volumes") or [])
''', '''def is_store(spec):
    """A CONVENIENCE store: a sales floor whose aisles are snack gondolas -- and not a supermarket, whose aisles
    are gondolas too since 0.272.0 (`migrate_supermarket_gondolas.py`) but which takes no slush station, roller
    grill or window posters by this rule. The supermarkets' own cooler wall and glass front are their own
    decision, not this one's side effect."""
    rooms = {r.get("id") for r in spec.get("rooms") or []}
    if str(spec.get("name", "")).startswith("supermarket"):
        return False
    return ROOM in rooms and any(str(v.get("name", "")).startswith("gondola_aisle")
                                 for v in spec.get("volumes") or [])
'''),
])

done = subprocess.run([sys.executable, str(C / "migrations" / "migrate_supermarket_gondolas.py")], capture_output=True,
                      text=True, cwd=str(C))
print(done.stdout.strip())
assert done.returncode == 0 and "2 supermarket spec(s), 9 aisle(s) renamed" in done.stdout, done.stdout + done.stderr
