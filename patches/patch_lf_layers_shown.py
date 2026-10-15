"""Level Factory 0.213.0: the output layers, shown -- the light apart from the art (the factory's roadmap 257,
the walker's ask of 2026-10-15).

  README.md                        the intro's three layers; the Output layers table and bullets; the flags line
  packages/exporting/export.py     `output_layers_record`, `handoff_layers_text`; the label spelled by the
                                   planner; HANDOFF.md's last paragraph; an `[export] layers:` line
  docs/RENDER_PASS_SPLIT.md        marked built, the other way round
  tests/unit/test_layers_shown.py  new, from `lf_layers_shown/test_layers_shown.py.txt`

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. The README's em
dashes (U+2014) and arrows (U+2192) are spelled as escapes here and asserted like any other anchor. CHANGELOG and
VERSION from `lf_layers_shown/CHANGELOG_0.213.0.md`; `--results-pending` leaves RESULT_SUITE to `--fill`. The
package proof -- the two files that move, `output_layers.json` and `HANDOFF.md` -- is the next cold run's, in
its NOTES at the factory root, as 0.211.0's ground was proven.

Read before it was written, in this session: README.md 9-14 and 36-62 (the intro and the Output layers section,
their non-ASCII codepoints printed); export.py 34-66 (the modes, `ships_lux`), 71-112 (`HANDOFF_LANGUAGE`),
1836-1850 (how `layers` is decided, the light taken out for an unlit mode), 2203-2216 (the HANDOFF write) and
2520-2560 (the output_layers write and the closure verdict's print); planner.py 103-116 (`label_for_layers`);
the tests that pin the label (`test_light_layer.py` 59-62, `test_planner_graph.py` 211-222) and the manifest's
listing of `output_layers.json` (`test_manifest_lists_what_ships.py`); RENDER_PASS_SPLIT.md 1-40. Every file LF.

    python patches/patch_lf_layers_shown.py --results-pending
    (the suite in level_factory; COMMANDS.md trap 1: tally the progress characters; then a cold run's package)
    python patches/patch_lf_layers_shown.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_layers_shown"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.212.0", b"0.213.0"
CHANGELOG_HEAD = "## [0.212.0] - The light bake counts what it bakes"
SHA = {"README.md": "74941ad7ffec8235",
       "packages/exporting/export.py": "2a6d1d69a2494816",
       "docs/RENDER_PASS_SPLIT.md": "3e98aecc1a2b483d"}
NEW = {"tests/unit/test_layers_shown.py": "test_layers_shown.py.txt"}

DASH, ARROW = "—", "→"

README_INTRO_OLD = ("**Graybox** base and two independent, optional layers " + DASH + " **Art** and **Gameplay** "
                    + DASH + "\n")
README_INTRO_NEW = ("**Graybox** base and three independent, optional layers " + DASH
                    + " **Art**, **Light** and **Gameplay** " + DASH + "\n")

README_TABLE_OLD = (
    "run <mission>                  " + ARROW + " graybox            DC greybox + collision, assembled by Lot (+ Laser Tag nav QA)\n"
    "run <mission> --art            " + ARROW + " graybox + art      Zoo swaps + props/dressing, Pixelcoat, Patina, Lux\n"
    "run <mission> --gameplay       " + ARROW + " graybox + gameplay Dispatch objective/nav/spawn suggestions (advisory)\n"
    "run <mission> --art --gameplay " + ARROW + " full stack         art pass + Dispatch over the art scene\n")
README_TABLE_NEW = (
    "run <mission>                     " + ARROW + " graybox                DC greybox + collision, assembled by Lot (+ Laser Tag nav QA)\n"
    "run <mission> --art               " + ARROW + " graybox + art + light  Zoo swaps + props/dressing, Pixelcoat, Patina; then Lux, the light\n"
    "run <mission> --art --unlit       " + ARROW + " graybox + art          the same art pass with no light: for a runtime that lights it itself\n"
    "run <mission> --gameplay          " + ARROW + " graybox + gameplay     Dispatch objective/nav/spawn suggestions (advisory)\n"
    "run <mission> --art --gameplay    " + ARROW + " full stack             art + light, and Dispatch over the art scene\n"
    "export <mission> --mode art-unlit " + ARROW + " the lit build shipped without its light, the art and its fixtures unchanged\n")

README_ART_OLD = "  dressing), Pixelcoat skins, Patina cohesion, Lux the runtime look. It never\n"
README_ART_NEW = "  dressing), Pixelcoat skins, Patina cohesion. It never\n"

README_GAMEPLAY_OLD = "- **Gameplay** is Dispatch's advisory objective layer (spawns, objectives, nav\n"
README_LIGHT_NEW = (
    "- **Light** is Lux's apply pass alone -- the lights, the exposure, the baked\n"
    "  lightmap: the render decisions, which are separate from what the level is\n"
    "  made of. `--art` includes it; `--unlit` leaves it out, and `export --mode\n"
    "  art-unlit` ships a lit build without it. The light *fixtures* stay in Art\n"
    "  (Zoo builds the hardware from the locked shell, `lux_fixture_gate` checks\n"
    "  it), with their `LuxEmit` markers, so another lighting system reads them as\n"
    "  a contract rather than a guess (0.35.0, 0.36.0; `docs/RENDER_PASS_SPLIT.md`).\n"
    + README_GAMEPLAY_OLD)

README_FLAGS_OLD = "`--art`/`--gameplay` are independent flags; bare `run` is graybox. The legacy\n"
README_FLAGS_NEW = "`--art`, `--unlit` and `--gameplay` are independent flags; bare `run` is graybox. The legacy\n"

EXPORT_HELPERS_OLD = "    return mode not in UNLIT_MODES\n"
EXPORT_HELPERS_NEW = EXPORT_HELPERS_OLD + '''

def output_layers_record(layers) -> dict:
    """`output_layers.json`: the layers this package carries, and its label in
    ONE spelling, the planner's (0.213.0, the factory's roadmap 257). This file
    spelled the label from `("art", "gameplay")` alone while
    `planner.label_for_layers` spelled the whole set, so a package carrying
    the light said `graybox+art+gameplay` of itself."""
    from packages.pipeline.planner import label_for_layers
    layers = sorted(layers or ())
    return {"schema": "level_factory.output_layers.v0.1", "layers": layers,
            "label": label_for_layers(layers)}


def handoff_layers_text(layers, mode: str) -> str:
    """HANDOFF.md's last paragraph (0.213.0, the factory's roadmap 257): what
    this package is made of, layer by layer, and that the light is Lux's
    result, a layer apart from the art it lights. `output_layers.json` and
    `LF_MANIFEST.json` carry the same names."""
    from packages.pipeline.planner import LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT
    layers = frozenset(layers or ())
    parts = ["the graybox base (Deli Counter's shells with their collision, "
             "assembled by Lot, with navigation)"]
    if LAYER_ART in layers:
        parts.append("the ART layer (Zoo's themed modules, props and dressing, "
                     "Pixelcoat's skins, Patina's cohesion -- and the light "
                     "FIXTURES, which are geometry whoever lights them, with "
                     "their `LuxEmit` markers)")
    if LAYER_LIGHT in layers:
        parts.append("the LIGHT layer (Lux's applied scene and its baked "
                     "lightmap: the render decisions)")
    if LAYER_GAMEPLAY in layers:
        parts.append("the GAMEPLAY layer (Dispatch's advisory objectives, "
                     "spawns and navigation hints)")
    text = "WHAT THIS PACKAGE IS MADE OF: " + "; ".join(parts) + ". "
    text += "THE LIGHT IS A LAYER OF ITS OWN, APART FROM THE ART. "
    if LAYER_LIGHT in layers:
        text += ("This package carries it. The same build exports without it as "
                 "`--mode art-unlit` -- the art and its fixtures unchanged -- for "
                 "a runtime that brings its own lighting.")
    elif mode == MODE_ART_UNLIT:
        text += ("This package was exported `art-unlit`: the art and its fixtures "
                 "with no Lux result. Light it yourself, or export the same build "
                 "`portable-godot` for Lux's.")
    else:
        text += "This package carries no light layer."
    return text + " `output_layers.json` and `LF_MANIFEST.json` name the layers.\\n"
'''

EXPORT_LABEL_OLD = (
    '    parts = ["graybox"] + [x for x in ("art", "gameplay") if x in layers]\n'
    '    (export_dir / "output_layers.json").write_text(pretty_dumps({\n'
    '        "schema": "level_factory.output_layers.v0.1",\n'
    '        "layers": sorted(layers), "label": "+".join(parts),\n'
    '    }), encoding="utf-8")\n')
EXPORT_LABEL_NEW = (
    '    record = output_layers_record(layers)\n'
    '    (export_dir / "output_layers.json").write_text(pretty_dumps(record), encoding="utf-8")\n'
    '    # `LAYER_LIGHT` is "light" (pinned by test_layers_shown); the record carries strings\n'
    '    print("[export] layers: %s (%s); the light is Lux\'s result, a layer apart from the art%s"\n'
    '          % (", ".join(record["layers"]) or "none, the graybox alone", record["label"],\n'
    '             "" if "light" in record["layers"] else " -- this package carries none"))\n')

EXPORT_HANDOFF_OLD = '    (export_dir / "HANDOFF.md").write_text(HANDOFF_LANGUAGE, encoding="utf-8")\n'
EXPORT_HANDOFF_NEW = ('    (export_dir / "HANDOFF.md").write_text(\n'
                      '        HANDOFF_LANGUAGE + handoff_layers_text(layers, profile.mode), encoding="utf-8")\n')

DOC_OLD = "**Raised 2026-08-05.** Not implemented; captured so it does not get lost.\n"
DOC_NEW = ("**Raised 2026-08-05. BUILT in 0.35.0 and 0.36.0, the other way round:** light is\n"
           "a layer a run DECLINES (`--unlit`), not one it adds (`--render`). `LAYER_LIGHT`\n"
           "is `lux_apply` alone, `--art` still lights the level by default, and `export\n"
           "--mode art-unlit` ships a lit build without Lux's result; the fixtures stay in\n"
           "the art. Kept below as it was proposed. The README's Output layers section says\n"
           "what shipped (0.213.0, the factory's roadmap 257).\n")

EDITS = {
    "README.md": [(README_INTRO_OLD, README_INTRO_NEW), (README_TABLE_OLD, README_TABLE_NEW),
                  (README_ART_OLD, README_ART_NEW), (README_GAMEPLAY_OLD, README_LIGHT_NEW),
                  (README_FLAGS_OLD, README_FLAGS_NEW)],
    "packages/exporting/export.py": [(EXPORT_HELPERS_OLD, EXPORT_HELPERS_NEW),
                                     (EXPORT_LABEL_OLD, EXPORT_LABEL_NEW),
                                     (EXPORT_HANDOFF_OLD, EXPORT_HANDOFF_NEW)],
    "docs/RENDER_PASS_SPLIT.md": [(DOC_OLD, DOC_NEW)],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.213.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.213.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.213.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.213.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in SHA:
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in EDITS[rel]:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        p = LF / rel
        assert not p.exists(), (rel, "already exists")
        writes[p] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Level Factory 0.212.0 -> 0.213.0")


if __name__ == "__main__":
    main()
