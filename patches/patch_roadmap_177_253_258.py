"""Roadmap 177 NARROWED (decided), 253 NARROWED (built), 258 OPEN (re-measured), 2026-10-19.

177: the decision it owed -- block, warn or delete -- made under the walker's standing instruction of 2026-10-19
("make decisions that can be changed later"): warn now, block once the library counts zero. Level Factory 0.218.1
says WARN; Deli Counter 0.227.0 takes the office's two pairs out; cold run 9323 leaves deli_a01's two.
253: built and in every walk copy; what closes it is the walker's walk. 258: the time it priced is cached away on a
repeat run; the dead assets stand, bigger.

Each status line is replaced whole, its earlier status kept after it verbatim. Anchored on each line's sha256 and on
the item heading two lines below it (asserted once). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_177_253_258.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    {
        "n": 177,
        "sha": "1e84bd859bcbdaf6cf68bc7811b3da097ee3c1fa2ef6b1da6166dd27539a92f0",
        "heading": "**177. A gate has printed FAIL on five consecutive cold runs and nobod",
        "old_prefix": "*STATUS: NARROWED 2026-10-06 -- ",
        "new": ("*STATUS: NARROWED 2026-10-19 -- THE DECISION IS MADE, a call meant to be changed (the walker's "
                "standing instruction of 2026-10-19): WARN now, BLOCK once the library counts zero. The pipeline "
                "already warned -- the compose job is `exit_advisory`, so the scheduler records it SUCCEEDED, and "
                "the presentation adapter files PRESENTATION_ZFIGHT as moderate and not blocking -- while the log "
                "said [FAIL] and ERROR: Level Factory 0.218.1 (4fb25fb, `patches/patch_lf_zfight_warns.py`) makes it "
                "say WARN and name the pairs. Cold run 9322's four pairs, all open-sided and all Deli Counter "
                "geometry, attributed: the office's `VAULTLEDGE_0 / reception_desk` (2), the preset's vault ledge "
                "standing inside the reception desk it tags, a 0.2 m strip 10 cm proud of the desk -- Deli Counter "
                "0.227.0 (709fee88, `patches/patch_dc_vault_ledge_hidden.py`) draws no box for a ledge at least half "
                "inside a visible volume (`ledge_cover.HIDDEN_BY`, a call; 7 built shells, 19 of 228 ledges in the "
                "spec library), collider and vault tag kept; and deli_a01's `ext_0_E_seg10 / int_0_1_seg18` (2), "
                "partition 1 running the building's full 38 m into the east wall, whose segment ends land on its "
                "faces. Cold run 9323 (0 interventions, findings 109 -> 108): 16 buildings OK, deli_a01 WARN on its "
                "2. Left for BLOCK: those 2, in the modular kit's wall junction; then the adapter's finding becomes a "
                "blocker and the label FAIL. Earlier status kept: NARROWED 2026-10-06 -- "),
    },
    {
        "n": 253,
        "sha": "ed26d3f27f64f796cb266050c39fb10d377ee0d44c5c8a07a0a6dfa457c05278",
        "heading": "**253. Flag assets as looking good or needing love.**",
        "old_prefix": "*STATUS: OPEN 2026-10-14 -- ",
        "new": ("*STATUS: NARROWED 2026-10-19 -- BUILT, and in every walk copy since cold run 9323; what closes it is "
                "the walker's walk. `tools/walk_asset_flags.gd` (root f7e7a76; debug builds only, like F3 and the "
                "work light): G marks what the crosshair rests on as looking good, P as needing love, and a banner "
                "says what was flagged. It picks BY RENDER first -- collision here is Deli Counter's greybox and the "
                "asset the eye sees is the Zoo module over it, so the F3 ray names `slab_col_1` and never the tile -- "
                "names the asset by its nearest instanced ancestor's file (module and building) with the physics "
                "hit beside it, and appends a record and a 640-wide frame beside the copy. `tools/asset_flags.py` "
                "gathers every copy's flags into one ledger per asset, needs-love first, frames copied beside it so "
                "it outlives the walk copy (`docs/findings/asset_flags_253/`). Proven headless "
                "(`tools/walk_asset_flags_selftest.gd`, 14 checks) and by the ledger's selftest. Known gaps: a "
                "MultiMesh (Lot's dressing) falls to the physics hit; merged Empties carry their merged name. "
                "Earlier status kept: OPEN 2026-10-14 -- "),
    },
    {
        "n": 258,
        "sha": "5fe604649678b3b2b247eb5b266fdec021643b4491435f22c32cef6bd52c505a",
        "heading": "**258. The mission's own shell is built three times a run and ships as",
        "old_prefix": "*STATUS: OPEN 2026-10-15 -- ",
        "new": ("*STATUS: OPEN 2026-10-19 -- RE-MEASURED, still not decided. On cold run 9322 the three shell builds "
                "finished 17 s into the shell leg (all three job logs at 07:47:56, the leg starting at 07:47:39), "
                "against 1.7 min each on 9316: the build cache from the cold-run speed loop (239) serves a repeat "
                "run, so the time this item priced is paid only on a new mission or seed. What stands is the dead "
                "asset, bigger: 9322's package carries `assets/shell.glb` and `assets/lot.glb`, 1,020,940 bytes "
                "each and byte-identical, which no scene references (only `build.lock.json`, `light_bake.json`, "
                "`mission_manifest.json` and `portable_resource_manifest.json` list them). So reading (1) now buys "
                "about 2 MB a package and a compose arm, not five minutes. Earlier status kept: OPEN 2026-10-15 -- "),
    },
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    found = []
    for it in ITEMS:
        hits = [i for i, l in enumerate(lines) if hashlib.sha256(l.encode("utf-8")).hexdigest() == it["sha"]]
        assert len(hits) == 1, f"{it['n']}: the status line found {len(hits)} times"
        i = hits[0]
        assert lines[i + 1] == "" and lines[i + 2].startswith(it["heading"]), \
            f"{it['n']}: the status no longer adjoins its heading"
        old = lines[i]
        assert old.startswith(it["old_prefix"]) and old.endswith("*")
        new = it["new"] + old[len(it["old_prefix"]):]
        assert new.endswith("*") and not new.startswith("**")
        found.append((i, new))
    for i, new in found:
        lines[i] = new
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 177 NARROWED (decided), 253 NARROWED (built), 258 OPEN (re-measured); now roadmap_status.py "
          "--write / --check")


if __name__ == "__main__":
    sys.exit(main())
