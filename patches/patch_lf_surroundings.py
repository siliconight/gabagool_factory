"""Level Factory 0.175.0: the brief names what stands beyond the edge, or the archetype decides
(roadmap 228, step D's other half). See `lf_surroundings/CHANGELOG_0.175.0.md`.

Anchored edits, each asserted to match exactly once, nothing written until all of them did:
  packages/core/models.py               `MissionBrief.surroundings`
  packages/pipeline/site_variation.py   `SURROUNDINGS`, `surroundings_of`, `surroundings_known`
  apps/cli/commands/__init__.py         the site spec carries `surroundings` and
                                        `surroundings_resolved`, and the writer says so
  new  tests/unit/test_surroundings.py
CHANGELOG and VERSION from `CHANGELOG_0.175.0.md`.

    python patch_lf_surroundings.py --results-pending
    python patch_lf_surroundings.py --fill        fill the results from result_*.txt
    LF_ROOT=<copy> python patch_lf_surroundings.py --draft
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_surroundings"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.174.0", b"0.175.0"
CHANGELOG_HEAD = "## [0.174.0] - The backdrop beyond the plate's edge ships as MultiMeshes\n"

MODELS = "packages/core/models.py"
M_ANCHOR = "    theme: str = \"\"\n"
M_FIELD = (
    "    #: WHAT STANDS BEYOND THE PLATE'S EDGE (0.175.0, roadmap 228): `borough`,\n"
    "    #: `none`, `yards`, `parkland` or `roadside`, Lot's backdrop recipes. Empty,\n"
    "    #: the archetype and the site shape decide (`site_variation.surroundings_of`).\n"
    "    #: Not in the functional signature: the backdrop has no collision and\n"
    "    #: changes nothing a lock protects, like the weather.\n"
    "    surroundings: str = \"\"\n"
)

VARIATION = "packages/pipeline/site_variation.py"
V_ANCHOR = "    return _SHAPE_ALIASES.get(_norm(site_shape), \"row\")\n"
V_FUNCS = (
    "\n\n#: What stands beyond the plate's edge (0.175.0, roadmap 228): Lot's backdrop\n"
    "#: recipes, in `lot/site_backdrop.py`'s own words. `borough` is rows of\n"
    "#: rowhomes and a water tower, the walker's E; `none` lays nothing; the other\n"
    "#: three lay the borough with a finding until their kits exist.\n"
    "SURROUNDINGS = (\"borough\", \"none\", \"yards\", \"parkland\", \"roadside\")\n"
    "\n"
    "#: Unnamed, the archetype decides first and the site shape second. A table\n"
    "#: rather than a rule, stated so it can be argued with: a warehouse backs\n"
    "#: onto yards wherever it stands; a hospital onto parkland; a gas station or\n"
    "#: a convenience store on a strip onto the road; everything else onto the\n"
    "#: borough, which is what every level backed onto before this existed.\n"
    "_SURROUNDINGS_BY_ARCHETYPE = {\"industrial_warehouse\": \"yards\",\n"
    "                              \"county_hospital\": \"parkland\"}\n"
    "_SURROUNDINGS_BY_SHAPE = {\"yard\": \"yards\", \"campus\": \"parkland\"}\n"
    "_ROADSIDE_ARCHETYPES = (\"gas_station\", \"convenience_store\")\n"
    "\n"
    "\n"
    "def surroundings_known(asked) -> bool:\n"
    "    \"\"\"Whether ``asked`` is a recipe this table has an opinion about; the\n"
    "    empty string is known, it means derive.\"\"\"\n"
    "    return _norm(asked) in (\"\",) + SURROUNDINGS\n"
    "\n"
    "\n"
    "def surroundings_of(asked, archetype, site_shape) -> str:\n"
    "    \"\"\"The backdrop recipe a brief gets: the one it names, else the one its\n"
    "    archetype and site shape decide, else the borough. A spelling nobody\n"
    "    knows is the borough too, and `surroundings_known` says which.\"\"\"\n"
    "    want = _norm(asked)\n"
    "    if want in SURROUNDINGS:\n"
    "        return want\n"
    "    arch, shape = _norm(archetype), _norm(site_shape)\n"
    "    if arch in _SURROUNDINGS_BY_ARCHETYPE:\n"
    "        return _SURROUNDINGS_BY_ARCHETYPE[arch]\n"
    "    if arch in _ROADSIDE_ARCHETYPES and shape == \"strip\":\n"
    "        return \"roadside\"\n"
    "    return _SURROUNDINGS_BY_SHAPE.get(shape, \"borough\")\n"
)

CLI = "apps/cli/commands/__init__.py"
C_ANCHOR = "        \"site_shape\": model.site_shape,\n"
C_KEYS = (
    "        # WHAT STANDS BEYOND THE EDGE (0.175.0, roadmap 228): the recipe Lot's\n"
    "        # `site_backdrop` lays, named by the brief or decided by the archetype\n"
    "        # and the site shape, recorded as `site_shape` is below.\n"
    "        \"surroundings\": site_variation.surroundings_of(\n"
    "            model.surroundings, model.archetype, model.site_shape),\n"
    "        \"surroundings_resolved\": {\n"
    "            \"asked\": str(model.surroundings or \"\"),\n"
    "            \"got\": site_variation.surroundings_of(\n"
    "                model.surroundings, model.archetype, model.site_shape),\n"
    "            \"known\": site_variation.surroundings_known(model.surroundings),\n"
    "        },\n"
)
LAYER = "packages/exporting/backdrop_layer.py"
L_OLD = "            \"pos\": [float(x), float(y), float(dims[2]) / 2.0],\n"
L_NEW = (
    "            # a Zoo module stands on -h/2, so the centre is h/2 above the piece's\n"
    "            # foot, which Lot lifts with `z` for a container stacked on another\n"
    "            # (Lot 0.109.0's yards)\n"
    "            \"pos\": [float(x), float(y), float(p.get(\"z\") or 0.0) + float(dims[2]) / 2.0],\n"
)
NEW = {"tests/unit/test_surroundings.py": "test_surroundings.py"}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _text(rel):
    raw = (LF / rel).read_bytes()
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value)
        results[key] = value
    for path, rel in ((LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.175.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        path.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    print("Level Factory 0.175.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.175.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.175.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    text, eol = _text(MODELS)
    assert "surroundings" not in text, "already patched"
    text = _once(text, M_ANCHOR, M_ANCHOR + M_FIELD, "the theme field")
    writes[LF / MODELS] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(VARIATION)
    assert "surroundings_of" not in text, "already patched"
    text = _once(text, V_ANCHOR, V_ANCHOR + V_FUNCS, "shape_of's return")
    writes[LF / VARIATION] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(CLI)
    text = _once(text, C_ANCHOR, C_ANCHOR + C_KEYS, "the spec's site_shape key")
    writes[LF / CLI] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(LAYER)
    text = _once(text, L_OLD, L_NEW, "the backdrop order's position")
    writes[LF / LAYER] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        assert not (LF / rel).exists(), (rel, "already exists")
        writes[LF / rel] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl_text, cl_eol = _text("CHANGELOG.md")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    for p, data in writes.items():
        p.write_bytes(data)
    (LF / "CHANGELOG.md").write_bytes(
        (entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.174.0 -> 0.175.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
