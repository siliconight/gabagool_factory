"""Level Factory 0.198.0: the reflection atlas sized to the package's probes (factory roadmap 238; measured in
the factory's `docs/findings/texture_memory/`).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  packages/core/godot_project.py      the docstring; `count_package_probes`, `reflection_atlas_count`,
                                      `reflection_atlas_mib`, the engine defaults, `REFLECTION_ATLAS_SIZE`;
                                      `rendering_block(light_count, occluders, probes)` writes the atlas
  packages/exporting/export.py        passes `count_package_probes(export_dir)`
  packages/preview/walk_preview.py    passes `count_package_probes(dest)`
  tests/unit/test_occluders.py        its seven `rendering_block(<int>, <int>)` calls say 0 probes -- one
                                      pattern, asserted to match exactly seven times
  tests/unit/test_lux_interior_dark.py, tests/unit/test_project_godot_agreement.py   one call each
  tests/unit/test_reflection_atlas.py NEW (`lf_reflection_atlas/test_reflection_atlas.py.txt`)
CHANGELOG and VERSION from `lf_reflection_atlas/CHANGELOG_0.198.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written, in this session: `godot_project.py` whole (`count_package_lights`'s glob, the
light cap derived from the package, `rendering_block` and its no-default `occluders`, `set_occlusion_culling`),
`export.py`'s `_write_project_godot` and its import, `walk_preview.py`'s project write and its import,
every `rendering_block(` call in the repository (eleven: two in code, nine in three test files), and
`test_project_godot_agreement.py`'s `_settings` reading. `test_occluders.py` is CRLF, the rest LF.

    python patches/patch_lf_reflection_atlas.py --results-pending
    (python -m pytest -q in level_factory; exit 0 and the tally, docs/COMMANDS.md trap 1)
    python patches/patch_lf_reflection_atlas.py --fill
"""
import hashlib
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reflection_atlas"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.197.0", b"0.198.0"
CHANGELOG_HEAD = "## [0.197.0] - A stoop's railings stand in the frontage with it"
SHA = {"packages/core/godot_project.py": "78dc9d412b7dfee5",
       "packages/exporting/export.py": "26c25f0a7c23acc4",
       "packages/preview/walk_preview.py": "09babe4ebf7e882e",
       "tests/unit/test_occluders.py": "465ea1607d48cee4",
       "tests/unit/test_lux_interior_dark.py": "ac586bda5debdb5c",
       "tests/unit/test_project_godot_agreement.py": "be95231f96a20260"}
NEW = {"tests/unit/test_reflection_atlas.py": "test_reflection_atlas.py.txt"}

GP_DOC_OLD = ("_ready. Absent, unreadable or short of the key, the record contributes\n"
              "nothing and the text count stands alone, as it did before -- an older driver\n"
              "is not a reason to write a smaller cap than 0.86.1 would have.\n"
              "\"\"\"\n")
GP_DOC_NEW = ("_ready. Absent, unreadable or short of the key, the record contributes\n"
              "nothing and the text count stands alone, as it did before -- an older driver\n"
              "is not a reason to write a smaller cap than 0.86.1 would have.\n"
              "\n"
              "THE REFLECTION ATLAS IS DERIVED FROM THE PACKAGE TOO (0.198.0, roadmap 238).\n"
              "Godot allocates it the first time any ReflectionProbe renders, at the size\n"
              "two settings give it, and the defaults -- 64 slots of 256 x 256 x 6 faces in\n"
              "half-float with mips -- are 256 MiB of texture memory: on cold run 9273's\n"
              "package, 257 of its 314.6 MiB, for 23 probes, each an interior room's\n"
              "ambient (the factory's `docs/findings/texture_memory/`). So the slots are the\n"
              "package's probe count rounded up (`reflection_atlas_count`), and the face\n"
              "size is the priced `REFLECTION_ATLAS_SIZE`.\n"
              "\"\"\"\n")

GP_BUDGET_OLD = ("def package_light_budget(root: Path) -> int:\n"
                 "    \"\"\"The light count the `[rendering]` cap is written from: the larger of\n"
                 "    the scene-text count and the driver's census (module docstring).\"\"\"\n"
                 "    text = count_package_lights(root)\n"
                 "    census = lights_reported_by_lux(root)\n"
                 "    return text if census is None else max(text, census)\n")
