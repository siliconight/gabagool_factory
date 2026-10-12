"""Level Factory 0.194.0: a site's overhead wires stay out of the lightmap (factory roadmap 240, the
pole line's wires -- Lot 0.119.0 draws them as `site_wires_*.obj` beside the scene).

Anchored edits, each asserted once, nothing written until all of them matched:
  packages/exporting/light_bake.py   `UNLIT_PREFIXES` before `mark_imports`; its report gains
                                     `unlit`; an OBJ whose name starts with one is listed there and
                                     its sidecar left as the engine wrote it, never asked for a
                                     lightmap UV
  tests/unit/test_wires_unlit.py     NEW
  tests/unit/test_light_bake.py      the test pinning `mark_imports`' whole report gains `unlit`
                                     (the first application missed it: the suite's one failure)
CHANGELOG and VERSION from `lf_wires_unlit/CHANGELOG_0.194.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: light_bake.py's `mark_imports` (0.177.1 asks every `*.obj.import` for a
lightmap UV, so the road paint bakes like a model) and the summary line that counts its `baked`.

    python patches/patch_lf_wires_unlit.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_wires_unlit.py --fill
    LF_ROOT=<copy> python patches/patch_lf_wires_unlit.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_wires_unlit"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.193.2", b"0.194.0"
CHANGELOG_HEAD = ("## [0.193.2] - The archetype corpus is walked once a session, and never into a "
                  "directory it discards\n")
BAKE = "packages/exporting/light_bake.py"
TEST = "tests/unit/test_wires_unlit.py"
SHA = {BAKE: "62dba96d73388f14"}

DEF_OLD = "def mark_imports(export_dir: Path, spawned=()) -> dict:\n"
DEF_NEW = (
    "#: OBJs a site ships that are NOT lit by the bake (0.194.0): Lot 0.119.0's\n"
    "#: overhead wires, `site_wires_*.obj`, unshaded tubes whose nodes take no GI\n"
    "#: (`gi_mode = 0`) -- a 2 cm wire unwrapped into the lightmap would spend its\n"
    "#: texels on nothing a player sees lit, and its import would make a second UV\n"
    "#: for nothing. `mark_imports` lists them under `unlit` and leaves their\n"
    "#: sidecars as the engine wrote them.\n"
    'UNLIT_PREFIXES = ("site_wires_",)\n'
    "\n\n"
    "def mark_imports(export_dir: Path, spawned=()) -> dict:\n")
OUT_OLD = ('    out = {"baked": [], "dynamic": [], "spawned": [], "spawned_unmatched": [], '
           '"unreadable": []}\n')
OUT_NEW = ('    out = {"baked": [], "dynamic": [], "spawned": [], "spawned_unmatched": [], '
           '"unreadable": [],\n'
           '           "unlit": []}\n')
OBJ_OLD = ('        rel = sidecar.with_suffix("").relative_to(export_dir).as_posix()\n'
           '        text = sidecar.read_text(encoding="utf-8")\n'
           '        new, k = re.subn(r"^generate_lightmap_uv2=(?:true|false)$",\n')
OBJ_NEW = ('        rel = sidecar.with_suffix("").relative_to(export_dir).as_posix()\n'
           "        if sidecar.name.startswith(UNLIT_PREFIXES):\n"
           '            out["unlit"].append(rel)\n'
           "            continue\n"
           '        text = sidecar.read_text(encoding="utf-8")\n'
           '        new, k = re.subn(r"^generate_lightmap_uv2=(?:true|false)$",\n')


TEST_LB = "tests/unit/test_light_bake.py"
LB_OLD = ('    assert got == {"baked": ["shell.glb"], "dynamic": ["grill.glb"], "spawned": [],\n'
          '                   "spawned_unmatched": [], "unreadable": ["odd.glb"]}\n')
LB_NEW = ("    # the report's `unlit` (0.194.0): a site's wires, none here\n"
          '    assert got == {"baked": ["shell.glb"], "dynamic": ["grill.glb"], "spawned": [],\n'
          '                   "spawned_unmatched": [], "unreadable": ["odd.glb"], "unlit": []}\n')


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


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.194.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.194.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.194.0.md")
    assert entry.startswith("## [0.194.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LF / TEST).exists(), "already applied"
    p = LF / BAKE
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[BAKE], (BAKE, "is not the file this patch read", got)
    eol = _eol(raw, BAKE)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    text = _once(text, DEF_OLD, DEF_NEW, "mark_imports' definition")
    text = _once(text, OUT_OLD, OUT_NEW, "mark_imports' report")
    text = _once(text, OBJ_OLD, OBJ_NEW, "the OBJ loop")
    new_test = _src("test_wires_unlit.py.txt")
    lb = LF / TEST_LB
    lb_raw = lb.read_bytes()
    lb_eol = _eol(lb_raw, TEST_LB)
    lb_text = _once(lb_raw.decode("utf-8").replace("\r\n", "\n"), LB_OLD, LB_NEW, "the report's test")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    (LF / TEST).write_bytes(new_test.encode("utf-8"))
    lb.write_bytes(lb_text.replace("\n", lb_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.193.2 -> 0.194.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
