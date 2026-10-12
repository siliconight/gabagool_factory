"""REFUTED, NOT APPLIED (2026-10-11). Kept as the record of what was tried; `main` refuses to run.

Re-exporting cold run 9251 with it applied FAILED the greybox-skin gate: 105 slab surfaces still on
a greybox material (good exports: 3), the Empties merged to 148 meshes instead of 236, and the
bake lit 3,320 users instead of 3,491. The light bake's re-import of every model is load-bearing:
it is the import in which `zoo_worldskin.gd` skins the models with the texture packs already
imported. With lightmap UVs asked for in the first, cold pass, that pass was the models' last
import, and the worldskin could not find its packs for the slabs. `import_plan_probe.py`'s
equivalence compared sidecars only, and a sidecar does not record what the import script did.
(`docs/findings/grader_speed/README.md`.) What follows is the original docstring.

Level Factory 0.186.0: the export's first import pass imports the models as they ship (embedded
images, lightmap UVs when baking), so neither the second pass nor the light bake imports them again
(factory roadmap 239, the export's imports).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/export.py     `FIRST_PASS_SCENE_DEFAULTS`, `FIRST_PASS_LIGHTMAP_DEFAULTS` and
                                   `_first_pass_defaults` before `_write_import_sidecars`, which takes
                                   `lightmaps`, runs its first pass with them in `project.godot`'s
                                   model defaults and puts the file back byte for byte, wipes the cache
                                   for a full second pass only when a model's sidecar was rewritten,
                                   and otherwise re-imports just what the pins changed; the export
                                   passes `lightmaps=profile.bake_lights`
  packages/exporting/light_bake.py `STATIC`; `mark_imports` writes it for a model whose second UV set
                                   is shader data instead of leaving the engine's default to stand
  tests/unit/test_import_once.py   NEW, from `lf_import_once/`
CHANGELOG and VERSION from `lf_import_once/CHANGELOG_0.186.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

    python patches/patch_lf_import_once.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_import_once.py --fill
    LF_ROOT=<copy> python patches/patch_lf_import_once.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_import_once"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.185.0", b"0.186.0"
CHANGELOG_HEAD = ("## [0.185.0] - Blender jobs run three at a time where the machine allows, the "
                  "width cold run 9251 measured\n")
EXPORT = "packages/exporting/export.py"
BAKE = "packages/exporting/light_bake.py"
TEST = "tests/unit/test_import_once.py"
SHA = {EXPORT: "dde99794ebd0c3d5", BAKE: "9a306665d0fbf1aa"}

E_DEF_OLD = "def _write_import_sidecars(export_dir: Path, godot_executable) -> int:\n"
E_DEF_NEW = (
    "#: The model importer's defaults the export's FIRST import pass runs with\n"
    "#: (0.186.0), and only that pass: every model then has a sidecar, defaults\n"
    "#: reach no file that has one, and `project.godot` is put back byte for byte\n"
    "#: before anything else reads it, so the package ships the file it always did.\n"
    "#: Embedded images were a rewrite between two passes, the second after the cache\n"
    "#: was wiped; Static Lightmaps was `light_bake.mark_imports`' rewrite before an\n"
    "#: import of every model again for its lightmap UVs -- the pass that imported the\n"
    "#: shared textures 1,843 times and reset 62 to 86 of their pins (0.182.0).\n"
    "FIRST_PASS_SCENE_DEFAULTS = {\"gltf/embedded_image_handling\": 3}\n"
    "FIRST_PASS_LIGHTMAP_DEFAULTS = {\"meshes/light_baking\": 2}\n"
    "\n"
    "\n"
    "def _first_pass_defaults(text: str, lightmaps: bool) -> str:\n"
    "    \"\"\"`project.godot`'s text with the first pass's model defaults in its\n"
    "    `[importer_defaults] scene` dictionary, which is made if it is missing.\"\"\"\n"
    "    keys = dict(FIRST_PASS_SCENE_DEFAULTS)\n"
    "    if lightmaps:\n"
    "        keys.update(FIRST_PASS_LIGHTMAP_DEFAULTS)\n"
    "    lines = \",\\n\".join('\"%s\": %s' % (k, v) for k, v in keys.items())\n"
    "    section, head = \"[importer_defaults]\\n\", \"scene={\\n\"\n"
    "    if section in text and head in text[text.index(section):]:\n"
    "        i = text.index(head, text.index(section)) + len(head)\n"
    "        j = text.index(\"}\", i)\n"
    "        body = text[i:j].rstrip(\"\\n\")\n"
    "        return text[:i] + (body + \",\\n\" if body.strip() else \"\") + lines + \"\\n\" + text[j:]\n"
    "    if section in text:\n"
    "        k = text.index(section) + len(section)\n"
    "        return text[:k] + \"\\n\" + head + lines + \"\\n}\\n\" + text[k:]\n"
    "    return text.rstrip(\"\\n\") + \"\\n\\n\" + section + \"\\n\" + head + lines + \"\\n}\\n\"\n"
    "\n"
    "\n"
    "def _write_import_sidecars(export_dir: Path, godot_executable, *,\n"
    "                           lightmaps: bool = False) -> int:\n")
E_P1_OLD = ("    _import_pass_verified()\n"
            "\n"
            "    KEY = \"gltf/embedded_image_handling\"\n")
E_P1_NEW = ("    # THE FIRST PASS IMPORTS THE MODELS AS THEY SHIP (0.186.0):\n"
            "    # `FIRST_PASS_SCENE_DEFAULTS`, and `FIRST_PASS_LIGHTMAP_DEFAULTS` when the\n"
            "    # export will bake, then `project.godot` back as it was.\n"
            "    proj = export_dir / \"project.godot\"\n"
            "    kept = proj.read_bytes() if proj.is_file() else None\n"
            "    if kept is not None:\n"
            "        p_eol = \"\\r\\n\" if b\"\\r\\n\" in kept else \"\\n\"\n"
            "        first = _first_pass_defaults(kept.decode(\"utf-8\").replace(\"\\r\\n\", \"\\n\"), lightmaps)\n"
            "        proj.write_bytes(first.replace(\"\\n\", p_eol).encode(\"utf-8\"))\n"
            "    try:\n"
            "        _import_pass_verified()\n"
            "    finally:\n"
            "        if kept is not None:\n"
            "            proj.write_bytes(kept)\n"
            "\n"
            "    KEY = \"gltf/embedded_image_handling\"\n")
E_PINS_OLD = ("    rewrote += _pin_shared_texture_imports(export_dir)\n"
              "    rewrote += _pin_sign_texture_imports(export_dir)\n"
              "\n"
              "    if rewrote:\n")
E_PINS_NEW = ("    models_rewrote = rewrote\n"
              "    rewrote += _pin_shared_texture_imports(export_dir)\n"
              "    rewrote += _pin_sign_texture_imports(export_dir)\n"
              "\n"
              "    if models_rewrote:\n")
E_P2_OLD = ("        _shutil.rmtree(export_dir / \".godot\", ignore_errors=True)\n"
            "        _import_pass_verified()\n")
E_P2_NEW = ("        _shutil.rmtree(export_dir / \".godot\", ignore_errors=True)\n"
            "        _import_pass_verified()\n"
            "    elif rewrote:\n"
            "        # ONLY THE TEXTURES' PINS CHANGED (0.186.0): the models imported as\n"
            "        # they ship, so nothing was extracted and the cache stays; Godot\n"
            "        # re-imports just the sidecars whose parameters moved. Measured on cold\n"
            "        # run 9251's package: 8.6 s, where the wipe and the full pass took 39.\n"
            "        _import_pass_verified()\n")
E_CALL_OLD = "    _write_import_sidecars(export_dir, godot_executable)\n"
E_CALL_NEW = "    _write_import_sidecars(export_dir, godot_executable, lightmaps=profile.bake_lights)\n"

B_C_OLD = "LIGHT_BAKING = \"meshes/light_baking\"\nSTATIC_LIGHTMAPS = 2\n"
B_C_NEW = ("LIGHT_BAKING = \"meshes/light_baking\"\n"
           "STATIC_LIGHTMAPS = 2\n"
           "#: `meshes/light_baking` Static: lit by the bake, no lightmap UVs of its own --\n"
           "#: the engine's default, which a model whose second UV set is shader data has\n"
           "#: always shipped with. Written since 0.186.0, when the first import may run\n"
           "#: with Static Lightmaps as the default.\n"
           "STATIC = 1\n")
B_M_OLD = ("        elif glb_has_uv2(glb):\n"
           "            out[\"dynamic\"].append(rel)\n"
           "            continue\n")
B_M_NEW = ("        elif glb_has_uv2(glb):\n"
           "            # its second UV set is shader data: no lightmap UVs, and said so\n"
           "            # rather than left to a default the first import may have changed\n"
           "            value, bucket = STATIC, \"dynamic\"\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.186.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.186.0: results filled")


def main():
    sys.exit("refused: this patch is REFUTED (its docstring says why) and must not be applied")
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.186.0.md")
    assert entry.startswith("## [0.186.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_import_once.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    ep, e_eol, export = _read(EXPORT)
    assert "FIRST_PASS_SCENE_DEFAULTS" not in export, "already applied"
    export = _once(export, E_DEF_OLD, E_DEF_NEW, "_write_import_sidecars' definition")
    export = _once(export, E_P1_OLD, E_P1_NEW, "the first pass")
    export = _once(export, E_PINS_OLD, E_PINS_NEW, "the pins and the second pass's condition")
    export = _once(export, E_P2_OLD, E_P2_NEW, "the second pass")
    export = _once(export, E_CALL_OLD, E_CALL_NEW, "the export's call")
    bp, b_eol, bake = _read(BAKE)
    bake = _once(bake, B_C_OLD, B_C_NEW, "the light-baking constants")
    bake = _once(bake, B_M_OLD, B_M_NEW, "mark_imports' shader-UV2 branch")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(ep, e_eol, export)
    _write(bp, b_eol, bake)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.185.0 -> 0.186.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
