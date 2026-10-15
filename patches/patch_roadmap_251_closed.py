"""Roadmap 251 CLOSED: Level Factory 0.212.0, proven by cold run 9313 against 9312. Replaces 251's status block
(asserted once) and appends one body paragraph at the end of 251's body, before 252's status block. The index is
NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_251_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-10-14 -- FOUND WRITING COLD RUN 9308'S NOTES. The light bake's log line counts "
                   "every inline primitive given a UV2 in every scene of the package as lightmapped")
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-15 -- Level Factory 0.212.0 (775cac8): `add_primitive_uv2(export_dir, only=)` writes "
    "and counts the scenes the bake draws, `baked_scenes(export_dir)` -- the presentation and every scene it "
    "instances, transitively -- and the export passes it; `only=None` is every scene, as before. Cold run 9313 "
    "(urban_row_001, seed_9104, staged from 9312, 0 interventions, `docs/cold_runs/cold_9313/`): the log reads "
    "`349 model(s) and 112 primitive mesh(es) lightmapped` where 9312's read 225; `site.tscn` carries 0 "
    "`add_uv2 = true` marks where it carried 112 and `site_backdrop.tscn` 0 where it carried 1, the presentation "
    "its 112 as before; `bake.exr` the same bytes as 9312's, all 329 GLBs the same, 3,160 lightmap users as "
    "before; of the 24 files that differ, 2 are these marks, 12 are Godot's per-save ids (247's residue, 0 lines "
    "once masked), and 10 are the metadata that records times, paths, versions and the hashes of the above "
    "(`uv2_marks.py`, `masked_scenes.py` there). `tests/unit/test_bake_counts_what_it_bakes.py`, four checks "
    "failing on 0.211.0 and passing on 0.212.0; the suite 2,427 passed.*"
)

BODY_ADD = """

**PROVEN, cold run 9313** (`docs/cold_runs/cold_9313/NOTES.md`). Level Factory 0.212.0 on 9312's toolchain, brief and seed: the one line that was wrong reads 112, the two scenes the bake never draws carry no second UV set, the scene it does draw carries its 112 as before, and the lightmap is byte for byte 9312's -- which is the proof that the count was the only thing that moved: the bake's input, the presentation and the lot scenes it instances, had every mark it has now. What the backdrop's ground lost is a UV2 nothing read; its cost in the frame is 252's."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "PROVEN, cold run 9313" not in text, "already applied"
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "251's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    text = text[:i] + STATUS_NEW + text[j:]
    head = "\n\n**251. The light bake's log says \"lightmapped\" of primitives it does not bake.**"
    h = text.find(head)
    assert h > 0 and text.count(head) == 1, "251's heading not found once"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, "no status block after 251's body"
    assert "**252. " in text[nxt:nxt + 2000], "the block after 251 is not 252's"
    text = text[:nxt] + BODY_ADD + text[nxt:]
    k = text.find(STATUS_NEW)
    assert text[k + len(STATUS_NEW):].startswith(head), "251's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 251: status replaced, one paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
