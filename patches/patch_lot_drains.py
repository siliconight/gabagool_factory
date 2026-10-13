"""Lot 0.120.0: the street's drains -- manhole covers and storm inlets (factory roadmap 179, filed by the
walker 2026-10-04; the rules read at source in `docs/reference/STREET_DRAINS.md`).

Anchored edits, each asserted once, nothing written until all of them matched:
  lot.py                     `_outdoor_nodes` stands the drains after the wires, with the art only
  site_drains.py             NEW (`lot_drains/site_drains.py.txt`)
  tests/test_site_drains.py  NEW (`lot_drains/test_site_drains.py.txt`)
CHANGELOG and VERSION from `lot_drains/CHANGELOG_0.120.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`.

Read before it was written: `site_furniture` (the hydrant's corner rule, `corner_key`, `_clear_of_cuts`,
`HYDRANT_MIN_SPACING`, a piece's `size`), `site_streets` (`Road`, `Kerb`, `Cut`, `approaches`, a kerb's
`offset` and the band's road-side edge), `lot._marking_meshes` and `site_poles.wire_meshes` (an OBJ a
cell beside the scene, the heights: the road's top `ROAD_THICK`, the paint's `MARKING_Y + SURFACE_TIER
/ 2`, the band's `SIDEWALK_H`), the scene writer's `files` (any OBJ declared as a Mesh by its name),
Level Factory's bake (`light_bake.mark_imports`: every OBJ but `site_wires_*` lightmapped), and Zoo's
README on floaters (proud 3 mm, a 4 mm skirt). Every file LF.

    python patches/patch_lot_drains.py --results-pending
    (python -m pytest -q in lot)
    python patches/patch_lot_drains.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_drains.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_drains"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_PLAN": "result_plan.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.119.2", b"Lot 0.120.0"
CHANGELOG_HEAD = "## 0.119.2 - the wires' pixel floor is written as a float, so a scene reads it\n"
SHA = {"lot.py": "bb4cb71010f253b7"}
NEW = {"site_drains.py": "site_drains.py.txt", "tests/test_site_drains.py": "test_site_drains.py.txt"}

HOOK_OLD = ("            files.update(wf)\n"
            "\n"
            "    # THE SHOP SIGNS. A lit cabinet over each door, on the facade that\n")
HOOK_NEW = ("            files.update(wf)\n"
            "\n"
            "    # THE DRAINS (0.120.0, `site_drains`, factory roadmap 179): a manhole cover\n"
            "    # at every junction and along a long run, a storm inlet a corner, and the\n"
            "    # odd lid in the sidewalk behind one -- flush, without collision, and with\n"
            "    # the art only, as the wires are: a candidate's greybox lot carries none.\n"
            "    if cover_refs:\n"
            "        import site_drains\n"
            "        drains = site_drains.plan(street_roads, site_spec.get(\"cover\") or [])\n"
            "        db, ds, df = site_drains.meshes(drains, ROAD_THICK,\n"
            "                                        MARKING_Y + SURFACE_TIER / 2.0, SIDEWALK_H)\n"
            "        body += db\n"
            "        sub += ds\n"
            "        if files is not None:\n"
            "            files.update(df)\n"
            "        print(\"[lot] drains: %d manhole cover(s), %d inlet(s), %d sidewalk lid(s)\" % tuple(\n"
            "            sum(1 for d in drains if d[\"kind\"] == k) for k in (\"manhole\", \"inlet\", \"walk_cover\")))\n"
            "\n"
            "    # THE SHOP SIGNS. A lit cabinet over each door, on the facade that\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.120.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.120.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.120.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.120.0 - "), entry[:40]
    if not DRAFT:
        left = entry
        for key in RESULTS if PENDING else ():
            left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LOT / rel).exists(), ("already applied", rel)
    p = LOT / "lot.py"
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA["lot.py"], ("lot.py is not the file this patch read", got)
    eol = _eol(raw, "lot.py")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(HOOK_OLD) == 1, ("the hook's anchor", text.count(HOOK_OLD))
    text = text.replace(HOOK_OLD, HOOK_NEW)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    p.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for rel, data in news.items():
        (LOT / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.119.2 -> 0.120.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
