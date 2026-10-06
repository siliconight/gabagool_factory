"""Level Factory 0.144.0: VERSION and the CHANGELOG entry for
`patch_lf_defaults_on.py` and `patch_lf_bake_report_metadata.py`, written
after the failing tests and the suite were measured.

    python patch_lf_defaults_on_release.py
"""
import pathlib

LF = pathlib.Path(__file__).resolve().parent.parent / "level_factory"

ENTRY = '''## [0.144.0] - The Empties and the light bake, on by default

The walker, 2026-10-05: "yes to both defaults", before a cold run on each of
ten missions.

**Why.** Cold runs 9135 to 9165 all built gas_block_001, and no other mission
has had a cold run since 9134 (2 October). So nothing shipped since has been
through a cold run on any other brief: the light bake (0.131.0), fronts to
the street (0.132.0), the Empties (0.137.0 on) and their merge (0.143.0).
Both were opt-in. A brief that did not know the field, and an export that
did not know the flag, got neither.

**The Empties** (`packages/core/models.py`).
- `MissionBrief.empties` defaults to `"across"`. `"none"`, or any other
  word, the empty string included, turns them off.
- `empties_effective(empties, lot_library, building_count)` is the one rule.
  A terrace stands when the brief asks or says nothing, has a lot library to
  draw from, and stands two or more buildings.
  `building_library.empties_for_brief` and `functional_signature` both read
  it, so the lock and the site cannot disagree.
- **What it invalidates.** The signature now carries
  `"empties": "across"` for every brief with a lot library and two or more
  buildings that said nothing.
  - Those missions' functional locks break, which is right: a terrace now
    stands on their sites.
  - A brief with no library, or one building, keeps its signature, because
    it gets no terrace.
  - A brief that said `"across"` or `"none"` without the means to stand one
    loses a key that recorded nothing.
- **Of the ten missions the sweep builds** (their briefs as last run cold):
  - seven get the terrace. gas_block_001 already asked; club_block_014,
    bank_block_001, video_block_001, card_block_001, precinct_yard_001 and
    gas_stop_001 now do.
  - three cannot: county_hospital_001 (one building, no library),
    restaurant_row_001 and warehouse_yard_001 (no library).
- **Not changed:** `lot_library` stays opt-in, for the reason its own
  comment gives. The Empties reach as far as the lot library does.

**The light bake** (`apps/cli/main.py`).
- `export` bakes unless passed `--no-bake-lights`
  (`argparse.BooleanOptionalAction`, default on). `--bake-lights` still
  parses, for every command already written with it.
- `ExportProfile.bake_lights` stays `False`. Code that builds a profile says
  what it wants, and the suite opens no editor window.
- **The cost, stated before anyone pays it.** About a minute of editor
  window per export on a machine with a GPU and a display: 75.6 s in cold
  run 9165.
  - Without either, the bake fails and the package ships unbaked, with the
    reason in `light_bake.json` (`light_bake.py:314-321`).
  - That is quick when Godot is missing or the editor exits. If the editor
    hangs, it waits up to `EDITOR_TIMEOUT_S` (900 s, `light_bake.py:74`).
  - Nobody has measured which happens on a machine with no display.

**A defect the default found, fixed here** (`packages/exporting/closure.py`).
With the bake on, `test_presentation_export_and_portability` exported
through it for the first time.
- Its stub presentation scene has no rig script, so the bake failed and
  restored the package, as designed.
- But `reason` carried the package's absolute path, and the closure scan
  refused the export: `EXPORT_CLOSURE_BROKEN ... light_bake.json: absolute
  path`. So a machine that could not bake could not export at all, whenever
  the reason named a path.
- `light_bake.json` joins `_METADATA_FILES`, beside
  `glb_reference_scan.json`. It is LF's own log of a build step, and no
  Godot loader reads it (a grep across lux, dispatch and LF's assets).
- A successful bake's report carries no path, which is why no cold run met
  this.

**Tests.**
- `test_empties_terrace.py`'s brief test is rewritten. It pinned the opt-in,
  and now pins the default, the opt-out, and the unchanged signature of a
  brief with no library or one building.
- `test_light_bake.py` gains the command line's default and the failed
  bake's closure.
- **Proven to fail without the change.** On 0.143.0's source, the two
  default tests fail. On the unfixed scan, the closure test fails with the
  integration test's own error.
- **Suite:** 1,921 collected: 1,906 passed, 14 skipped, 1 xfail.

'''


def main():
    version = LF / "VERSION"
    changelog = LF / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"0.143.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.143.0] - "), c[:60]
    version.write_bytes(b"0.144.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Level Factory 0.144.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
