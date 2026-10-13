"""Deli Counter 0.210.0: a rowhome Empty's roof is tar (factory roadmap 240's roofscape; the walker's call
of 2026-10-12, "tar now, coating later"; the grounding is `docs/reference/ROWHOUSE_ROOFS.md`).

Anchored edits, each asserted once, nothing written until all of them matched:
  presets.py                 `empty_rowhome`'s `roof_material` "concrete" -> "tar", the comment saying why
  material_kind.py           a `tar` row in KIND_BY_MATERIAL, after `asphalt`'s
  test_material_kind.py      `_spec_material_ids` reads `roof_material`
  test_empty_roof.py         the roof slot's material is `tar`
  specs/gs_empty_rowhome_*.json   the twelve carry `"roof_material": "tar"` (one field each; `test_empties`
                             holds every one to the preset's own output)
CHANGELOG and VERSION from `dc_rowhome_tar_roof/CHANGELOG_0.210.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. The twelve Empties are rebuilt after (`build.py`, Blender): Level Factory reads
their `build/<id>.slots.json`.

Read before it was written: `empty_rowhome` and `EMPTY_ROWHOMES` (presets.py), `KIND_BY_MATERIAL` and
`SKIN_KINDS` (`tar` already a kind; only `asphalt` named it), `_spec_material_ids` (no `roof_material`),
`test_empty_roof.py`, the twelve specs (each names the field once), and the trace of a slot's material
through Zoo (`skins.KNOWN_KINDS`, `roof.json`'s delco default `tar`) and Pixelcoat (every theme maps
`tar` to `tar_neutral`). Every file LF.

    python patches/patch_dc_rowhome_tar_roof.py --results-pending
    (rebuild the twelve; python -m pytest -q in deli_counter)
    python patches/patch_dc_rowhome_tar_roof.py --fill
    DC_ROOT=<copy> python patches/patch_dc_rowhome_tar_roof.py --draft
"""
import glob
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_rowhome_tar_roof"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILD": "result_build.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.209.1", b"Deli Counter 0.210.0"
CHANGELOG_HEAD = "## [0.209.1] - a stair's column ends at the ceiling of the top floor it serves\n"
SHA = {"presets.py": "46ea704f24ee51f9", "material_kind.py": "51fb69cf49853868",
       "test_empty_roof.py": "d424e8bff0e317da", "test_material_kind.py": "8556048b21c512cc"}

EDITS = {
    "presets.py": [(
        "    # A 1990s rowhouse roof is flat tar, silver-coated -- never its brick.\n"
        "    # Unnamed, the roof slot's style follows the walls (`roofs.roof_slots`).\n"
        "    s[\"roof_material\"] = \"concrete\"\n",
        "    # A rowhouse roof is a membrane over a wood deck -- built-up or modified\n"
        "    # bitumen, the skin kind `tar` -- never its brick; and `tar` is what Zoo's\n"
        "    # roof wears in the delco themes, so a row's Empties match its other\n"
        "    # roofs (0.210.0). It was `concrete`, under a comment calling it \"flat\n"
        "    # tar, silver-coated\": neither had a source. \"Silver\" is the colour of an\n"
        "    # aluminum coating over the membrane; how many 1990s Philadelphia roofs\n"
        "    # carried one has none yet, and the walker held it until one is found\n"
        "    # (the factory's docs/reference/ROWHOUSE_ROOFS.md, roadmap 240).\n"
        "    # Unnamed, the roof slot's style follows the walls (`roofs.roof_slots`).\n"
        "    s[\"roof_material\"] = \"tar\"\n")],
    "material_kind.py": [(
        "    \"asphalt\": \"tar\",\n",
        "    \"asphalt\": \"tar\",\n"
        "    # a rowhome Empty's roof (0.210.0): a membrane, built-up or modified\n"
        "    # bitumen. `asphalt` above is a forecourt's pad\n"
        "    \"tar\": \"tar\",\n")],
    "test_material_kind.py": [(
        "        if spec.get(\"default_material\"):\n"
        "            ids.add(spec[\"default_material\"])\n",
        "        if spec.get(\"default_material\"):\n"
        "            ids.add(spec[\"default_material\"])\n"
        "        # the roof's own material (0.210.0): read nowhere here before, so a\n"
        "        # misspelt one reached the build with a printed warning and no more\n"
        "        if spec.get(\"roof_material\"):\n"
        "            ids.add(spec[\"roof_material\"])\n")],
    "test_empty_roof.py": [(
        "    # the flat roof of a 1990s rowhouse is tar, silver-coated; never its brick\n"
        "    assert roof[\"material\"] == \"concrete\"\n",
        "    # a rowhouse roof is a membrane, the skin kind `tar`; never its brick\n"
        "    # (0.210.0: it was `concrete`, unsourced)\n"
        "    assert roof[\"material\"] == \"tar\"\n")],
}
SPEC_OLD = b'"roof_material": "concrete"'
SPEC_NEW = b'"roof_material": "tar"'


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.210.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.210.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.210.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.210.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        for key in RESULTS if PENDING else ():
            left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, edits in EDITS.items():
        raw = (DC / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, old[:50], text.count(old))
            text = text.replace(old, new)
        writes[DC / rel] = text.encode("utf-8").replace(b"\n", eol)
    specs = sorted(glob.glob(str(DC / "specs" / "gs_empty_rowhome_*.json")))
    assert len(specs) == 12, len(specs)
    for p in specs:
        raw = pathlib.Path(p).read_bytes()
        assert raw.count(SPEC_OLD) == 1, (p, raw.count(SPEC_OLD))
        writes[pathlib.Path(p)] = raw.replace(SPEC_OLD, SPEC_NEW)
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    writes[cl] = (entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol)
    # every anchor matched: now write
    for path, data in writes.items():
        path.write_bytes(data)
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.209.1 -> 0.210.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
