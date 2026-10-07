"""Deli Counter 0.197.0 tests: open floor is a way in (L24's false positives).

    python patch_dc_open_plan_tests.py

Appends to `deli_counter/test_walk_reach.py`, anchored on its last test as
0.194.0 wrote it. Run BEFORE `patch_dc_open_plan.py`: all three must fail.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_walk_reach.py"

OLD_TAIL = '''def test_walk_baseline_has_not_gone_stale():
    lib = _library()
    gone = {k: [n for n in v if n not in lib.get(k, [])] for k, v in _frozen().items()}
    assert not {k: v for k, v in gone.items() if v}, gone
'''

NEW_TAIL = OLD_TAIL + '''

# ------------------------------------------------------- open floor (0.197.0)
# L24 shipped asking L12's graph, which joins rooms through openings, stairs
# and ladders only. deli_a01's basement partition along y = 1 stops at x 12,
# so the utility room's north edge from x 12 to 19 is open floor, and cold run
# 9189's bake walks across it on the street's island -- while L24 named the
# room "reachable only by breaching". Nine of the fifteen rooms 0.194.0 froze
# were open floor. tactical.build_graph has modelled it all along; the rule
# is now one function both ask.

def _open_plan(partition_end):
    """`_spec`'s two rooms, a breach between them, the partition between them
    covering their 10 m shared edge from y -5 to `partition_end`."""
    s = _spec("breach", breach_class="soft_wall")
    s["partitions"][0]["end"] = partition_end
    return s


def test_an_open_floor_edge_is_a_way_in():
    assert _walk(_open_plan(2.0)) == []            # 3 m of the edge uncovered
    assert _walk(_open_plan(4.5)) == ["back"]      # 0.5 m: a gap, not a way in


def test_lint_asks_tacticals_open_floor_rule(monkeypatch):
    import tactical
    monkeypatch.setattr(tactical, "shared_open_edge", lambda a, b, parts: False)
    assert _walk(_open_plan(2.0)) == ["back"]


def test_deli_a01s_utility_room_is_open_floor():
    spec = json.load(open(os.path.join(HERE, "specs", "deli_a01.json"), encoding="utf-8"))
    assert "utility_room" not in _walk(spec)
'''


def main():
    data = TEST.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(OLD_TAIL), "test_walk_reach.py no longer ends as 0.194.0 wrote it; refusing"
    assert "shared_open_edge" not in text
    TEST.write_bytes((text[:-len(OLD_TAIL)] + NEW_TAIL).encode("utf-8"))
    print("test_walk_reach.py: 3 tests appended")


if __name__ == "__main__":
    main()
