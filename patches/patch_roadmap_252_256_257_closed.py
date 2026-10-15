"""Roadmap 252, 256 and 257 CLOSED: Level Factory 0.213.0, 0.214.0, 0.215.0 and 0.215.1, proven by cold run 9314.
Replaces each item's status block (each asserted once) and appends one body paragraph to 257. The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_252_256_257_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    ("*STATUS: NARROWED 2026-10-15 -- PRICED, and the cheap version ships.",
     "\n\n**252. The backdrop's ground was shipped unpriced.**",
     "*STATUS: CLOSED 2026-10-15 -- priced, and the cheap version shipped and proven. Priced on cold run 9308's "
     "package against itself with the node removed, two controls, 53 headings (`docs/findings/walk_2026-10-14/`, "
     "\"The ground's price\"): shaded as 0.211.0 shipped it, +1 to +7 draws a heading (+2.5 on the mean) and at the "
     "heaviest heading +6 draws and +7.20 ms on the p95 against a 0.40 ms noise floor, nine of 53 headings beyond "
     "the controls' spread; unshaded, +1 draw everywhere and at most +0.52 ms (+0.04 on the median, an 0.08 ms "
     "floor); at the walker's spot, from 26 m up and from the east elevation the two read the same in that evening "
     "level (`ground_frames/ground_sheet.png`). Level Factory 0.215.0 (56fd144) writes the ground unshaded, line "
     "for line the priced arm's material; cold run 9314 (0 interventions, `docs/cold_runs/cold_9314/`) carries it "
     "in `site_backdrop.tscn` and `backdrop_layer.json`, the lightmap and every GLB 9313's bytes, no fight field "
     "moved. Left to the walker, not to this item: the shaded ground on a level when runtime data says its frame "
     "can, and the look by day, unmeasured.*"),
    ("*STATUS: OPEN 2026-10-14 -- FOUND BY INSTALL TEST 9: the venv pins three packages and not the nine they bring.",
     "\n\n**256. The venv pins three packages, not the nine they bring.**",
     "*STATUS: CLOSED 2026-10-15 -- Level Factory 0.214.0 (d7c5586): `interpreter.CONSTRAINED` holds the nine at the "
     "versions install test 9 ran, `write_constraints` writes `<venv>/constraints.txt` with all twelve `==` lines "
     "before pip runs and `make_venv` passes it with `-c`, so a constraint fixes a version without asking for the "
     "package and what the base carries stays the base's; `setup --venv`'s line says what is held; "
     "`tests/unit/test_setup_venv.py` restated and extended (the restated test and two new ones fail on 0.213.0, "
     "proven on a copy); the factory's START_HERE.md says the nine come with the three at certified versions. The "
     "doctor's row still asks for imports, not versions. Certified where it is proven: the next install test, "
     "whose `setup` log should download nothing the constraints file does not name.*"),
    ("*STATUS: OPEN 2026-10-15 -- THE WALKER'S ASK, and the work it asks about is DONE and UNSHOWN:",
     "\n\n**257. Level Factory shows its output layers, the light apart from the art.**",
     "*STATUS: CLOSED 2026-10-15 -- Level Factory 0.213.0 (46dc828) and 0.215.1: `output_layers_record` spells the "
     "label by `planner.label_for_layers` and nowhere else; `handoff_layers_text` is HANDOFF.md's last paragraph, "
     "what the package is made of layer by layer and that the light is Lux's result, a layer apart from the art; "
     "an `[export] layers:` log line; the README's Output layers section names three independent layers, Art, "
     "Light and Gameplay, its table gains `--art --unlit` and `export --mode art-unlit`, and a Light bullet says "
     "what the layer is and that the fixtures stay in Art as a contract another lighting system reads; "
     "`docs/RENDER_PASS_SPLIT.md` marked built the other way round. `tests/unit/test_layers_shown.py`, four checks "
     "failing on 0.212.0. Cold run 9314 (0 interventions): `output_layers.json`'s label `graybox+art+gameplay` -> "
     "`graybox+art+light+gameplay`, HANDOFF.md 17 -> 18 lines with the paragraph, the log line, and nothing else "
     "moved but the ground (0.215.0) and the metadata. Found there and fixed in 0.215.1: the paragraph had been "
     "appended without a blank line and read as the last line of the paragraph before it; `handoff_text` joins "
     "them with one, a test on the composed text. The GitHub README is the push of 46dc828.*"),
]

BODY_257 = """

**BUILT, 2026-10-15** (Level Factory 0.213.0, 46dc828; 0.215.1). What a reader meets first now says what the package records: the README's Output layers section, the package's own label, HANDOFF.md's last paragraph and the export's log. Cold run 9314 carries the first package that says it (`docs/cold_runs/cold_9314/NOTES.md`). The only thing that moved in a package besides these is the ground 0.215.0 unshaded."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "BUILT, 2026-10-15** (Level Factory 0.213.0" not in text, "already applied"
    for old_head, heading, new in ITEMS:
        i = text.find(old_head)
        assert i >= 0 and text.count(old_head) == 1, ("status block not found once", old_head[:60])
        j = text.find("\n", i)
        old = text[i:j]
        assert old.endswith("*") and old.count("*STATUS:") == 1, old[-80:]
        text = text[:i] + new + text[j:]
        k = text.find(new)
        assert text[k + len(new):].startswith(heading), ("status no longer adjoins its heading", heading[:50])
    head = "\n\n**257. Level Factory shows its output layers, the light apart from the art.**"
    h = text.find(head)
    assert h > 0 and text.count(head) == 1
    tail = text[h + 2:]
    assert tail.count("\n\n*STATUS:") == 0, "257 is not the last item"
    assert text.endswith("\n") and not text.endswith("\n\n"), repr(text[-5:])
    text = text.rstrip("\n") + BODY_257 + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 252, 256, 257: statuses replaced, one paragraph appended to 257; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
