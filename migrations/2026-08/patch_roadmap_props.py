"""Item 22: outdoor props have no swap contract. Plus four carried smalls.

ITEM 22 came from looking at a lit level and asking why the cover is still
boxes. The answer is not that Zoo cannot build props -- it builds kit modules,
dressing props and light fixtures already. It is that the swap contract Deli
Counter has for building interiors was never extended outdoors, so nothing
downstream is invited to replace Lot's cover crates.

THE FOUR SMALLS are things this session found and would otherwise lose: the
migrations index built from one run instead of a directory, archive_scratch
superseded by tidy_migrations, ps1.gdshader existing twice, and cater writing a
project.godot without a main scene while package.py writes one with.

Anchored on `### Smaller, carried` and `### Not to be worked on`, both verified
unique. Asserts both, refuses on a miss.
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEM_ANCHOR = "### Not to be worked on\n"

ITEM = '''**22. Outdoor props have no swap contract, so cover stays boxes forever.** The
art path's missing wire, and the reason a lit site still reads as a blockout.

Lot places cover as primitive 1 m boxes -- `LOT_COVER_PLACED: 22 piece(s) of 2 m
cover were placed to break sightlines` -- and nothing downstream is invited to
replace them. That is not a Zoo limitation. Zoo already owns "structural kit
modules built to Deli Counter's slot dims, dressing props, and light fixtures",
and it already does exactly this swap one scale down:

    Deli Counter    greyboxes a building, emits <name>.slots.json -- "every
                    wall / doorway / window / breach slot with a transform, fit
                    dims, and a role"
    Zoo             builds modules to those dims; "the resolver swaps them in
                    for the grey boxes -- missing modules keep the box, so the
                    art pass stays progressive"

**Lot has no equivalent.** There is no `<site>.slots.json`, so Zoo's props and
Pixelcoat's skins have nothing to resolve against outdoors. The machinery exists
at both ends and the manifest between them does not.

WHY THIS IS NOT JUST "EMIT A LIST OF POSITIONS". A car is not a 1 m cube. Cover
was placed to occlude a measured sightline -- Laser Tag opens fire at 45 m and
`LOT_SIGHTLINE_OPEN` reports what is still exposed after placement. Swap in
geometry with a different footprint and the thing the placement was solving has
silently changed, with no gate able to see it. Which is precisely what Zoo's
`fit_*` validation is for: "modules whose dimensions exactly fit the requesting
slot". So outdoor cover wants the same treatment as a wall slot -- transform,
fit dims, and a role (`vehicle`, `dumpster`, `crate`, `planter`) -- with the box
kept whenever nothing fits, so the art pass stays progressive here too.

The same contract would carry the rest of the outdoor vocabulary: blockers are
already "facade shell" capable, and roads, kerbs and courtyards are surfaces
Pixelcoat could skin if anything told it their extents and material roles.

Do not start this before the drift in item 21 is closed. It adds a contract
between two tools that are both currently uncertified.

'''

SMALL_ANCHOR = "### Smaller, carried\n"

SMALL = '''### Smaller, carried

**`MIGRATIONS.md` indexes one run rather than a directory.** `tidy_migrations.ps1`
builds the table from the files *that invocation* moved, so when `tidy_tools.ps1`
filed five scripts into `migrations/2026-08/` and a later `tidy_migrations` run
moved two more, the index was rewritten to list two and the five vanished from
it. The directory holds seven. Generate the table by walking
`migrations/<bucket>/` and it is correct no matter which script filed something,
and self-healing when one skips the index entirely. Same shape as everything
else in this file: an enumeration of one run standing in for a description of a
set.

**`archive_scratch.ps1` is superseded and its list has rotted.** It enumerates 23
filenames, three of which -- `lf_patch.ps1`, `guardrail_regate.ps1`,
`reconcile_version.ps1` -- it would have archived as one-shots. It was right
about all three, and only its `git ls-files` tracked-check stopped it. Those
three are now in `migrations/2026-08/` where they belong.
`tidy_migrations.ps1` does the same job by rule. Retiring one of the two is a
decision rather than a tidy, so both are still there.

**`ps1.gdshader` exists twice**, at `patina/godot/addon/patina/ps1.gdshader` and
`patina/godot/shaders/ps1.gdshader`, identical 2,688 bytes. The addon README
says the copy inside the addon is the one that travels. Two copies of a shader
is the same drift risk as two copies of a rule, and item 20 may retire both
anyway.

**`cater.py` writes a `project.godot` with no main scene.** `package.py
--walkable` sets `run/main_scene` and says so; cater writes "minimal
project.godot" without one, so F5 in a cater-built project fails with "no main
scene defined" and only F6 on the open scene works. Two writers of the same file
disagreeing about what a complete one contains. One line in cater.

'''


def main() -> int:
    if not RM.exists():
        raise SystemExit(f"missing {RM}. Nothing written.")
    src = RM.read_text(encoding="utf-8")
    before = len(src)
    done = []

    if "**22. Outdoor props have no swap contract" in src:
        done.append("item 22 already present")
    else:
        if "**21. Four of eight tools have drifted" not in src:
            raise SystemExit("no item 21 -- run patch_roadmap_addons.py first. "
                             "NOTHING WRITTEN.")
        n = src.count(ITEM_ANCHOR)
        if n != 1:
            raise SystemExit(f"`Not to be worked on` appears {n} time(s), "
                             f"expected 1. NOTHING WRITTEN.")
        src = src.replace(ITEM_ANCHOR, ITEM + ITEM_ANCHOR)
        done.append("item 22, ahead of `Not to be worked on`")

    if "MIGRATIONS.md` indexes one run" in src:
        done.append("the four smalls already present")
    else:
        n = src.count(SMALL_ANCHOR)
        if n != 1:
            raise SystemExit(f"`Smaller, carried` appears {n} time(s), expected "
                             f"1. NOTHING WRITTEN.")
        src = src.replace(SMALL_ANCHOR, SMALL)
        done.append("four carried smalls, at the top of `Smaller, carried`")

    if not any("already present" not in d for d in done):
        for d in done:
            print(f"  {d}")
        return 0

    backup = RM.with_suffix(".md.pre_props")
    if not backup.exists():
        shutil.copy2(RM, backup)
    RM.write_text(src, encoding="utf-8")
    for d in done:
        print(f"  PIPELINE_ROADMAP.md: {d}")
    print(f"  {before} -> {len(src)} characters; previous file kept at "
          f"{backup.name}")
    print("\n  22 is the art path's missing wire: Zoo can build props, Deli "
          "Counter has a\n  slot contract for interiors, and nothing connects "
          "either to Lot's cover.\n  The four smalls are things tonight found "
          "that were living in a chat window.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
