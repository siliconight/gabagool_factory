"""Level Factory 0.137.0: Empties across the street.

Roadmap 106, the walker 2026-10-04: Empties stand around the walkable level
and across its streets. Deli Counter 0.174.0 builds the rowhome family with
real fronts; this places a terrace of them along the far side of the through
road, as Lot `blockers`, themed through the same art pipeline as the lot's
buildings.

New: `packages/pipeline/empties.py` and `tests/unit/test_empties_terrace.py`
copied from `lf_empties/`. Anchored edits (every anchor once; refuses on a
miss):
  packages/core/models.py              `empties` on the brief, in the
                                       functional signature only when set
  packages/pipeline/building_library.py  `EMPTY_PREFIX`, `empty_rows`,
                                       `empties_for_brief`
  packages/pipeline/planner.py         an Empty's art jobs: kit, Patina,
                                       dressing -- no fixtures, it has no lights
  apps/cli/commands/__init__.py        the compose rows carry the Empties; the
                                       site spec places the terrace
CHANGELOG and VERSION from `lf_empties/CHANGELOG_0.137.0.md`.

    python patch_lf_empties.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_empties"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


LIB = '''

#: EMPTIES (0.137.0): Deli Counter's non-enterable shells with real fronts
#: (roadmap 106; Deli Counter 0.174.0 builds the rowhome family), by the id
#: prefix it gives them. `gs_facade_rowhome` and `gs_facade_storefront`, the
#: two sealed boxes from before, do not carry it and are not offered.
EMPTY_PREFIX = "gs_empty_"


def empty_rows(build_dir) -> list[dict]:
    """Every Empty in a Deli Counter build dir that can be themed, sorted by
    id: ``{"id", "family", "glb", "gameplay", "slots"}``. An Empty is one
    Deli Counter says is (`facade` true in its validation manifest) and whose
    id carries `EMPTY_PREFIX`; it has no lights by design (its lit windows
    are paint), so `.lights.json` is not asked for."""
    d = Path(str(build_dir))
    out = []
    for glb in sorted(d.glob(EMPTY_PREFIX + "*.glb")):
        aid = glb.stem
        row = {"id": aid, "family": "empty", "glb": str(glb),
               "gameplay": str(d / f"{aid}.gameplay.json"),
               "slots": str(d / f"{aid}.slots.json")}
        if not all(Path(row[k]).exists() for k in ("gameplay", "slots")):
            continue
        if (_manifest(d / (aid + ".validation.json")) or {}).get("facade") is not True:
            continue
        out.append(row)
    return out


def empties_for_brief(model) -> list[dict]:
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
'''


PLANNER = '''        # THE EMPTIES (0.137.0): every Empty the brief asks for is themed as
        # itself -- its kit, its Patina pass and its dressing -- and composed
        # beside the lot. No fixtures and no fixture gate: an Empty has no
        # lights (its lit windows are paint), and `require_art_inputs` is not
        # asked of it for the same reason.
        for _e in building_library.empties_for_brief(brief):
            aid = _e["id"]
            zoo_kit_jid = job_id(brief.mission_id, _STAGE_ZOO_KIT, archetype=aid)
            plan.graph.add(Job(
                job_id=zoo_kit_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_ZOO_KIT, adapter_id="zoo",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="blender",
                depends_on=[lot_jid, pixelcoat_jid], expected_outputs=[]))
            zoo_kit_jids.append(zoo_kit_jid)
            patina_base_jid = job_id(brief.mission_id, _STAGE_PATINA_BASE, archetype=aid)
            plan.graph.add(Job(
                job_id=patina_base_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_PATINA_BASE, adapter_id="patina",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="python_cpu", depends_on=[lot_jid],
                expected_outputs=[f"{aid}.patina.glb", f"{aid}.patina.json",
                                  f"{aid}.patina.gameplay.json"]))
            patina_dress_jid = job_id(brief.mission_id, _STAGE_PATINA_DRESS, archetype=aid)
            plan.graph.add(Job(
                job_id=patina_dress_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_PATINA_DRESS, adapter_id="patina",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="python_cpu", depends_on=[patina_base_jid],
                expected_outputs=[f"{aid}.patina.glb", f"{aid}.patina.json",
                                  f"{aid}.patina.gameplay.json",
                                  f"{aid}.patina.dressing.json"]))
            zoo_dress_jid = job_id(brief.mission_id, _STAGE_ZOO_DRESS, archetype=aid)
            plan.graph.add(Job(
                job_id=zoo_dress_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_ZOO_DRESS, adapter_id="zoo",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="blender",
                depends_on=[patina_dress_jid, zoo_kit_jid], expected_outputs=[]))
            zoo_dress_jids.append(zoo_dress_jid)
'''


SPEC = '''    # THE EMPTIES ACROSS THE STREET (0.137.0, roadmap 106): a terrace of
    # non-enterable shells along the far side of the through road, every
    # front on one line, as Lot `blockers` -- themed when the compose stage
    # published their scenes, greybox otherwise, like the lot's buildings.
    # Lot reads no walk, dumpster, field or entry gate off a blocker.
    import math
    from packages.pipeline import building_library as _bl
    _empty_rows = _bl.empties_for_brief(model) if library else []
    if _empty_rows and roads:
        from packages.pipeline import empties as _empties
        from packages.pipeline import street_line as _sl
        _ext = {r["id"]: _sl.shell_extents(r["glb"]) for r in _empty_rows}
        _row = {r["id"]: r for r in _empty_rows}
        placed_e, need_half = _empties.terrace(
            _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x5E3A11),
            roads, spec["ground"]["size_x"])
        blockers = []
        for p in placed_e:
            aid = p["archetype"]
            scene = (themed_map or {}).get(aid)
            if scene:
                staged_packages[aid] = str(Path(scene).parent)
                src = {"scene": f"lot/{aid}/site.tscn"}
            else:
                staged_glbs[aid] = str(_row[aid]["glb"])
                src = {"glb": f"buildings/{aid}.glb"}
            blockers.append({"id": p["id"], "archetype": aid, **src,
                             "at": p["at"], "rot": p["rot"],
                             "size_x": p["size_x"], "size_y": p["size_y"],
                             "empty": True})
        if blockers:
            spec["blockers"] = blockers
            # the plate reaches past the row's backs by the clearance the
            # row's own ends keep
            half_y = need_half + _empties.CLEARANCE
            if spec["ground"]["size_y"] / 2.0 < half_y:
                spec["ground"]["size_y"] = int(math.ceil(2.0 * half_y))
            print(f"[site] {len(blockers)} Empt{'y' if len(blockers) == 1 else 'ies'} "
                  f"across the street, {len({b['archetype'] for b in blockers})} "
                  f"shell(s), {'themed' if themed_map else 'greybox'}")
    # Self-check before the spec leaves the building. This can only fire if the
'''


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.136.0", v
    assert not (LF / "packages" / "pipeline" / "empties.py").exists(), "already applied"
    _edit(LF / "packages" / "core" / "models.py", [
        ('    lot_library: str = ""\n',
         '    lot_library: str = ""\n'
         '    #: EMPTIES (0.137.0, roadmap 106): `"across"` stands a terrace of\n'
         '    #: non-enterable shells along the far side of the through road,\n'
         '    #: drawn from the lot library\'s Empties. Empty (the default) leaves\n'
         '    #: the far side to the plate\'s edge, as every level before it.\n'
         '    empties: str = ""\n'),
        ('        if self.lot_library:\n'
         '            sig["lot_library"] = self.lot_library\n',
         '        if self.lot_library:\n'
         '            sig["lot_library"] = self.lot_library\n'
         '        # the same care for the Empties (0.137.0): they stand on the site\n'
         '        if self.empties:\n'
         '            sig["empties"] = self.empties\n'),
    ])
    bl = LF / "packages" / "pipeline" / "building_library.py"
    s = bl.read_text(encoding="utf-8")
    assert "\r" not in s and "def empty_rows" not in s
    bl.write_text(s.rstrip("\n") + "\n" + LIB, encoding="utf-8", newline="\n")
    _edit(LF / "packages" / "pipeline" / "planner.py", [
        ('            zoo_dress_jids.append(zoo_dress_jid)\n'
         '        # Named before the fixtures jobs are added, because compose depends on\n',
         '            zoo_dress_jids.append(zoo_dress_jid)\n' + PLANNER +
         '        # Named before the fixtures jobs are added, because compose depends on\n'),
    ])
    _edit(LF / "apps" / "cli" / "commands" / "__init__.py", [
        ('              f"(incomplete manifest): "\n'
         '              + ", ".join(e["id"] for e in incomplete[:5]))\n'
         '    return lot\n',
         '              f"(incomplete manifest): "\n'
         '              + ", ".join(e["id"] for e in incomplete[:5]))\n'
         '    # THE EMPTIES ARE COMPOSED BESIDE THE LOT (0.137.0): their rows join\n'
         '    # the lot\'s, so their art jobs resolve, compose themes them and the\n'
         '    # themed site finds their scenes -- one list, not three.\n'
         '    if lot:\n'
         '        ids = {e["id"] for e in lot}\n'
         '        lot = lot + [e for e in building_library.empties_for_brief(model)\n'
         '                     if e["id"] not in ids]\n'
         '    return lot\n'),
        ('    # Self-check before the spec leaves the building. This can only fire if the\n',
         SPEC),
    ])
    # Deli Counter 0.174.0 registers `empty_rowhome`; the adapter's own set
    # is compared with the registry (`test_dc_preset_registry`)
    _edit(LF / "adapters" / "deli_counter" / "__init__.py", [
        ('    "corner_deli", "facade_industrial", "facade_rowhome",\n',
         '    "corner_deli", "empty_rowhome", "facade_industrial", "facade_rowhome",\n'),
    ])
    # an Empty has no front door to find: the 0.132.0 survey skips them
    _edit(LF / "tests" / "unit" / "test_front_door.py", [
        ('from __future__ import annotations\n',
         'from __future__ import annotations\nimport json\n'),
        ('    found = sum(1 for f in files if FD.front_wall_of(f)[0] is not None)\n',
         '    # AN EMPTY HAS NO FRONT DOOR TO FIND (0.137.0): Deli Counter 0.174.0\'s\n'
         '    # non-enterable shells record no openings by design, so they are not\n'
         '    # buildings this rule turns. Skipped by Deli Counter\'s own word for them.\n'
         '    def _empty(f):\n'
         '        v = f.replace(".gameplay.json", ".validation.json")\n'
         '        try:\n'
         '            with open(v, encoding="utf-8") as fh:\n'
         '                return json.load(fh).get("facade") is True\n'
         '        except (OSError, ValueError):\n'
         '            return False\n'
         '    files = [f for f in files if not _empty(f)]\n'
         '    found = sum(1 for f in files if FD.front_wall_of(f)[0] is not None)\n'),
    ])
    shutil.copyfile(SRC / "empties.py", LF / "packages" / "pipeline" / "empties.py")
    shutil.copyfile(SRC / "test_empties_terrace.py", LF / "tests" / "unit" / "test_empties_terrace.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    assert s.startswith("## [0.136.0]"), "changelog head"
    ch.write_text((SRC / "CHANGELOG_0.137.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.137.0", encoding="utf-8", newline="\n")
    print("Level Factory 0.137.0 applied")


if __name__ == "__main__":
    main()