GP_BUDGET_NEW = GP_BUDGET_OLD + '''

#: THE REFLECTION ATLAS (0.198.0, roadmap 238; module docstring). Fewer slots than
#: probes is not a lever: at 4 slots for 23 probes the engine raised
#: `rpi->atlas_index < 0` 113,494 times and the run stalled in its warm-up.
_PROBE_RE = re.compile(r'type="ReflectionProbe"')
ENGINE_DEFAULT_REFLECTION_COUNT = 64
ENGINE_DEFAULT_REFLECTION_SIZE = 256
#: The face size, priced on cold run 9273's package at its derived stations and
#: twelve interiors against the 256 it shipped with (the factory's
#: `docs/findings/texture_memory/atlas_frames.sh`): at 64 no pixel of any frame
#: moved more than 32 codes and at most 2.7 % moved more than 8, in one drywall
#: room; texture memory 314.6 -> 73.5 MiB at 64 slots. What 128 or 256 would buy
#: back is a sharper reflection on a glossy surface, and the interiors measured are
#: concrete, drywall and brick: the number to raise if a level shows otherwise.
REFLECTION_ATLAS_SIZE = 64


def count_package_probes(root: Path) -> int:
    """ReflectionProbe nodes across every `.tscn` under `root`, globbed as
    `count_package_lights` globs lights. On cold run 9273's package the text's 23
    is the running tree's 23: Lux's room probes ship in its applied scene."""
    total = 0
    for scene in sorted(Path(root).rglob("*.tscn")):
        try:
            text = scene.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        total += len(_PROBE_RE.findall(text))
    return total


def reflection_atlas_count(probes: int) -> int:
    """The atlas's slots for `probes` probes: the next power of two at or above
    the count -- a slot for every probe, and room for one a rig adds at runtime."""
    n = 1
    while n < probes:
        n *= 2
    return n


def reflection_atlas_mib(count: int, size: int) -> float:
    """What an atlas of `count` slots of `size` costs in texture memory, MiB: six
    faces of half-float RGBA (8 bytes a texel) with a mip chain (x 4/3). The
    defaults, 64 x 256, are 256 MiB -- the 257.3 the Warmup's sweep allocated on
    cold run 9273's package -- and 64 x 64 is 16, the 241.1 that face size took away."""
    return count * 6 * size * size * 8 * 4.0 / 3.0 / 2 ** 20
'''

GP_SIG_OLD = "def rendering_block(light_count: int, occluders: int) -> str:\n"
GP_SIG_NEW = "def rendering_block(light_count: int, occluders: int, probes: int) -> str:\n"
GP_DOCARG_OLD = ("    `occluders` has no default ON PURPOSE. Every caller has to have an answer,\n"
                 "    and a walk preview's honest answer is 0.\n"
                 "    \"\"\"\n")
GP_DOCARG_NEW = ("    `occluders` has no default ON PURPOSE. Every caller has to have an answer,\n"
                 "    and a walk preview's honest answer is 0. Nor has `probes` (0.198.0): the\n"
                 "    package's ReflectionProbe count, `count_package_probes` of its folder.\n"
                 "    \"\"\"\n")
GP_ATLAS_OLD = "    # No per-object cap, ON PURPOSE (roadmap 54, closed). Every plate visual\n"
GP_ATLAS_NEW = ("    # THE REFLECTION ATLAS (0.198.0, roadmap 238): written only when the\n"
                "    # package has a probe -- the atlas is allocated the first time one\n"
                "    # renders, so a package with none never pays for it.\n"
                "    if probes > 0:\n"
                "        out += [\n"
                "            \"; REFLECTION ATLAS -- sized to this package's reflection probes. Godot's\",\n"
                "            \"; default, 64 slots of 256 x 256 x 6 half-float with mips, is 256 MiB of\",\n"
                "            \"; texture memory the first time any probe renders (cold run 9273's package:\",\n"
                "            \"; 257 of its 314.6 MiB). The slots are this package's probe count,\",\n"
                "            f\"; {probes}, rounded up to a power of two: fewer slots than probes floods\",\n"
                "            \"; the log and stalls the frame. The face size is the priced one.\",\n"
                "            f\"reflections/reflection_atlas/reflection_count={reflection_atlas_count(probes)}\",\n"
                "            f\"reflections/reflection_atlas/reflection_size={REFLECTION_ATLAS_SIZE}\",\n"
                "        ]\n"
                "\n"
                "    # No per-object cap, ON PURPOSE (roadmap 54, closed). Every plate visual\n")

