"""Level Factory 0.174.0: the backdrop beyond the plate's edge ships as MultiMeshes (roadmap 228,
step E). See `lf_backdrop/CHANGELOG_0.174.0.md`.

Anchored edits, each asserted to match exactly once, nothing written until all of them did:
  packages/exporting/export.py          `backdrop_spec` beside the dressing's inputs; step 2.8
                                        ships the backdrop after the dressing
  apps/cli/commands/__init__.py         the export leg names the themed site's drawn spec
  packages/exporting/localize.py        the entry scene instances `*_backdrop.tscn` too
  new  packages/exporting/backdrop_layer.py
  new  tests/unit/test_backdrop_layer.py
CHANGELOG and VERSION from `CHANGELOG_0.174.0.md`.

    python patch_lf_backdrop.py --results-pending
    python patch_lf_backdrop.py --fill        fill the results from result_*.txt
    LF_ROOT=<copy> python patch_lf_backdrop.py --draft
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_backdrop"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SEEN": "result_seen.txt", "RESULT_PRICE": "result_price.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.173.0", b"0.174.0"
CHANGELOG_HEAD = ("## [0.173.0] - The doctor reads the long-paths flag and weighs the workspace's "
                  "depth\n")

EXPORT = "packages/exporting/export.py"
E_PARAM_ANCHOR = "    clutter_dir: Path | None = None,\n"
E_PARAM = (
    "    #: The backdrop beyond the plate's edge (0.174.0, roadmap 228): the themed\n"
    "    #: site's drawn spec, read for its `backdrop` list and the kit it names.\n"
    "    #: None for a caller with nothing to pass, and then the package is exactly\n"
    "    #: what it was.\n"
    "    backdrop_spec: Path | None = None,\n"
)
E_SHIP_ANCHOR = "    # 3. Source authoring (only in source mode).\n"
E_SHIP = (
    "    # 2.8 THE BACKDROP BEYOND THE PLATE'S EDGE (0.174.0, roadmap 228 step E):\n"
    "    # the themed site's `backdrop` list and the site kit's modules, as\n"
    "    # `<site>_backdrop.tscn` with one MultiMesh a module a side, which the\n"
    "    # entry scene at 3.5 instances beside the level. Needs Godot for the\n"
    "    # mesh extraction, as the dressing does; without one the report says so.\n"
    "    backdrop_report = None\n"
    "    if profile.mode != MODE_PURE_SHELL and backdrop_spec:\n"
    "        from packages.exporting.backdrop_layer import ship_backdrop\n"
    "        backdrop_report = ship_backdrop(\n"
    "            export_dir, backdrop_spec, godot_executable, scratch_root=out_root)\n"
    "        if backdrop_report.get(\"shipped\"):\n"
    "            print(\"[export] backdrop: %s -- %d instances of %d module(s) on their \"\n"
    "                  \"sides, %d draw calls (%s; %d tower)\"\n"
    "                  % (backdrop_report[\"scene\"], backdrop_report[\"instances\"],\n"
    "                     len(backdrop_report[\"modules\"]), backdrop_report[\"draw_calls\"],\n"
    "                     \", \".join(\"%s %d\" % kv for kv in backdrop_report[\"by_side\"].items()),\n"
    "                     backdrop_report[\"towers\"]))\n"
    "        else:\n"
    "            print(\"[export] backdrop NOT shipped: \"\n"
    "                  + \"; \".join(backdrop_report.get(\"reasons\") or [\"?\"]))\n"
    "\n"
)

CLI = "apps/cli/commands/__init__.py"
C_PATH_ANCHOR = "    clutter_dir = jobs_dir / f\"{mission_id}.zoo_clutter_build\" / \"out\"\n"
C_PATH = (
    "    # the backdrop beyond the plate's edge (0.174.0, roadmap 228): the themed\n"
    "    # site's drawn spec, with its `backdrop` list and the kit it names\n"
    "    backdrop_spec = themed_site_dir / \"site.site.drawn.json\"\n"
)
C_CALL_ANCHOR = "        clutter_dir=clutter_dir if clutter_dir.is_dir() else None,\n"
C_CALL = "        backdrop_spec=backdrop_spec if backdrop_spec.is_file() else None,\n"

LOCALIZE = "packages/exporting/localize.py"
L_OLD = (
    "    for dressing in sorted(export_dir.glob(\"*_dressing.tscn\")):\n"
    "        candidates.append(dressing.name)\n"
)
L_NEW = (
    "    for dressing in sorted(export_dir.glob(\"*_dressing.tscn\")):\n"
    "        candidates.append(dressing.name)\n"
    "    # and the backdrop beyond the plate's edge (0.174.0, roadmap 228):\n"
    "    # `<site>_backdrop.tscn`, MultiMeshes of rowhomes and a tower past the\n"
    "    # fence, written by packages/exporting/backdrop_layer.py the same way\n"
    "    for backdrop in sorted(export_dir.glob(\"*_backdrop.tscn\")):\n"
    "        candidates.append(backdrop.name)\n"
)

NEW = {
    "packages/exporting/backdrop_layer.py": "backdrop_layer.py",
    "tests/unit/test_backdrop_layer.py": "test_backdrop_layer.py",
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _text(rel):
    raw = (LF / rel).read_bytes()
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value)
        results[key] = value
    for path, rel in ((LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.174.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        path.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    print("Level Factory 0.174.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.174.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.174.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    text, eol = _text(EXPORT)
    assert "backdrop_spec" not in text, "already patched"
    text = _once(text, E_PARAM_ANCHOR, E_PARAM_ANCHOR + E_PARAM, "the dressing's parameters")
    text = _once(text, E_SHIP_ANCHOR, E_SHIP + E_SHIP_ANCHOR, "step 3's heading")
    writes[LF / EXPORT] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(CLI)
    text = _once(text, C_PATH_ANCHOR, C_PATH_ANCHOR + C_PATH, "the clutter dir")
    text = _once(text, C_CALL_ANCHOR, C_CALL_ANCHOR + C_CALL, "the clutter_dir argument")
    writes[LF / CLI] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(LOCALIZE)
    text = _once(text, L_OLD, L_NEW, "the dressing glob")
    writes[LF / LOCALIZE] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        assert not (LF / rel).exists(), (rel, "already exists")
        writes[LF / rel] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl_text, cl_eol = _text("CHANGELOG.md")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    for p, data in writes.items():
        p.write_bytes(data)
    (LF / "CHANGELOG.md").write_bytes(
        (entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.173.0 -> 0.174.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
