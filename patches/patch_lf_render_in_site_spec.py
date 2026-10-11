"""Level Factory 0.178.0: the site spec tells Lot the package will bake its lights (roadmap 231,
the second lever, beside Lot 0.115.0).

Anchored edits in `packages/exporting/export.py` (`BAKE_LIGHTS_CLI_DEFAULT`), `apps/cli/main.py`
(the `--bake-lights` default reads it) and `apps/cli/commands/__init__.py` (`_write_site_spec`
writes `render.lights_baked`; `cmd_export` says out loud when `--no-bake-lights` leaves a site
drawn for a bake), and a new `tests/unit/test_render_in_site_spec.py`; each file pinned by hash
and each anchor asserted once, nothing written on a miss; the file's own line endings kept.
CHANGELOG and VERSION from `lf_render_in_site_spec/CHANGELOG_0.178.0.md`; `--suite-pending`
leaves RESULT_SUITE to `--fill`.

    python patches/patch_lf_render_in_site_spec.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_render_in_site_spec.py --fill
    LF_ROOT=<copy> python patches/patch_lf_render_in_site_spec.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_render_in_site_spec"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.177.2", b"0.178.0"
CHANGELOG_HEAD = "## [0.177.2] - The Lot adapter publishes the paint meshes\n"
SHA = {"packages/exporting/export.py": "863215629b169131",
       "apps/cli/main.py": "81a7277813e26ef8",
       "apps/cli/commands/__init__.py": "d1f152d36c65bf98"}
NEW_TEST = "tests/unit/test_render_in_site_spec.py"

EXP_OLD = "@dataclass\nclass ExportProfile:\n"
EXP_NEW = ("#: Whether `export` bakes the lights unless told otherwise (0.178.0, roadmap\n"
           "#: 231): the command line's default since 0.144.0, now ONE constant read by\n"
           "#: the parser (`apps/cli/main.py`) and by the site spec writer, which tells\n"
           "#: Lot the package will bake (`render.lights_baked`) so Lot can cut its\n"
           "#: plates for a lightmapped package (Lot 0.115.0's MESH_TILE_BAKED; the\n"
           "#: culler pairs no baked light with a lightmapped mesh). `ExportProfile`\n"
           "#: itself stays off, as its comment below says.\n"
           "BAKE_LIGHTS_CLI_DEFAULT = True\n"
           "\n"
           "\n"
           "@dataclass\nclass ExportProfile:\n")

MAIN_IMP_OLD = "    cmd_walk,\n)\n\nEXIT_OK = 0\n"
MAIN_IMP_NEW = ("    cmd_walk,\n)\n"
                "from packages.exporting.export import BAKE_LIGHTS_CLI_DEFAULT  # noqa: E402\n"
                "\nEXIT_OK = 0\n")
MAIN_ARG_OLD = ('    sp.add_argument("--bake-lights", action=argparse.BooleanOptionalAction, '
                'default=True,\n')
MAIN_ARG_NEW = ('    sp.add_argument("--bake-lights", action=argparse.BooleanOptionalAction,\n'
                '                    default=BAKE_LIGHTS_CLI_DEFAULT,\n')

CMD_IMP_OLD = ("    from packages.pipeline import road_grammar, site_variation\n"
               "    from packages.pipeline.site_variation import (\n"
               "        STREET, ground_size, row_spacing, shell_footprint, site_placements)\n")
CMD_IMP_NEW = ("    from packages.exporting.export import BAKE_LIGHTS_CLI_DEFAULT\n" + CMD_IMP_OLD)
CMD_SPEC_OLD = '        "road_grammar": model.road_grammar,\n'
CMD_SPEC_NEW = ('        # THE PACKAGE BAKES ITS LIGHTS (0.178.0, roadmap 231): said to Lot here,\n'
                '        # because Lot cuts its plates for the per-mesh light cap and a\n'
                '        # lightmapped mesh pairs with no baked light (Lot 0.115.0\'s\n'
                '        # MESH_TILE_BAKED, 0.159.0\'s paired census). The export\'s own default,\n'
                '        # one constant; `export --no-bake-lights` says out loud that the site\n'
                '        # was drawn for a bake it did not get.\n'
                '        "render": {"lights_baked": bool(BAKE_LIGHTS_CLI_DEFAULT)},\n'
                + CMD_SPEC_OLD)
CMD_EXPIMP_OLD = "        MODES, ExportProfile, export_mission, zip_export,\n"
CMD_EXPIMP_NEW = "        BAKE_LIGHTS_CLI_DEFAULT, MODES, ExportProfile, export_mission, zip_export,\n"
CMD_NOTE_OLD = ("    profile = ExportProfile(mode=args.mode,\n"
                "                            include_walk=bool(getattr(args, \"include_walk\", False)),\n"
                "                            weather=weather,\n"
                "                            bake_lights=bool(getattr(args, \"bake_lights\", False)))\n")
CMD_NOTE_NEW = (CMD_NOTE_OLD +
                "    if not profile.bake_lights and BAKE_LIGHTS_CLI_DEFAULT:\n"
                "        # The site spec told Lot the package would bake (0.178.0), so its\n"
                "        # plates are cut to the baked tile (Lot 0.115.0, 32 m) rather than the\n"
                "        # 8 m priced against live lights. Said, not refused: the perf report's\n"
                "        # paired light census is the per-mesh cap's gate.\n"
                "        print(\"  lights NOT baked: the site was drawn for a bake (render.lights_baked), \"\n"
                "              \"its plates tiled for one; the perf report's paired light census is \"\n"
                "              \"the per-mesh cap's gate\")\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Level Factory 0.178.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.178.0.md")
    assert entry.startswith("## [0.178.0] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    assert not (LF / NEW_TEST).exists(), f"{NEW_TEST} already exists"

    ep, e_eol, exp = _read("packages/exporting/export.py")
    assert "BAKE_LIGHTS_CLI_DEFAULT" not in exp, "already applied"
    exp = _once(exp, EXP_OLD, EXP_NEW, "ExportProfile")

    mp, m_eol, mn = _read("apps/cli/main.py")
    mn = _once(mn, MAIN_IMP_OLD, MAIN_IMP_NEW, "main import")
    mn = _once(mn, MAIN_ARG_OLD, MAIN_ARG_NEW, "main --bake-lights")

    cp, c_eol, cmds = _read("apps/cli/commands/__init__.py")
    cmds = _once(cmds, CMD_IMP_OLD, CMD_IMP_NEW, "_write_site_spec import")
    cmds = _once(cmds, CMD_SPEC_OLD, CMD_SPEC_NEW, "site spec render")
    cmds = _once(cmds, CMD_EXPIMP_OLD, CMD_EXPIMP_NEW, "cmd_export import")
    cmds = _once(cmds, CMD_NOTE_OLD, CMD_NOTE_NEW, "cmd_export note")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    test = _src("test_render_in_site_spec.py.txt")
    # Every pin and anchor matched: now write.
    ep.write_bytes(exp.replace("\n", e_eol.decode()).encode("utf-8"))
    mp.write_bytes(mn.replace("\n", m_eol.decode()).encode("utf-8"))
    cp.write_bytes(cmds.replace("\n", c_eol.decode()).encode("utf-8"))
    (LF / NEW_TEST).write_bytes(test.replace("\n", c_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.177.1 -> 0.178.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
