"""Deli Counter 0.229.0: the build freshness gate watches every module a build writes with (factory roadmap 259).

`build_freshness.GEOMETRY_SOURCES` is the commit hook's whole idea of what a built shell is made of, and Level
Factory's library guard parses the same tuple (`building_library._geometry_sources`, `ast.literal_eval`).
Measured on 0.228.0 (`docs/findings/build_freshness_259/`): following AST imports from build.py and
deli_counter.py, a build reaches 54 of Deli Counter's modules; the tuple named 23, 22 of them reached. Of the 32
unlisted, read off their call sites, 21 put their output into what a build writes, and `agent_contract.json` --
body sizes and every clearance derived from them -- was named nowhere.

THE CALL, made 2026-10-19 and meant to be changed:
  * 20 of the 21 and `agent_contract.json` join the tuple, which stays a literal.
  * `layout_lint.py`, the 21st, stays OUT, as `test_gates_that_only_read_shells_are_not_watched` already holds
    it: a lint edit must not demand a full rebuild, which trains people to ignore the gate. It is not only a
    reader -- stairwell asks its `_host_openings` and `DOOR_APPROACH_M` where a stair can stand, and stair_pitch
    acts on its findings -- so that test's docstring gains the refutation of its premise, and the way to watch
    those names without the lint: move them into a geometry module.
  * `NOT_BAKED` (new, a literal): the 12 a build reaches that are kept out, each with why.
  * `test_freshness_sources.py` walks the build's imports and fails on a module in neither list, so the next
    module the builder imports is classified the day it lands.

No rebuild: measured before writing, every one of the 157 judged shells (built 09:47:47 onward) is newer than
the newest source added (level_design.py, 09:45:29), and the patch touches no source's time.

What it changes (anchored; each file pinned by hash; nothing written on a miss; LF-safe):
  * build_freshness.py -- the tuple's 21 new entries; `NOT_BAKED`.
  * test_build_freshness.py -- the refutation in `test_gates_that_only_read_shells_are_not_watched`'s docstring.
  * test_freshness_sources.py (new, 5 tests; 4 fail on 0.228.0 -- the fifth pins that the tuple is a literal
    naming files, which holds before and after).
  * VERSION 0.228.0 -> 0.229.0, CHANGELOG.

    python patches/patch_dc_freshness_sources.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_freshness_sources.py           # everything; the test again when it is this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
BF = DC / "build_freshness.py"
BF_SHA = "4b766d1118fe9702"
TBF = DC / "test_build_freshness.py"
TBF_SHA = "2db05d76f2ac33f7"

TUPLE_OLD = '''    # the roof hatch slot and its interactive, one per hatch link on the roof (0.224.0)
    "roof_hatch.py",
)
'''
TUPLE_NEW = '''    # the roof hatch slot and its interactive, one per hatch link on the roof (0.224.0)
    "roof_hatch.py",
    # EVERY OTHER MODULE A BUILD REACHES WHOSE OUTPUT IT WRITES (0.229.0, the
    # factory's roadmap 259). Until 0.228.0 this tuple named 23 sources while a
    # build reached 54 of this repo's modules, and 21 of the unlisted ones shape
    # what a build writes -- read off their call sites, not measured one edit at
    # a time. `test_freshness_sources.py` walks the build's imports and fails on
    # a module in neither this tuple nor `NOT_BAKED`. Listing one that bakes
    # nothing only asks for a rebuild nobody needed: the safe direction.
    "agent_contract.py",    # body sizes: stair landings, door widths, the vault aperture
    "agent_contract.json",  # ... and the numbers, the one data file a build reads
    "ledge_cover.py",       # whether a vault ledge draws its own box (0.227.0)
    "level_design.py",      # club rooms and the business id; lights' bar aisle
    "material_kind.py",     # each surface's skin kind
    "prop_species.py",      # a prop's species, long axis and collision owner
    "rarity.py",
    "setbacks.py",          # every storey's extent
    "skin_style.py",
    "stair_pitch.py",       # presets lengthen a flight and clear its walls with it
    "stoop.py",             # an Empty's stoop (0.211.0)
    "tactical.py",          # the room under a point and the room graph: ladders, stairs
    "tscn_export.py",       # the shell's .tscn
    "vault_room.py",        # a vault's slot and bearing faces
    "zoo_export.py",
    # the migrations presets call while they write a spec
    "migrate_furnish_recipes.py",
    "migrate_roller_grill.py",
    "migrate_slush_machine.py",
    "migrate_wall_crossing.py",
    "migrate_window_poster.py",
    "migrate_window_sign.py",
)

# THE MODULES A BUILD REACHES THAT ARE KEPT OUT OF `GEOMETRY_SOURCES`, each
# with why (0.229.0, the factory's roadmap 259). `test_freshness_sources.py`
# holds every module the build imports to one list or the other. A literal,
# like the tuple, so a reader can parse it without importing this repo.
NOT_BAKED = (
    ("circulation.py", "a reader: the composer's circulation gate; layout_lint reads one prefix from it"),
    ("zfight_gate.py", "a reader: the z-fight gate over built GLBs"),
    ("evidence.py", "writes the validation, combat-audit and navigation reports beside a shell; "
                    "no tool outside this repo reads them"),
    ("combat_audit.py", "a gate evidence.py reports"),
    ("enterability.py", "a gate evidence.py and validate.py report"),
    ("guards.py", "a gate evidence.py and validate.py report"),
    ("navigability.py", "a gate evidence.py and validate.py report"),
    ("pvp_heist.py", "a gate evidence.py and validate.py report"),
    ("sightlines.py", "an analysis evidence.py and validate.py report"),
    ("validate.py", "the spec validator; evidence.py reports its schema check"),
    ("polybudget.py", "an estimate validate.py prints"),
    # NOT ONLY A READER, AND KEPT OUT BY DECISION (a call made 2026-10-19 and
    # meant to be changed). stairwell asks its `_host_openings` and
    # `DOOR_APPROACH_M` where a stair can stand, and stair_pitch acts on its
    # findings, so an edit here can move a shell this gate does not see.
    # Watched, every lint edit would demand a full rebuild, which
    # `test_gates_that_only_read_shells_are_not_watched` refuses. Moving those
    # names into a geometry module would watch them without watching the lint.
    ("layout_lint.py", "a lint, kept out by decision though stairwell reads two of its names (roadmap 259)"),
)
'''

TEST_DOC_OLD = '''    """nav_gate/zfight_gate/circulation re-run against whatever is present;
    editing them does not make a shell stale. Listing them would demand a
    full rebuild every time a checker changed, which trains people to ignore
    the gate."""
'''
TEST_DOC_NEW = '''    """nav_gate/zfight_gate/circulation re-run against whatever is present;
    editing them does not make a shell stale. Listing them would demand a
    full rebuild every time a checker changed, which trains people to ignore
    the gate.

    NOT TRUE OF layout_lint, measured 2026-10-19 (0.229.0, the factory's
    roadmap 259): stairwell asks its `_host_openings` and `DOOR_APPROACH_M`
    where a stair can stand, and stair_pitch acts on its findings, so an edit
    there can move a shell the gate does not see. It stays unwatched by
    decision -- the cost above -- and `NOT_BAKED` says so beside its name;
    moving those names into a geometry module would watch them without
    watching the lint."""
'''

TEST = r'''"""Every module a shell build reaches is a geometry source or is named as kept out (0.229.0, the factory's
roadmap 259).

