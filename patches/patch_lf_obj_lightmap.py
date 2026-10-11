"""Level Factory 0.177.1: the paint's OBJ meshes bake -- the wavefront sidecar's lightmap UV (roadmap 231,
beside Lot 0.114.0).

One anchored edit in `packages/exporting/light_bake.py` (`mark_imports` asks every `*.obj.import`
for `generate_lightmap_uv2=true`) and two tests appended to `tests/unit/test_light_bake.py`; each
file pinned by hash and each anchor asserted once, nothing written on a miss; the file's own line
endings kept. CHANGELOG and VERSION from `lf_obj_lightmap/CHANGELOG_0.177.1.md`;
`--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lf_obj_lightmap.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_obj_lightmap.py --fill
    LF_ROOT=<copy> python patches/patch_lf_obj_lightmap.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_obj_lightmap"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.177.0", b"0.177.1"
CHANGELOG_HEAD = ("## [0.177.0] - The `block` road grammar: a second side street and a service lane behind "
                  "the row, one loop\n")
SHA = {"packages/exporting/light_bake.py": "f90951fbdbe33897",
       "tests/unit/test_light_bake.py": "3aa9c13538c617f5"}

MARK_OLD = (
    "    out[\"spawned_unmatched\"] = sorted(wanted - set(out[\"spawned\"]) - set(out[\"unreadable\"]))\n"
    "    return out\n")
MARK_NEW = (
    "    # THE PAINT'S MESHES (0.177.1, roadmap 231): Lot 0.114.0 ships a site's road\n"
    "    # markings as an OBJ per paint colour beside site.tscn, so that 227 marking\n"
    "    # submissions are two and the bake still lights them. The wavefront\n"
    "    # importer generates no lightmap UV unless asked -- `generate_lightmap_uv2`,\n"
    "    # read off the engine's own sidecar from a one-quad import -- so each\n"
    "    # sidecar is asked here and the mesh bakes like a model.\n"
    "    for sidecar in sorted(Path(export_dir).rglob(\"*.obj.import\")):\n"
    "        if \".godot\" in sidecar.parts:\n"
    "            continue\n"
    "        rel = sidecar.with_suffix(\"\").relative_to(export_dir).as_posix()\n"
    "        text = sidecar.read_text(encoding=\"utf-8\")\n"
    "        new, k = re.subn(r\"^generate_lightmap_uv2=(?:true|false)$\",\n"
    "                         \"generate_lightmap_uv2=true\", text, flags=re.M)\n"
    "        if k != 1:\n"
    "            out[\"unreadable\"].append(rel)\n"
    "            continue\n"
    "        if new != text:\n"
    "            sidecar.write_text(new, encoding=\"utf-8\", newline=\"\\n\")\n"
    "        out[\"baked\"].append(rel)\n"
    "    out[\"spawned_unmatched\"] = sorted(wanted - set(out[\"spawned\"]) - set(out[\"unreadable\"]))\n"
    "    return out\n")


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
    print("Level Factory 0.177.1's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.177.1.md")
    assert entry.startswith("## [0.177.1] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"

    bp, b_eol, bake = _read("packages/exporting/light_bake.py")
    assert "*.obj.import" not in bake, "already applied"
    bake = _once(bake, MARK_OLD, MARK_NEW, "mark_imports' tail")

    tp, t_eol, tests = _read("tests/unit/test_light_bake.py")
    assert tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + _src("test_obj_lightmap.py.txt")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # Every pin and anchor matched: now write.
    bp.write_bytes(bake.replace("\n", b_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.177.0 -> 0.177.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
