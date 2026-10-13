"""Level Factory 0.195.0: an Empty's stoop stands in the terrace's frontage (factory roadmap 240, with Deli
Counter 0.211.0's stoops).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  packages/pipeline/street_line.py   `STOOP_COLLIDERS`; `shell_extents(glb, skip=())`
  packages/pipeline/empties.py       a sentence in the docstring; `stoop_reach`
  apps/cli/commands/__init__.py      the terrace reads each Empty with the stoop skipped and reports a
                                     stoop that would reach past the frontage
  tests/unit/test_terrace_stoop.py   NEW (`lf_terrace_stoop/test_terrace_stoop.py.txt`)
CHANGELOG and VERSION from `lf_terrace_stoop/CHANGELOG_0.195.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written, in this session: `street_line.py` whole (`shell_extents`; the docstring's
reason a building's street edge is its furthest solid), `empties.py` whole (`FRONTAGE`, `terrace`,
`_turned`, `need`), the CLI's terrace block (`_ext`, `_empties`/`_sl` imported in it, the blockers'
`size_x`/`size_y` from the house extent), `glb_collision.Solid` (a `name`, axis-aligned hulls) and
`tests/unit/glb_fixture.write_glb`; and, in Deli Counter 0.211.0, `_stoop`'s collider names and
`presets.twin`'s `stoop_right` volume. Every file LF.

    python patches/patch_lf_terrace_stoop.py --results-pending
    (python -m pytest -q in level_factory; exit 0 and the tally, docs/COMMANDS.md trap 1)
    python patches/patch_lf_terrace_stoop.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_terrace_stoop"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_LIBRARY": "result_library.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.194.0", b"0.195.0"
CHANGELOG_HEAD = "## [0.194.0] - A site's overhead wires stay out of the lightmap"
SHA = {"packages/pipeline/street_line.py": "38695ac7207c4d80",
       "packages/pipeline/empties.py": "21b224835ff237e3",
       "apps/cli/commands/__init__.py": "b200a418ddfb6ab2"}
NEW = {"tests/unit/test_terrace_stoop.py": "test_terrace_stoop.py.txt"}

EDITS = {
    "packages/pipeline/street_line.py": [
        ("def shell_extents(glb_path):\n"
         "    \"\"\"``(x_min, x_max, y_min, y_max)`` of a shell's collider hulls about its\n"
         "    own origin, in site metres; None when the geometry cannot be read.\"\"\"\n"
         "    try:\n"
         "        from packages.validation import glb_collision\n"
         "    except ImportError:                       # pragma: no cover - packaging only\n"
         "        return None\n"
         "    reading = glb_collision.collision_solids(Path(glb_path))\n"
         "    if not reading.read or not reading.solids:\n"
         "        return None\n"
         "    x0 = min(s.centre[0] - s.size[0] / 2.0 for s in reading.solids)\n"
         "    x1 = max(s.centre[0] + s.size[0] / 2.0 for s in reading.solids)\n"
         "    z0 = min(s.centre[2] - s.size[2] / 2.0 for s in reading.solids)\n"
         "    z1 = max(s.centre[2] + s.size[2] / 2.0 for s in reading.solids)\n"
         "    return (x0, x1, -z1, -z0)\n",
         "#: Deli Counter 0.211.0's stoop colliders (`Builder._stoop`): the steps in\n"
         "#: front of a rowhome Empty's raised door. The terrace stands an Empty's FRONT\n"
         "#: FACE on its line and its stoop in the frontage before it -- the 2.0 m strip\n"
         "#: a Philadelphia stoop stands in (`empties.FRONTAGE`, factory roadmap 240) --\n"
         "#: so it leaves them out of the house's extent, and `empties.stoop_reach` holds\n"
         "#: them inside the strip. Named exactly: a twin's `stoop_right` volume is its\n"
         "#: own lot's, read with the building as a porch is.\n"
         "STOOP_COLLIDERS = (\"stoop_landing\", \"stoop_under_\", \"stoop_ramp\")\n"
         "\n"
         "\n"
         "def shell_extents(glb_path, skip=()):\n"
         "    \"\"\"``(x_min, x_max, y_min, y_max)`` of a shell's collider hulls about its\n"
         "    own origin, in site metres; None when the geometry cannot be read.\n"
         "    ``skip``: the name prefixes of colliders left out -- a part that stands in\n"
         "    front of the house rather than being it (`STOOP_COLLIDERS`, 0.195.0).\"\"\"\n"
         "    try:\n"
         "        from packages.validation import glb_collision\n"
         "    except ImportError:                       # pragma: no cover - packaging only\n"
         "        return None\n"
         "    reading = glb_collision.collision_solids(Path(glb_path))\n"
         "    if not reading.read or not reading.solids:\n"
         "        return None\n"
         "    solids = [s for s in reading.solids\n"
         "              if not any(s.name.startswith(p) for p in skip)]\n"
         "    if not solids:\n"
         "        return None\n"
         "    x0 = min(s.centre[0] - s.size[0] / 2.0 for s in solids)\n"
         "    x1 = max(s.centre[0] + s.size[0] / 2.0 for s in solids)\n"
         "    z0 = min(s.centre[2] - s.size[2] / 2.0 for s in solids)\n"
         "    z1 = max(s.centre[2] + s.size[2] / 2.0 for s in solids)\n"
         "    return (x0, x1, -z1, -z0)\n"),
    ],
    "packages/pipeline/empties.py": [
        ("gate reads. Placement here is plan metres; a building's street edge is read\n"
         "per side off its collider hulls (`street_line.shell_extents`), the same\n"
         "measure the near side's building line uses.\n",
         "gate reads. Placement here is plan metres; a building's street edge is read\n"
         "per side off its collider hulls (`street_line.shell_extents`), the same\n"
         "measure the near side's building line uses. A rowhome's STOOP is not its\n"
         "edge (0.195.0): it stands in the strip in front of the line, which is what\n"
         "the strip is for (`street_line.STOOP_COLLIDERS`, `stoop_reach`).\n"),
        ("            run_len = RUN[0] + next(stream) % (RUN[1] - RUN[0] + 1)\n"
         "    return out, need\n",
         "            run_len = RUN[0] + next(stream) % (RUN[1] - RUN[0] + 1)\n"
         "    return out, need\n"
         "\n"
         "\n"
         "def stoop_reach(whole, house):\n"
         "    \"\"\"How far a shell's stoop reaches in front of its house, metres: the\n"
         "    street edge (-y, unturned) of every collider (``whole``) less the house's\n"
         "    own (``house``, `street_line.STOOP_COLLIDERS` skipped); 0.0 for a shell\n"
         "    with none, None when either is unread. The terrace keeps it inside\n"
         "    `FRONTAGE` (0.195.0).\"\"\"\n"
         "    if whole is None or house is None:\n"
         "        return None\n"
         "    return round(max(0.0, house[2] - whole[2]), 4)\n"),
    ],
    "apps/cli/commands/__init__.py": [
        ("        _ext = {r[\"id\"]: _sl.shell_extents(r[\"glb\"]) for r in _empty_rows}\n",
         "        # A STOOP STANDS IN THE FRONTAGE (0.195.0): the house's front face on\n"
         "        # the line, read without its stoop (`STOOP_COLLIDERS`), and the stoop\n"
         "        # in the strip before it -- never past the strip onto the walk.\n"
         "        _ext = {r[\"id\"]: _sl.shell_extents(r[\"glb\"], skip=_sl.STOOP_COLLIDERS)\n"
         "                for r in _empty_rows}\n"
         "        for r in _empty_rows:\n"
         "            _reach = _empties.stoop_reach(_sl.shell_extents(r[\"glb\"]), _ext[r[\"id\"]])\n"
         "            if _reach and _reach > _empties.FRONTAGE:\n"
         "                print(f\"  EMPTY_STOOP_PAST_FRONTAGE: {r['id']}'s stoop reaches \"\n"
         "                      f\"{_reach:.2f} m in front of it and the terrace keeps \"\n"
         "                      f\"{_empties.FRONTAGE:.2f} m: it stands on the sidewalk\",\n"
         "                      file=sys.stderr)\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.195.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.195.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.195.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.195.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    for rel, data in news.items():
        (LF / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.194.0 -> 0.195.0")


if __name__ == "__main__":
    main()