`build_freshness.GEOMETRY_SOURCES` is the whole idea, for this repo's commit hook and for Level Factory's guard
that parses the same tuple, of what a built shell is made of. Until 0.228.0 it named 23 sources while a build
reached 54 of this repo's modules, 21 of the unlisted ones shaping what a build writes, so a change to one of
them passed the hook with every shell older than the code that makes it. This walks the build's imports the way
the factory's `docs/findings/build_freshness_259/freshness_imports.py` measured them -- AST imports, top-level
and inside functions, followed from build.py and deli_counter.py through this repo's modules -- and fails on a
module in neither `GEOMETRY_SOURCES` nor `NOT_BAKED`. Both are read the way Level Factory reads the tuple: parsed
with `ast`, never imported.

Run: python -m pytest -q test_freshness_sources.py
"""
import ast
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRIES = ("build", "deli_counter")


def _literal(name):
    tree = ast.parse(open(os.path.join(HERE, "build_freshness.py"), encoding="utf-8").read())
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            return ast.literal_eval(node.value)
    raise AssertionError("build_freshness.py assigns no literal %s" % name)


def _reached():
    local = {f[:-3] for f in os.listdir(HERE) if f.endswith(".py")}
    seen, todo = set(), list(ENTRIES)
    while todo:
        mod = todo.pop()
        if mod in seen:
            continue
        seen.add(mod)
        tree = ast.parse(open(os.path.join(HERE, mod + ".py"), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module.split(".")[0]]
            else:
                continue
            todo.extend(n for n in names if n in local)
    return seen


def test_the_sources_are_a_literal_that_names_files():
    sources = _literal("GEOMETRY_SOURCES")
    assert isinstance(sources, tuple) and sources
    missing = [s for s in sources if not os.path.isfile(os.path.join(HERE, s))]
    assert not missing, missing


def test_every_module_a_build_reaches_is_classified():
    sources = set(_literal("GEOMETRY_SOURCES"))
    kept_out = {name for name, _why in _literal("NOT_BAKED")}
    reached = _reached()
    assert len(reached) > 20, reached        # the walk found the build, not an empty graph
    unclassified = sorted(m + ".py" for m in reached if m + ".py" not in sources | kept_out)
    assert not unclassified, "reached by a build, in neither GEOMETRY_SOURCES nor NOT_BAKED: %s" % unclassified


def test_no_module_is_in_both():
    both = sorted(set(_literal("GEOMETRY_SOURCES")) & {name for name, _why in _literal("NOT_BAKED")})
    assert not both, both


def test_each_module_kept_out_says_why():
    for name, why in _literal("NOT_BAKED"):
        assert name.endswith(".py") and os.path.isfile(os.path.join(HERE, name)), name
        assert isinstance(why, str) and len(why) > 10, name


def test_the_agent_contract_is_a_source():
    # the one data file a build reads: body sizes and every clearance derived from them
    assert "agent_contract.json" in _literal("GEOMETRY_SOURCES")
'''

CHANGELOG = '''## [0.229.0] - the freshness gate watches every module a build writes with

**The factory's roadmap 259.** `build_freshness.GEOMETRY_SOURCES` is this repo's commit hook's whole idea of
what a built shell is made of, and Level Factory's library guard parses the same tuple. Measured on 0.228.0 by
following the build's imports (AST, from build.py and deli_counter.py): a build reaches 54 of this repo's
modules and the tuple named 23, 22 of them reached -- `ladder_place.py` is named on the build path only in
comments. Of the 32 unlisted, 21 put their output into what a build writes, read off their call sites, and
`agent_contract.json` was a source no tuple named. A commit changing only one of them passed the hook with
every shell older than the code that makes it.

**The call, made 2026-10-19 and meant to be changed:** 20 of the 21 and the contract are watched; `layout_lint`
is not (below).

### Changed
- `GEOMETRY_SOURCES` gains 20 modules and `agent_contract.json`: agent_contract, ledge_cover, level_design,
  material_kind, prop_species, rarity, setbacks, skin_style, stair_pitch, stoop, tactical, tscn_export,
  vault_room, zoo_export, and the six migrations presets call. Still a literal.
- No rebuild: every judged shell was built after the newest source added.

### Added
- `NOT_BAKED`, a literal: the 12 modules a build reaches that are kept out, each with why -- circulation,
  zfight_gate, evidence and the eight gates and reports it calls, and layout_lint.
- `test_freshness_sources.py` (5): every module a build reaches is in one list or the other; the tuple is a
  literal naming files; no module is in both; each kept out says why; the contract is a source. Four fail on
  0.228.0.

### Not done, by decision
- `layout_lint.py` stays unwatched, as `test_gates_that_only_read_shells_are_not_watched` holds it: a lint edit
  must not demand a rebuild. That test's premise is refuted in its docstring. stairwell asks layout_lint's
  `_host_openings` and `DOOR_APPROACH_M` where a stair can stand and stair_pitch acts on its findings, so an
  edit there can move a shell unseen. Moving those names into a geometry module would watch them without
  watching the lint.

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _pinned(path, want):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, f"{path.name} is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == want, (f"{path.name} is not the file this patch read", got)
    return raw.decode("utf-8")


def _test_plan():
    p = DC / "test_freshness_sources.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    return p


def write_tests(p=None):
    p = p or _test_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote deli_counter/test_freshness_sources.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    bf = _pinned(BF, BF_SHA)
    assert "NOT_BAKED" not in bf, "already applied"
    bf = _once(bf, TUPLE_OLD, TUPLE_NEW, "the tuple's end")
    tbf = _pinned(TBF, TBF_SHA)
    tbf = _once(tbf, TEST_DOC_OLD, TEST_DOC_NEW, "the readers test's docstring")
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.228.0", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.228.0]"), ctext[:40]
    plan = _test_plan()
    BF.write_bytes(bf.encode("utf-8"))
    TBF.write_bytes(tbf.encode("utf-8"))
    v.write_text("Deli Counter 0.229.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Deli Counter 0.229.0 applied: GEOMETRY_SOURCES +21, NOT_BAKED, test_freshness_sources.py, the readers "
          "test's refutation, VERSION, CHANGELOG -- no rebuild needed; the suite, build_freshness.py, then commit")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
