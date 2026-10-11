"""Deli Counter 0.209.1: a stair's column ends at the ceiling of the top floor it serves (cold run
9245's eight roof-props conflicts, every one a prop two slabs above a stair).

Anchored edits in `circulation.py` (`stair_column`, read off the stair's own landings;
`circulation_volumes` bounds every stair by it) and `test_circulation.py` (three tests, one failing
on 0.209.0); each file pinned by hash and each anchor asserted once, nothing written on a miss;
the files' own line endings kept. Applies on 0.209.0. CHANGELOG and VERSION from
`dc_stair_column/CHANGELOG_0.209.1.md`; `--results-pending` leaves RESULT_SUITE and RESULT_PACKAGE
to `--fill`. No library rebuild: nothing a shell ships changes.

    python patches/patch_dc_stair_column.py --results-pending && cd deli_counter && python -m pytest -q
    python docs/findings/roof_props/regate_9245.py
    python patches/patch_dc_stair_column.py --fill
    DC_ROOT=<copy> python patches/patch_dc_stair_column.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_stair_column"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_PACKAGE": "result_package.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.209.0", b"Deli Counter 0.209.1"
CHANGELOG_HEAD = ("## [0.209.0] - a roof slot says where a body steps off a ladder, and a building "
                  "carries a roof-props layer\n")
CIRC = "circulation.py"
TESTS = "test_circulation.py"
SHA = {CIRC: "44b019a36cd2596a", TESTS: "34c49b0941b729e1"}

C_DEF_OLD = "\n\ndef circulation_volumes(slots_manifest, gameplay):\n"
C_DEF_NEW = ("\n\n"
             "#: A stair's column reaches one storey above its upper landing -- the ceiling\n"
             "#: of the top floor it serves -- and no further (0.209.1). It used to reach\n"
             "#: +/-1e6: a prop anywhere over the footprint, on any floor, was \"in the\n"
             "#: shaft\". Cold run 9245's roof props found it: seven HVAC parts on the\n"
             "#: office's roof over `office_stair_0` (floors 0 to 2, the roof two slabs up)\n"
             "#: and a dish on the deli's over its BASEMENT stair -- eight conflicts, none a\n"
             "#: body could meet. The storey is read off the stair's own landings, so no\n"
             "#: manifest field is guessed; a stair without `nav_endpoints` keeps the full\n"
             "#: column, as before.\n"
             "def stair_column(system):\n"
             "    \"\"\"``(z_lo, z_hi)`` of a stair system's column, Blender z: from its lowest\n"
             "    landing to one storey above its highest, the storey being the landings'\n"
             "    rise over the floors they span. ``(-1e6, 1e6)`` without endpoints.\"\"\"\n"
             "    ends = system.get(\"nav_endpoints\") or {}\n"
             "    zs = []\n"
             "    for key in (\"lower\", \"upper\"):\n"
             "        pt = ends.get(key)\n"
             "        if isinstance(pt, (list, tuple)) and len(pt) >= 3:\n"
             "            try:\n"
             "                zs.append(float(pt[2]))\n"
             "            except (TypeError, ValueError):\n"
             "                pass\n"
             "    if len(zs) < 2 or zs[0] == zs[1]:\n"
             "        return -1e6, 1e6\n"
             "    z_lo, z_hi = min(zs), max(zs)\n"
             "    floors = system.get(\"floors_served\") or []\n"
             "    try:\n"
             "        spanned = max(1, int(max(floors)) - int(min(floors)))\n"
             "    except (TypeError, ValueError):\n"
             "        spanned = 1\n"
             "    return z_lo, z_hi + (z_hi - z_lo) / spanned\n"
             "\n\n"
             "def circulation_volumes(slots_manifest, gameplay):\n")
C_LOOP_OLD = ("    for st in ((gameplay or {}).get(\"stair_systems\") or []):\n"
              "        v = stair_volume(st)\n"
              "        if v:\n"
              "            vols.append((f\"stair:{st.get('id')}\", v))\n"
              "    return vols\n")
C_LOOP_NEW = ("    for st in ((gameplay or {}).get(\"stair_systems\") or []):\n"
              "        # the floors it serves, one storey of headroom above (0.209.1)\n"
              "        v = stair_volume(st, *stair_column(st))\n"
              "        if v:\n"
              "            vols.append((f\"stair:{st.get('id')}\", v))\n"
              "    return vols\n")

T_ADD = '''

# ---- 0.209.1: the column ends at the top floor's ceiling ----------------------

def _served(**kw):
    """A stair serving floors 0 to 2 of a 3.6 m building: landings at 0.0 and 7.2."""
    return _stair(floors_served=[0, 1, 2],
                  nav_endpoints={"lower": [5.0, 4.5, 0.0], "upper": [6.0, 5.5, 7.2]}, **kw)


def test_a_stairs_column_reaches_one_storey_above_its_upper_landing():
    """FAILS ON 0.209.0: the column was +/-1e6 whatever the stair served."""
    assert C.stair_column(_served()) == (0.0, 7.2 + 3.6)
    vols = dict(C.circulation_volumes({}, {"stair_systems": [_served()]}))
    lo, hi = vols["stair:stair_0"]
    assert lo[2] == 0.0 and abs(hi[2] - 10.8) < 1e-9


def test_a_roof_prop_over_a_stair_two_slabs_down_is_not_in_its_column():
    """Cold run 9245's office: HVAC units on a roof at 10.8 m over a stair
    serving floors 0 to 2 read as seven conflicts. Prop boxes are in Godot
    space (x, up, -y): a unit standing ON the roof grazes the column's top
    face by nothing, under the 2 cm floor; a table in the well is caught."""
    vols = C.circulation_volumes({}, {"stair_systems": [_served()]})
    on_roof = [("Hvac#0", ([4.5, 10.8, -5.5], [6.5, 11.7, -4.5]))]
    in_well = [("Table#0", ([4.5, 5.0, -5.5], [6.5, 6.0, -4.5]))]
    assert C.prop_conflicts(on_roof, vols) == []
    assert [c["prop"] for c in C.prop_conflicts(in_well, vols)] == ["Table#0"]


def test_a_stair_without_endpoints_keeps_the_full_column():
    assert C.stair_column(_stair(floors_served=[0, 1])) == (-1e6, 1e6)
    vols = dict(C.circulation_volumes({}, {"stair_systems": [_stair()]}))
    assert vols["stair:stair_0"][1][2] == 1e6
'''


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = DC / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.209.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.209.1: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.209.1.md")
    assert entry.startswith("## [0.209.1] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"

    cp, c_eol, circ = _read(CIRC)
    assert "def stair_column" not in circ, "already applied"
    circ = _once(circ, C_DEF_OLD, C_DEF_NEW, "stair_column before circulation_volumes")
    circ = _once(circ, C_LOOP_OLD, C_LOOP_NEW, "the stair loop")

    tp, t_eol, tests = _read(TESTS)
    tests = tests.rstrip("\n") + "\n" + T_ADD

    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:140]
    # every anchor matched: now write
    _write(cp, c_eol, circ)
    _write(tp, t_eol, tests)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.209.0 -> 0.209.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
