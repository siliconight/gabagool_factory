"""Level Factory 0.144.3: the price probe counts the tree as it is, not as it
was at load.

The breadth sweep's close-out could not price county_hospital_001 (cold run
9173's package): `perf_stations.gd` went silent after its sightline line and
quit on its 600 s watchdog with nothing measured, twice. The level itself ran
300 frames in 2.8 s (`frame_clock.gd`), and a debug copy of the probe showed
the real cause:

    [dbg] draw-call check 0: 378
    [dbg] counting 6444 node(s)
    SCRIPT ERROR: Left operand of 'is' is a previously freed instance.

The probe walks the scene once, at load, and reads that list after seventy
frames. The hospital's warm-up frees its own nodes by then; `is` on a freed
instance is a script error, the probe's coroutine dies, and nothing is left to
quit but the watchdog.

    python patch_lf_perf_rewalk.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

GD_OLD = """\tvar n_mesh: int = 0
\tvar n_multi: int = 0
\tfor n in nodes:
"""
GD_NEW = """\t# THE TREE AS IT IS NOW, not as it was at load (0.144.3). A level's
\t# warm-up frees its own nodes when it is done -- county_hospital_001's
\t# within the first seventy frames -- and the list walked at load then
\t# holds freed instances. `is` on one is a script error, the coroutine
\t# dies, and the probe idles until its watchdog with nothing measured:
\t# cold run 9173's package, twice, read as a 600 s stall while the level
\t# itself ran 300 frames in 2.8 s. The light census below reads this list
\t# too, with no frame between.
\tnodes = []
\t_walk(scene, nodes)
\tvar n_mesh: int = 0
\tvar n_multi: int = 0
\tfor n in nodes:
"""

TEST = '''"""The price probe counts the scene as it is when it counts (0.144.3).

`perf_stations.gd` walked the scene once, at load, and read that list after
seventy frames of rendering. county_hospital_001's warm-up frees its own nodes
in that time; `is` on a freed instance is a script error, the probe's
coroutine died, and it idled until its 600 s watchdog with nothing measured --
twice, on cold run 9173's package, while the level ran 300 frames in 2.8 s.

The probe cannot run here (no Godot in the suite), so this pins the order in
its source: the tree is walked again after the last frame the probe waits on
and before the mesh count and the light census read it.

Run:  python -m pytest tests/unit/test_perf_rewalk.py -q
"""
from pathlib import Path

PROBE = Path(__file__).resolve().parents[2] / "tools" / "perf_stations.gd"


def test_the_tree_is_walked_again_between_the_last_wait_and_the_count():
    src = PROBE.read_text(encoding="utf-8")
    last_wait = src.index("var drew := false")       # the draw-call check
    count = src.index("var n_mesh: int = 0")
    census = src.index("_light_census(nodes, cap)")
    between = src[last_wait:count]
    assert "_walk(scene, nodes)" in between, (
        "the mesh count reads the list walked at load, after frames in which "
        "a level can free its own nodes")
    assert last_wait < count < census
    # and no frame passes between the fresh walk and the census that reads it
    assert "await" not in src[count:census]
'''

EDITS = {LF / "tools/perf_stations.gd": [(GD_OLD, GD_NEW)]}
NEW_FILES = {LF / "tests/unit/test_perf_rewalk.py": TEST}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in NEW_FILES.items():
        assert not path.exists(), f"{path} already exists"
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
