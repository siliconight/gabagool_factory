"""Roadmap 257: Level Factory shows its output layers, the light apart from the art (the walker, 2026-10-15).

Appends item 257 after 256, the file's last item, with its status block above its heading. The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it. Asserts the roadmap is LF,
that 256's heading is the last line, that no 257 exists, and that no body line starts like an item.

    python patches/patch_roadmap_257_output_layers.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
LAST_ITEM_HEAD = "**256. The venv pins three packages, not the nine they bring.**"

ITEM = """
*STATUS: OPEN 2026-10-15 -- THE WALKER'S ASK, and the work it asks about is DONE and UNSHOWN: light has been its own layer since Level Factory 0.35.0 (`LAYER_LIGHT`, declined with `--unlit`) and `export --mode art-unlit` since 0.36.0, and the package records it (`LF_MANIFEST.json`, `output_layers.json`: `["art", "gameplay", "light"]`); the README's Output layers section, the package's label, HANDOFF.md and the export's log do not say so. Level Factory's; what would close it is below.*

**257. Level Factory shows its output layers, the light apart from the art.** The walker, 2026-10-15: "I want Level Factory to clearly show the output layers calling out how lighting/render is separate from art ... I thought we did the work to make that another step in the output layers?" **Measured that morning, on the checkout at 0.212.0 and cold run 9312's package.** The work was done: `docs/RENDER_PASS_SPLIT.md` (2026-08-05) proposed taking Lux out of `--art` behind a `--render` flag; 0.35.0 built it the other way round, as a layer a run can DECLINE -- `LAYER_LIGHT` is `lux_apply` alone, `--unlit` leaves it out, `--art` still lights the level by default, and the fixtures (Zoo's hardware, the `lux_fixture_gate`) stay in the art because a dark fixture is broken geometry whoever lights it; 0.36.0 added `export --mode art-unlit`, the same build shipped without Lux's result, so a recipient can compare one geometry under two lighting solutions. The package says it: `LF_MANIFEST.json` and `output_layers.json` both list `layers: ["art", "gameplay", "light"]`. **What does not say it, each read off the files:** (1) `level_factory/README.md`'s Output layers section -- the repo's front page on GitHub -- still describes a Graybox base and two optional layers, Art and Gameplay, lists Lux inside `--art`'s row, and names neither `light`, `--unlit` nor `art-unlit` anywhere (grep: 0 lines). (2) `output_layers.json`'s `label` reads `graybox+art+gameplay` for a package whose `layers` carry `light`: `packages/exporting/export.py` composes it from `("art", "gameplay")` alone, while `packages/pipeline/planner.label_for_layers` composes `graybox+art+light+gameplay` for the same set -- two spellings of one label, the shape CLAUDE.md's threshold rule names. (3) `HANDOFF.md`, the page a recipient reads first, says nothing about layers (17 lines: the player contract and the manifest). (4) The export's log prints no layers line. (5) `RENDER_PASS_SPLIT.md` still opens "Not implemented". **WHAT WOULD CLOSE IT, in Level Factory:** the README's Output layers table gains the light row and the two commands that decline it (`run --art --unlit`, `export --mode art-unlit`) with one sentence on what stays in the art (the fixtures and their `LuxEmit` markers, a contract another lighting system reads); `output_layers.json`'s label spelled by `planner.label_for_layers` and nowhere else, with a test that a package carrying light says so; a HANDOFF.md paragraph naming the layers this package carries and that the light is Lux's result, separable from the art it lights; an `[export] layers:` log line; and the design doc marked built, with the flag as it shipped. A doc-and-label change, no geometry: proven by the suite and by one export's files, no cold run owed.
"""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**257. " not in text, "already applied"
    last = text.rstrip("\n").rsplit("\n", 1)[-1]
    assert last.startswith(LAST_ITEM_HEAD) and text.count(LAST_ITEM_HEAD) == 1, last[:80]
    assert text.endswith("\n") and not text.endswith("\n\n"), repr(text[-5:])
    for line in ITEM.splitlines()[1:]:
        assert not (line.startswith("**") and line[2:3].isdigit()) or line.startswith("**257. "), line[:40]
    RM.write_bytes((text + ITEM).encode("utf-8"))
    print("roadmap 257 appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
