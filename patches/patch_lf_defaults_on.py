"""Level Factory 0.144.0 source and tests: the Empties and the light bake ON by
default (the walker, 2026-10-05: "yes to both defaults"), plus the factory
root's cold-run recipe, which the bake default makes stale.

Every anchor must match exactly once in an LF file; every file is staged and
nothing is written until all of them matched. VERSION and CHANGELOG follow in
`patch_lf_defaults_on_release.py`, once the failing-test count and the suite
are measured.

    python patch_lf_defaults_on.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {}


def edit(path, old, new):
    EDITS.setdefault(path, []).append((old, new))


# --- packages/core/models.py: one rule for whether a terrace stands ---------

edit(LF / "packages/core/models.py",
     "\n\n@dataclass\nclass MissionBrief:\n",
     '''

#: The Empties' one word for "stand them" (0.137.0). Every other value leaves
#: the far side of the through road to the plate's edge.
EMPTIES_ACROSS = "across"


def empties_effective(empties, lot_library, building_count) -> str:
    """What a brief GETS, not what it says: `EMPTIES_ACROSS` when it asks
    for the Empties (the default since 0.144.0), has a lot library to draw
    them from and stands two or more buildings; `""` otherwise. One rule,
    read by `MissionBrief.functional_signature` and by
    `building_library.empties_for_brief`, so the lock and the site cannot
    disagree about whether a terrace stands."""
    if str(empties or "").strip().lower() != EMPTIES_ACROSS:
        return ""
    if not lot_library or int(building_count or 1) < 2:
        return ""
    return EMPTIES_ACROSS


@dataclass
class MissionBrief:
''')

edit(LF / "packages/core/models.py",
     '''    #: EMPTIES (0.137.0, roadmap 106): `"across"` stands a terrace of
    #: non-enterable shells along the far side of the through road,
    #: drawn from the lot library's Empties. Empty (the default) leaves
    #: the far side to the plate's edge, as every level before it.
    empties: str = ""
''',
     '''    #: EMPTIES (0.137.0, roadmap 106): `"across"` stands a terrace of
    #: non-enterable shells along the far side of the through road,
    #: drawn from the lot library's Empties. THE DEFAULT SINCE 0.144.0 (the
    #: walker, 2026-10-05: "yes to both defaults"). `"none"` -- or any word
    #: but `"across"`, the empty string included -- leaves the far side to
    #: the plate's edge, as every level before 0.137.0. A brief with no
    #: `lot_library`, or one building, stands no terrace whatever it says:
    #: `empties_effective` is the one rule.
    empties: str = EMPTIES_ACROSS
''')

edit(LF / "packages/core/models.py",
     '''        # the same care for the Empties (0.137.0): they stand on the site
        if self.empties:
            sig["empties"] = self.empties
        return sig
''',
     '''        # the same care for the Empties (0.137.0): they stand on the site.
        # Keyed on what the brief GETS since they became the default
        # (0.144.0): a brief with no library, or one building, stands no
        # terrace whatever it says and keeps the signature it always had --
        # a key there would break its lock to record nothing.
        empties = empties_effective(self.empties, self.lot_library, self.building_count)
        if empties:
            sig["empties"] = empties
        return sig
''')

# --- packages/pipeline/building_library.py: read the one rule --------------

edit(LF / "packages/pipeline/building_library.py",
     "from packages.pipeline.site_variation import stream\n",
     "from packages.core.models import EMPTIES_ACROSS, empties_effective\n"
     "from packages.pipeline.site_variation import stream\n")

edit(LF / "packages/pipeline/building_library.py",
     '''def empties_for_brief(model) -> list[dict]:
    """The Empties a brief asks for: every themeable one in its lot library
    when it sets `empties: across` and a varied lot, [] otherwise. ONE list
    for the planner (which fans their art jobs out), the compose rows and the
    site spec, the way `lot_for_brief` is one lot."""
    if str(getattr(model, "empties", "") or "").strip().lower() != "across":
        return []
    library = getattr(model, "lot_library", None)
    if not library or int(getattr(model, "building_count", 1) or 1) < 2:
        return []
    return empty_rows(library)
''',
     '''def empties_for_brief(model) -> list[dict]:
    """The Empties a brief gets: every themeable one in its lot library when
    `models.empties_effective` says a terrace stands -- `empties: across`,
    the default since 0.144.0, and a varied lot -- [] otherwise. ONE list
    for the planner (which fans their art jobs out), the compose rows and the
    site spec, the way `lot_for_brief` is one lot. A model with no `empties`
    attribute at all reads as the default."""
    library = getattr(model, "lot_library", None)
    if not empties_effective(getattr(model, "empties", EMPTIES_ACROSS), library,
                             getattr(model, "building_count", 1)):
        return []
    return empty_rows(library)
''')

# --- apps/cli/main.py: the export bakes unless told not to ------------------

edit(LF / "apps/cli/main.py",
     '''    sp.add_argument("--bake-lights", action="store_true",
                    help="bake the steady lights into a lightmap (needs a GPU and a display; "
                         "opens the Godot editor for about a minute)")
''',
     '''    # ON BY DEFAULT since 0.144.0 (the walker, 2026-10-05). `--bake-lights`
    # still parses, for the commands already written with it; a bake that
    # cannot run ships the package unbaked and says why in light_bake.json.
    sp.add_argument("--bake-lights", action=argparse.BooleanOptionalAction, default=True,
                    help="bake the steady lights into a lightmap -- the default. It needs "
                         "a GPU and a display, opens the Godot editor for about a minute, "
                         "and ships the package unbaked when it cannot; "
                         "--no-bake-lights skips it")
''')

# --- packages/exporting/export.py: the profile's default stays off ----------

edit(LF / "packages/exporting/export.py",
     '''    #: Bake the steady lights into a lightmap (0.131.0, roadmap item 31,
    #: `packages/exporting/light_bake.py`). Opt-in: it needs a GPU and a
    #: display, and opens the Godot editor for about a minute.
    bake_lights: bool = False
''',
     '''    #: Bake the steady lights into a lightmap (0.131.0, roadmap item 31,
    #: `packages/exporting/light_bake.py`). It needs a GPU and a display,
    #: and opens the Godot editor for about a minute. OFF HERE and ON at the
    #: command line since 0.144.0 (`apps/cli/main.py`): code that builds a
    #: profile, the tests among it, says what it wants, and a person running
    #: `export` gets the bake unless they pass --no-bake-lights.
    bake_lights: bool = False
''')

# --- tests -------------------------------------------------------------------

edit(LF / "tests/unit/test_empties_terrace.py",
     '''def test_a_brief_asks_for_empties_and_its_signature_says_so_only_then(tmp_path):
    lib = tmp_path / "build"
    lib.mkdir()
    for aid, facade in (("gs_empty_rowhome_a", True), ("gs_facade_rowhome", True),
                        ("gs_empty_rowhome_x", False)):
        for suf in (".glb", ".gameplay.json", ".slots.json"):
            (lib / f"{aid}{suf}").write_text("{}", encoding="utf-8")
        (lib / f"{aid}.validation.json").write_text(json.dumps({"facade": facade}), encoding="utf-8")
    plain = MissionBrief(mission_id="m", display_name="m", lot_library=str(lib), building_count=3)
    asked = MissionBrief(mission_id="m", display_name="m", lot_library=str(lib), building_count=3, empties="across")
    assert building_library.empties_for_brief(plain) == []
    # only the prefixed shell Deli Counter calls a facade
    assert [r["id"] for r in building_library.empties_for_brief(asked)] == ["gs_empty_rowhome_a"]
    assert "empties" not in plain.functional_signature()
    assert asked.functional_signature()["empties"] == "across"
''',
     '''def test_a_brief_gets_empties_unless_it_says_none_and_its_signature_follows(tmp_path):
    """0.144.0: the Empties are the default. Until then this test pinned the
    opt-in -- a brief that said nothing got no terrace. Now a silent brief
    gets one, `"none"` turns it off, and a brief with no library or one
    building gets none whatever it says, with a signature that says so, so
    its functional lock does not break to record nothing."""
    lib = tmp_path / "build"
    lib.mkdir()
    for aid, facade in (("gs_empty_rowhome_a", True), ("gs_facade_rowhome", True),
                        ("gs_empty_rowhome_x", False)):
        for suf in (".glb", ".gameplay.json", ".slots.json"):
            (lib / f"{aid}{suf}").write_text("{}", encoding="utf-8")
        (lib / f"{aid}.validation.json").write_text(json.dumps({"facade": facade}), encoding="utf-8")

    def brief(**kw):
        return MissionBrief(mission_id="m", display_name="m", **kw)

    for b in (brief(lot_library=str(lib), building_count=3),
              brief(lot_library=str(lib), building_count=3, empties="across")):
        # only the prefixed shell Deli Counter calls a facade
        assert [r["id"] for r in building_library.empties_for_brief(b)] == ["gs_empty_rowhome_a"]
        assert b.functional_signature()["empties"] == "across"
    for b in (brief(lot_library=str(lib), building_count=3, empties="none"),
              brief(lot_library=str(lib), building_count=3, empties=""),
              brief(building_count=3),
              brief(lot_library=str(lib), building_count=1),
              brief(building_count=3, empties="across")):
        assert building_library.empties_for_brief(b) == []
        assert "empties" not in b.functional_signature()
''')

edit(LF / "tests/unit/test_light_bake.py",
     '''def test_the_export_profile_does_not_bake_unless_asked():
    from packages.exporting.export import ExportProfile
    assert ExportProfile().bake_lights is False
''',
     '''def test_the_export_profile_does_not_bake_unless_asked():
    from packages.exporting.export import ExportProfile
    assert ExportProfile().bake_lights is False


def test_the_export_command_bakes_unless_told_not_to():
    """0.144.0: on at the command line, off in the profile (above)."""
    from apps.cli.main import build_parser
    parse = build_parser().parse_args
    assert parse(["export", "m"]).bake_lights is True
    # the spelling every cold run before 0.144.0 used still parses
    assert parse(["export", "m", "--bake-lights"]).bake_lights is True
    assert parse(["export", "m", "--no-bake-lights"]).bake_lights is False
''')

# --- the factory root's cold-run recipe --------------------------------------

edit(ROOT / "docs/COMMANDS.md",
     "    EXPORT_FLAGS=--bake-lights bash tools/cold_drive/cold_drive.sh <N> <PREV> <mission> <seed|auto> > docs/cold_runs/cold_<N>/driver.log 2>&1\n",
     "    bash tools/cold_drive/cold_drive.sh <N> <PREV> <mission> <seed|auto> > docs/cold_runs/cold_<N>/driver.log 2>&1\n")

edit(ROOT / "docs/COMMANDS.md",
     "\n- **What the driver does.** It stops at the first failing leg and keeps the\n",
     '''
- **The export bakes the lights by default** (Level Factory 0.144.0).
  `EXPORT_FLAGS=--no-bake-lights` skips the bake. Runs before 0.144.0
  passed `EXPORT_FLAGS=--bake-lights`, which still parses.
- **A mission whose last run's workspace is gone.** `stage_batch.py`
  copies `batch.json` and `briefs/` out of `docs/cold_runs/cold_<PREV>`, so
  stage from the mission's own last run. Then drive with `<PREV>` set to the
  newest workspace that still exists. The driver copies
  `workspaces/cold-<PREV>-ws/tools.local.json` and stops without it, and
  its findings diff against a different mission reads as an empty count.
- **What the driver does.** It stops at the first failing leg and keeps the
''')

edit(ROOT / "tools/cold_drive/cold_drive.sh",
     '''#   EXPORT_FLAGS=--bake-lights bash tools/cold_drive/cold_drive.sh <N> <PREV> <mission> <seed|auto> \\
#       > docs/cold_runs/cold_<N>/driver.log 2>&1
''',
     '''#   bash tools/cold_drive/cold_drive.sh <N> <PREV> <mission> <seed|auto> \\
#       > docs/cold_runs/cold_<N>/driver.log 2>&1
#
# The export bakes the lights by default since Level Factory 0.144.0;
# EXPORT_FLAGS=--no-bake-lights skips it.
''')


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        assert b"\r\n" not in data, f"{path}: CRLF, and every anchor here is LF"
        text = data.decode("utf-8")
        for old, new in pairs:
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
