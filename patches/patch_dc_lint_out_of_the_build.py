"""Deli Counter 0.233.0: a shell build reads nothing from the layout lint (roadmap 259, its last residue).

0.229.0 left `layout_lint.py` out of `build_freshness.GEOMETRY_SOURCES` by decision, so a lint edit does not demand
a full rebuild, though stairwell asked it two things while building a shell: `_host_openings` (the door-like
openings on a host wall and where along it each centres) and `DOOR_APPROACH_M` (the floor a body needs before a
door). An edit to either could move a shell the gate did not see. Read off the call sites
(`docs/findings/build_freshness_259/call_sites.out.txt`), those two are the lint's only build-time readers: the
evidence report also calls the lint, and writes a report, not a shell; furnish (`level_design`) and stair_pitch
(through `presets._finish_stairs`, which the builder reaches only through `combat_audit`'s report) read its
findings when a SPEC is made, and a spec's own hash (`spec_sha256_16`) covers what that changes.

THE MOVE, one function and one number, no geometry: `host_openings` goes verbatim to `partition_bounds.py`, the
builder's and the lint's shared source of wall-span truth (watched since it was written); layout_lint keeps the old
name as an alias, so its own callers read the same function; stairwell asks `partition_bounds.host_openings` and
`agent_contract.door_approach()` -- the function `DOOR_APPROACH_M` was always computed from -- and imports the
lint nowhere. `NOT_BAKED` says so beside layout_lint's name, and the test that kept it out records that its premise
is true again.

What it changes (anchored; each file pinned by hash; nothing written on a miss; each file keeps its own endings):
  * partition_bounds.py (CRLF) -- `host_openings`, moved.
  * layout_lint.py -- the definition replaced by the alias.
  * stairwell.py -- two function-level `import layout_lint` gone; the two names asked of their sources.
  * build_freshness.py -- layout_lint's `NOT_BAKED` reason.
  * test_build_freshness.py -- the readers test's docstring: the refuted premise holds again.
  * test_lint_out_of_the_build.py (new, 3; two fail on 0.232.0): stairwell imports no lint; the two names are one
    function; and the number stairwell now asks the contract for is the lint's -- true before and after, pinned.
  * VERSION 0.232.0 -> 0.233.0, CHANGELOG.

AFTER APPLYING: `python build.py --all` (stairwell.py and partition_bounds.py are geometry sources) -- every record
must change its build time alone, the proof that nothing moved -- then the suite and the commit.

    python patches/patch_dc_lint_out_of_the_build.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_lint_out_of_the_build.py           # everything; the test again when it is this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
PINS = {
    "partition_bounds.py": "7b953b84b8987dae",
    "layout_lint.py": "46e14962f86b42cb",
    "stairwell.py": "75922402ff8522c9",
    "build_freshness.py": "b9b045f7b0c94945",
    "test_build_freshness.py": "9fd3fc51b82ffe94",
}

HOST_OPENINGS = '''def _host_openings(spec, host, is_ext):
    """(center_along, width, label) for the door-like openings on a host wall.

    Center math matches `_opening_xy` (the graph's convention): exterior
    `pos` is a centered fraction of the footprint on the wall's running
    axis; partition `pos` is a centered fraction of the (unclamped) span.
    Width defaults to 1.0, the same default the floorplan drawing uses.
    """
    hx, hy = spec["footprint_x"] / 2, spec["footprint_y"] / 2
    out = []
    for op in host.get("openings", []):
        if op.get("kind", "door") not in ("door", "garage", "breach"):
            continue
        w = float(op.get("width") or 1.0)
        if is_ext:
            face = host["wall"]
            along = op.get("pos", 0.0) * (spec["footprint_x"]
                                          if face in ("N", "S")
                                          else spec["footprint_y"])
        else:
            ax = str(host.get("axis", "X")).upper()
            s, e = host.get("start"), host.get("end")
            lo = -hx if ax == "X" else -hy
            hi = hx if ax == "X" else hy
            s = lo if s is None else s
            e = hi if e is None else e
            along = (s + e) / 2 + op.get("pos", 0.0) * (e - s)
        out.append((along, w, op.get("tag") or op.get("kind", "door")))
    return out
'''
LINT_ALIAS = '''# THE OPENINGS ON A HOST WALL LIVE IN `partition_bounds.host_openings`
# (0.233.0, the factory's roadmap 259). stairwell asked this lint for them
# while building a shell, which made the lint part of what a build is made
# of and a lint edit a move the freshness gate could not see. One function,
# two names: the lint's own callers read it here.
from partition_bounds import host_openings as _host_openings  # noqa: E402
'''
MOVED = '''

def host_openings(spec, host, is_ext):
    """(center_along, width, label) for the door-like openings on a host wall.

    MOVED HERE FROM `layout_lint._host_openings` (0.233.0, the factory's
    roadmap 259), verbatim: stairwell asks it where a stair can stand while
    building a shell, and this module is the builder's and the lint's shared
    source of wall-span truth, watched by `build_freshness`; the lint keeps
    the old name as an alias.

    Center math matches `_opening_xy` (the graph's convention): exterior
    `pos` is a centered fraction of the footprint on the wall's running
    axis; partition `pos` is a centered fraction of the (unclamped) span.
    Width defaults to 1.0, the same default the floorplan drawing uses.
    """
    hx, hy = spec["footprint_x"] / 2, spec["footprint_y"] / 2
    out = []
    for op in host.get("openings", []):
        if op.get("kind", "door") not in ("door", "garage", "breach"):
            continue
        w = float(op.get("width") or 1.0)
        if is_ext:
            face = host["wall"]
            along = op.get("pos", 0.0) * (spec["footprint_x"]
                                          if face in ("N", "S")
                                          else spec["footprint_y"])
        else:
            ax = str(host.get("axis", "X")).upper()
            s, e = host.get("start"), host.get("end")
            lo = -hx if ax == "X" else -hy
            hi = hx if ax == "X" else hy
            s = lo if s is None else s
            e = hi if e is None else e
            along = (s + e) / 2 + op.get("pos", 0.0) * (e - s)
        out.append((along, w, op.get("tag") or op.get("kind", "door")))
    return out
'''

STAIRWELL = [
    ("the first import", '''        if p["kind"] == "back":
            return []
        import layout_lint as _ll
        out = []
''', '''        if p["kind"] == "back":
            return []
        out = []
'''),
    ("the first openings", '''            for along, w, _label in _ll._host_openings(spec_dims, host,
                                                        False):
                if abs(along - p["pos"]) < w / 2.0 + T + band(p):
                    r = _ll.DOOR_APPROACH_M
''', '''            for along, w, _label in partition_bounds.host_openings(
                    spec_dims, host, False):
                if abs(along - p["pos"]) < w / 2.0 + T + band(p):
                    r = agent_contract.door_approach()
'''),
    ("the second import", '''        if p["kind"] != "back":
            return []
        import layout_lint as _ll
        import ladder_geom as _lg
''', '''        if p["kind"] != "back":
            return []
        import ladder_geom as _lg
'''),
    ("the second approach", '''        r_app = _ll.DOOR_APPROACH_M
''', '''        r_app = agent_contract.door_approach()
'''),
    ("the second openings", '''            for c, w, _label in _ll._host_openings(spec_dims, host, is_ext):
''', '''            for c, w, _label in partition_bounds.host_openings(spec_dims, host, is_ext):
'''),
]

BF_OLD = '''    # NOT ONLY A READER, AND KEPT OUT BY DECISION (a call made 2026-10-19 and
    # meant to be changed). stairwell asks its `_host_openings` and
    # `DOOR_APPROACH_M` where a stair can stand, and stair_pitch acts on its
    # findings, so an edit here can move a shell this gate does not see.
    # Watched, every lint edit would demand a full rebuild, which
    # `test_gates_that_only_read_shells_are_not_watched` refuses. Moving those
    # names into a geometry module would watch them without watching the lint.
    ("layout_lint.py", "a lint, kept out by decision though stairwell reads two of its names (roadmap 259)"),
'''
BF_NEW = '''    # A READER AGAIN (0.233.0). Until then stairwell asked it `_host_openings`
    # and `DOOR_APPROACH_M` while building a shell (0.229.0 kept it out by
    # decision regardless); they are `partition_bounds.host_openings` and
    # `agent_contract.door_approach()` now, both watched. Furnish and
    # stair_pitch read its findings when a spec is made, which the spec's own
    # hash covers, and the evidence report calls it beside the shell.
    ("layout_lint.py", "a lint; no build-time code reads it since 0.233.0, and what furnish and stair_pitch "
                       "take from it shapes specs, which their own hashes cover (roadmap 259)"),
'''

TBF_OLD = '''    NOT TRUE OF layout_lint, measured 2026-10-19 (0.229.0, the factory's
    roadmap 259): stairwell asks its `_host_openings` and `DOOR_APPROACH_M`
    where a stair can stand, and stair_pitch acts on its findings, so an edit
    there can move a shell the gate does not see. It stays unwatched by
    decision -- the cost above -- and `NOT_BAKED` says so beside its name;
    moving those names into a geometry module would watch them without
    watching the lint."""
'''
TBF_NEW = '''    NOT TRUE OF layout_lint, measured 2026-10-19 (0.229.0, the factory's
    roadmap 259): stairwell asked its `_host_openings` and `DOOR_APPROACH_M`
    where a stair can stand, so an edit there could move a shell the gate did
    not see. TRUE AGAIN SINCE 0.233.0: those are `partition_bounds.
    host_openings` and `agent_contract.door_approach()`, both watched, and
    stairwell imports no lint (`test_lint_out_of_the_build.py`); what furnish
    and stair_pitch take from it shapes specs, which their hashes cover."""
'''

TEST = r'''"""A shell build reads nothing from the layout lint (0.233.0, the factory's roadmap 259).

`build_freshness` keeps `layout_lint.py` out of its sources so a lint edit does not demand a rebuild. That held only
if no build-time code read the lint, and stairwell did: `_host_openings` and `DOOR_APPROACH_M`, asked where a stair
can stand. They are `partition_bounds.host_openings` (watched) and `agent_contract.door_approach()` (watched) now.

Run: python -m pytest -q test_lint_out_of_the_build.py
"""
import ast
from pathlib import Path

import agent_contract
import layout_lint
import partition_bounds

HERE = Path(__file__).resolve().parent


def test_stairwell_imports_no_lint():
    tree = ast.parse((HERE / "stairwell.py").read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    assert "layout_lint" not in names


def test_the_openings_are_one_function_under_two_names():
    assert layout_lint._host_openings is partition_bounds.host_openings


def test_the_approach_is_the_contracts():
    assert layout_lint.DOOR_APPROACH_M == agent_contract.door_approach()
'''

CHANGELOG = '''## [0.233.0] - a shell build reads nothing from the layout lint

**The factory's roadmap 259, its last residue.** 0.229.0 kept `layout_lint.py` out of `build_freshness`'s sources by
decision, so a lint edit does not demand a rebuild, though stairwell asked the lint two things while building a
shell: `_host_openings`, the door-like openings on a host wall, and `DOOR_APPROACH_M`, the floor a body needs before
a door. An edit to either could move a shell the gate did not see. Read off the call sites, those two were the
lint's only build-time readers: the evidence report writes a report, and furnish and stair_pitch read its findings
when a spec is made, which the spec's own hash covers.

### Changed
- `host_openings` moved verbatim to `partition_bounds.py`, the builder's and the lint's shared source of wall-span
  truth, watched since it was written; layout_lint keeps `_host_openings` as an alias, so its callers read the same
  function.
- stairwell asks `partition_bounds.host_openings` and `agent_contract.door_approach()`, the function
  `DOOR_APPROACH_M` was always computed from, and imports the lint nowhere.
- `build_freshness.NOT_BAKED` says layout_lint is a reader again; the readers test's docstring records its premise
  as true again.

### Added
- `test_lint_out_of_the_build.py` (3): two fail on 0.232.0; the third, that the contract's number is the
  lint's, holds before and after and pins the swap stairwell makes.

No geometry moves: rebuilt with `build.py --all`, every tracked build record changed its build time alone.

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(name):
    p = DC / name
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == PINS[name], (f"{name} is not the file this patch read", got)
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf == 0 or crlf == lf, f"{name} has mixed endings"
    eol = "\r\n" if crlf else "\n"
    return p, raw.decode("utf-8").replace("\r\n", "\n"), eol


def _write(p, text, eol):
    p.write_bytes(text.replace("\n", eol).encode("utf-8"))


def _test_plan():
    p = DC / "test_lint_out_of_the_build.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    return p


def write_tests(p=None):
    p = p or _test_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote deli_counter/test_lint_out_of_the_build.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    pb, pb_text, pb_eol = _read("partition_bounds.py")
    assert "def host_openings" not in pb_text, "already applied"
    assert pb_text.endswith("\n")
    pb_text = pb_text + MOVED
    ll, ll_text, ll_eol = _read("layout_lint.py")
    ll_text = _once(ll_text, HOST_OPENINGS, LINT_ALIAS, "layout_lint's _host_openings")
    sw, sw_text, sw_eol = _read("stairwell.py")
    for what, old, new in STAIRWELL:
        sw_text = _once(sw_text, old, new, "stairwell: " + what)
    assert "_ll." not in sw_text and "layout_lint" not in sw_text, "stairwell still reads the lint"
    bf, bf_text, bf_eol = _read("build_freshness.py")
    bf_text = _once(bf_text, BF_OLD, BF_NEW, "NOT_BAKED's layout_lint")
    tb, tb_text, tb_eol = _read("test_build_freshness.py")
    tb_text = _once(tb_text, TBF_OLD, TBF_NEW, "the readers test's docstring")
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.232.0", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.232.0]"), ctext[:40]
    plan = _test_plan()
    _write(pb, pb_text, pb_eol)
    _write(ll, ll_text, ll_eol)
    _write(sw, sw_text, sw_eol)
    _write(bf, bf_text, bf_eol)
    _write(tb, tb_text, tb_eol)
    v.write_text("Deli Counter 0.233.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Deli Counter 0.233.0 applied: host_openings in partition_bounds, stairwell reads no lint, NOT_BAKED, "
          "tests, VERSION, CHANGELOG -- now build.py --all (every record must change its build time alone)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