EX_IMPORT_OLD = ("from packages.core.godot_project import (package_light_budget,\n"
                 "                                          rendering_block,\n"
                 "                                          set_occlusion_culling, shader_globals_block)\n")
EX_IMPORT_NEW = ("from packages.core.godot_project import (count_package_probes,\n"
                 "                                          package_light_budget,\n"
                 "                                          rendering_block,\n"
                 "                                          set_occlusion_culling, shader_globals_block)\n")
EX_CALL_OLD = "        + rendering_block(package_light_budget(export_dir), 0)\n"
EX_CALL_NEW = ("        # the reflection atlas from the probes in this folder (0.198.0)\n"
               "        + rendering_block(package_light_budget(export_dir), 0,\n"
               "                          count_package_probes(export_dir))\n")

WP_IMPORT_OLD = ("from packages.core.godot_project import (package_light_budget,\n"
                 "                                          rendering_block)\n")
WP_IMPORT_NEW = ("from packages.core.godot_project import (count_package_probes,\n"
                 "                                          package_light_budget,\n"
                 "                                          rendering_block)\n")
WP_CALL_OLD = ("                        rendering=rendering_block(\n"
               "                            package_light_budget(dest), 0)), encoding=\"utf-8\")\n")
WP_CALL_NEW = ("                        # and the reflection atlas from its probes (0.198.0)\n"
               "                        rendering=rendering_block(\n"
               "                            package_light_budget(dest), 0,\n"
               "                            count_package_probes(dest))), encoding=\"utf-8\")\n")

EDITS = {
    "packages/core/godot_project.py": [(GP_DOC_OLD, GP_DOC_NEW), (GP_BUDGET_OLD, GP_BUDGET_NEW),
                                       (GP_SIG_OLD, GP_SIG_NEW), (GP_DOCARG_OLD, GP_DOCARG_NEW),
                                       (GP_ATLAS_OLD, GP_ATLAS_NEW)],
    "packages/exporting/export.py": [(EX_IMPORT_OLD, EX_IMPORT_NEW), (EX_CALL_OLD, EX_CALL_NEW)],
    "packages/preview/walk_preview.py": [(WP_IMPORT_OLD, WP_IMPORT_NEW), (WP_CALL_OLD, WP_CALL_NEW)],
    "tests/unit/test_lux_interior_dark.py": [
        ("rendering=rendering_block(package_light_budget(tmp_path), 0)))",
         "rendering=rendering_block(package_light_budget(tmp_path), 0, 0)))")],
    "tests/unit/test_project_godot_agreement.py": [
        ("rendering=rendering_block(count_package_lights(tmp_path), 0))",
         "rendering=rendering_block(count_package_lights(tmp_path), 0, 0))")],
}
#: (file, pattern, replacement, how many times it must match)
PATTERNS = [("tests/unit/test_occluders.py", r"rendering_block\((\d+), (\d+)\)", r"rendering_block(\1, \2, 0)", 7)]


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.198.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.198.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.198.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.198.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    texts, eols = {}, {}
    for rel in SHA:
        raw = (LF / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eols[rel] = _eol(raw, rel)
        texts[rel] = raw.decode("utf-8").replace("\r\n", "\n")
    for rel, pairs in EDITS.items():
        for old, new in pairs:
            assert texts[rel].count(old) == 1, (rel, "anchor", texts[rel].count(old), old[:80])
            texts[rel] = texts[rel].replace(old, new)
    for rel, pat, rep, want in PATTERNS:
        texts[rel], n = re.subn(pat, rep, texts[rel])
        assert n == want, (rel, pat, "matched", n, "not", want)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, text in texts.items():
        (LF / rel).write_bytes(text.encode("utf-8").replace(b"\n", eols[rel]))
    for rel, data in news.items():
        (LF / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.197.0 -> 0.198.0")


if __name__ == "__main__":
    main()
