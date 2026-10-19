"""Roadmap 177 NARROWED again and 74 corrected, 2026-10-19: the last two z-fight pairs were the gate's.

177: Deli Counter's z-fight gate read each composed module's Transform3D basis as columns; Godot writes rows.
deli_a01's two pairs were its misreading (`docs/findings/zfight_rows_177/`); Deli Counter 0.230.0 reads rows, and
cold run 9325 reads every building OK. BLOCK still waits on the library's count, which nothing measures.

74: `tools/repetition_census.py` read turned instances' scales transposed, so its form counts on cold run 9314
were inflated; re-measured on cold run 9324 with the corrected reader. Its worst runs stand.

Each status line is replaced whole, its earlier status kept after it verbatim; each item gains a paragraph after
its last body line. Anchored on the four lines' sha256, each status's heading two lines below it and each body's
next status two lines below its end. The index is NOT touched here: run `python tools/roadmap_status.py --write`
then `--check` after it.

    python patches/patch_roadmap_177_74.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = {
    "177": {
        "status_sha": "0729008d27befe3d3186ce11ac0f06a48394c2c4c8719963dfb2413f5a70d272",
        "heading": "**177. A gate has printed FAIL on five consecutive cold runs and nobody read",
        "old_prefix": "*STATUS: NARROWED 2026-10-19 -- ",
        "body_end_sha": "2b9cafc5ee1ed550f048c104acfa87c98aab70a92f7c3d0e743f84bdb495331a",
        "new": ("*STATUS: NARROWED 2026-10-19 -- every building the level composes reads OK, and the last two "
                "pairs were the instrument's. Deli Counter's z-fight gate read each composed module's `Transform3D` "
                "basis as columns where Godot 4.7 writes and parses rows (measured three times; "
                "`docs/findings/zfight_rows_177/`): deli_a01's east-wall end piece, 0.6 m along its wall and 0.35 m "
                "through it, came out the other way round and shared both side planes of partition 1 -- the two "
                "0.9 m2 pairs of cold runs 9322 to 9324. The engine stands it as written, with no face on either "
                "plane (`tools/module_pose_census.py` on 9324's package). Deli Counter 0.230.0 (c5e77e52, "
                "`patches/patch_dc_zfight_rows.py`) reads rows: on 9324's 16 composed buildings, 2 visible pairs -> "
                "0, none unmasked. Cold run 9325 (urban_row_001, 0 interventions, seed 9104 PASS 100): 17 buildings "
                "[OK], findings 108 -> 107, PRESENTATION_ZFIGHT 1 -> 0. The same misreading in Level Factory's "
                "ground-contact pre-flight (0.218.2) and five of the factory's tools is fixed with it "
                "(`tools/godot_transform.py`, their one reader now). Left for BLOCK, the decision's condition: the "
                "LIBRARY's count, which needs every building composed with its art and no run does; the gate stays "
                "WARN until that reads zero. Earlier status kept: NARROWED 2026-10-19 -- "),
        "body": [
            "",
            "**THE LAST TWO PAIRS WERE THE GATE'S, 2026-10-19** (`docs/findings/zfight_rows_177/`; Deli Counter "
            "0.230.0, `patches/patch_dc_zfight_rows.py`; `docs/cold_runs/cold_9325/`). **Refuted, kept:** the "
            "status above filed deli_a01's two pairs as partition 1 \"running the building's full 38 m into the east "
            "wall, whose segment ends land on its faces\", geometry in the modular kit's wall junction. The slots "
            "did not fit that: the east wall's end piece is 0.6 m along the wall and centred on the junction, so "
            "its faces stand 0.125 m beyond the partition's on each side, and a 0.9 m2 overlap is exactly what it "
            "would share with the partition if its length and thickness were swapped. The engine "
            "(`tools/module_pose_census.py` on cold run 9324's package) stands it x 18.825..19.175, z "
            "-6.300..-5.700, as written; the gate read the basis's rows as columns, the transpose, which a pure "
            "turn hides and a turned, non-uniformly scaled module does not. Deli Counter 0.120.1 had moved the "
            "placement gate to rows for the same reason after cold run 9013; the z-fight gate, its sibling, kept "
            "columns. **Fixed and measured:** read as rows, 9324's 16 composed buildings count 0 visible pairs and "
            "none unmasked (buried, never gated on: deli_a01 213 -> 220, pharmacy_a01 29 -> 27); cold run 9325 "
            "reads 17 [OK] and PRESENTATION_ZFIGHT 1 -> 0. **The class:** Level Factory's ground-contact pre-flight "
            "(0.218.2) and five of the factory's tools held the same belief; re-read with rows, roadmap 74's form "
            "counts fall. **For BLOCK:** the library's count. Composing every library building with its art would "
            "measure it, and nothing does that today.",
        ],
    },
    "74": {
        "status_sha": "3c6b371733a91ba6b86fb960cbb440b4ab66f08909018db281949e37b1d3f5e1",
        "heading": "**74. Every wall in every building is the same 2.00 m module, and it gets",
        "old_prefix": "*STATUS: OPEN 2026-10-15 -- ",
        "body_end_sha": "44e82df05a66f39455150068348cbb9bc5de1891e81104b5415f6139090fa593",
        "new": ("*STATUS: OPEN 2026-10-19 -- CORRECTED, the form counts. The ruler read turned instances' scales "
                "transposed (`docs/findings/zfight_rows_177/`), so one wall-end size on an east-west wall and on a "
                "north-south one counted as two forms. Re-measured on cold run 9324's mission buildings with the "
                "corrected reader: deli_a01 347 wall instances, 59 forms where the 2026-10-15 reading said 64, worst "
                "run 18 of 21; office 196 / 24 (said 25) / 11; pharmacy_a01 73 / 24 / 7, unchanged. The worst runs "
                "stand -- every piece in one wall run shares a turn -- and so do the item's two closing moves. The "
                "2026-08-29 baseline was read with the same transposed scale and is not re-measured. Earlier status "
                "kept: OPEN 2026-10-15 -- "),
        "body": [
            "",
            "**CORRECTED, 2026-10-19: THE FORM COUNTS** (`docs/findings/zfight_rows_177/`, `before/` and `after/`). "
            "`tools/repetition_census.py` took each instance's per-axis scale from the lengths of the "
            "`Transform3D`'s written triplets, which are the basis's rows; per-axis scale is the length of each "
            "column. For a quarter-turned module the two swap x and z, so a wall end 1.65 m long on a north-south "
            "wall read as a form 0.35 m long and 1.65 m thick, distinct from its twins on an east-west wall. Read "
            "by columns on cold run 9324's composed buildings: deli_a01 64 -> 59 forms, office 25 -> 24, "
            "pharmacy_a01 24 -> 24; wall instances, worst runs and pitches unchanged; reuse 5.42 -> 5.88 and 7.84 "
            "-> 8.17 placements a form. The buildings are a little more repetitive than this item said, and its "
            "measure of a run is untouched.",
        ],
    },
}


def _sha(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    plans = []
    for n, it in ITEMS.items():
        hits = [i for i, l in enumerate(lines) if _sha(l) == it["status_sha"]]
        assert len(hits) == 1, f"item {n}'s status found {len(hits)} times"
        i = hits[0]
        assert lines[i + 1] == "" and lines[i + 2].startswith(it["heading"]), f"item {n}'s status left its heading"
        assert lines[i].startswith(it["old_prefix"]) and lines[i].endswith("*")
        ends = [j for j, l in enumerate(lines) if _sha(l) == it["body_end_sha"]]
        assert len(ends) == 1 and ends[0] > i, f"item {n}'s last body line found {len(ends)} times"
        j = ends[0]
        assert lines[j + 1] == "" and lines[j + 2].startswith("*STATUS:"), f"item {n}'s body no longer ends there"
        for k in range(i + 3, j):
            assert not lines[k].startswith("*STATUS:"), f"another status inside item {n} at line {k + 1}"
        for block in it["body"]:
            assert not (block.startswith("**") and block[2:3].isdigit()), "a body line would parse as an item"
        plans.append((i, j, it))
    # apply bottom-up so earlier indexes stay valid
    for i, j, it in sorted(plans, key=lambda p: -p[0]):
        lines[j + 1:j + 1] = it["body"]
        old = lines[i]
        lines[i] = it["new"] + old[len(it["old_prefix"]):]
        assert lines[i].endswith("*")
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 177 NARROWED (the gate's two pairs, Deli Counter 0.230.0, cold run 9325) and 74 corrected; "
          "now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
