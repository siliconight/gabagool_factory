"""Lot 0.104.0: a heap of filled garbage bags beside each dumpster (roadmap 219 note 11). See
`lot_trash_bags/CHANGELOG_0.104.0.md`.

The walker, 2026-10-09: "need filled black garbage bags stacked near the garbage bins". Zoo
1.93.0 draws the heap (`trash_bags`); this stands one beside each dumpster. Anchored edits, each
edited file pinned by the hash its content had when this patch was written, and one new test:
  site_dumpsters.py  the docstring's paragraph, the bag constants, `plan_bags` and two helpers
  lot.py             `COVER_MATERIALS["trash_bags"]` and the call after the pads
  site_furniture.py  `SPECIES["trash_bags"]`, the genome's default
  new                tests/test_site_trash_bags.py
CHANGELOG and VERSION from `CHANGELOG_0.104.0.md`. Nothing is written until every pin and anchor
matched.

    python patch_lot_trash_bags.py [--suite-pending]
    LOT_ROOT=<copy> python patch_lot_trash_bags.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_trash_bags"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


DOC_OLD = ("A building with no wall that takes one is said (`LOT_DUMPSTER_NO_ROOM`) and\n"
           "gets none: a dumpster in a doorway is worse than no dumpster.\n")
DOC_NEW = DOC_OLD + ("\n"
                     "THE BAGS BESIDE IT (0.104.0). `plan_bags` stands a heap of filled garbage\n"
                     "bags -- Zoo 1.93.0's `trash_bags` -- against the same wall, beside the\n"
                     "container, on its pad where the pad has room. It runs after `site_yards`,\n"
                     "so the heap stands on the pad rather than shrinking it. A dumpster with no\n"
                     "clear side is said (`LOT_BAGS_NO_ROOM`) and gets no bags.\n")
CONST_OLD = "GAP = 0.3\nEDGE = 0.5\n"
CONST_NEW = CONST_OLD + (
    "\n"
    "#: THE BAGS BESIDE IT (0.104.0, roadmap 219 note 11). The walker, 2026-10-09:\n"
    "#: \"need filled black garbage bags stacked near the garbage bins\". Zoo 1.93.0\n"
    "#: draws a heap of them; `plan_bags` stands one beside each dumpster.\n"
    "BAGS = \"trash_bags\"\n"
    "#: The genome's default heap: a row of three filled bags and one on top.\n"
    "BAG_DIMS = (1.4, 0.8, 0.75)\n"
    "#: The heaps Zoo draws (`trash_bag_forms.VARIANTS`); the building's id picks.\n"
    "BAG_VARIANTS = 4\n"
    "#: From the container's side to the heap, along the wall: piled against it,\n"
    "#: and the two boxes still apart.\n"
    "BAG_GAP = 0.1\n"
    "#: From the wall to the heap's back: bags lean on brick. Less than the\n"
    "#: container's `WALL_GAP`, which is there for a lid that swings back.\n"
    "BAG_WALL_GAP = 0.15\n"
    "#: THE HEAP IS TURNED so its width runs out from the wall: a row of bags\n"
    "#: lining the container's side. A full pad (`site_yards`) runs `PAD_ALONG`\n"
    "#: 3.7 m centred on its container, 0.935 m past each side. A heap 0.8 m deep\n"
    "#: and 0.1 m off fits on it with 3.5 cm to spare, and its 1.55 m out from\n"
    "#: the wall stays inside the pad's 1.65 m at the least. Face on, 1.4 m wide,\n"
    "#: it would not fit on the pad at all.\n")
FUNC_OLD = "\n\ndef _say(findings, text):\n"
MAT_OLD = ("                   # the dumpster at a building's service side (site_dumpsters)\n"
           "                   \"dumpster\": \"metal_painted\",\n")
MAT_NEW = MAT_OLD + ("                   # the bags beside it (site_dumpsters.plan_bags, 0.104.0):\n"
                     "                   # Zoo 1.93.0's one option, each bag's colour in its Wear\n"
                     "                   \"trash_bags\": \"plastic\",\n")
CALL_OLD = ("    for f_ in _yard_findings:\n"
            "        print(f\"[lot] {f_}\")\n"
            "    for _p in pylons:\n")
CALL_NEW = ("    for f_ in _yard_findings:\n"
            "        print(f\"[lot] {f_}\")\n"
            "    # THE BAGS BESIDE EACH DUMPSTER (site_dumpsters.plan_bags, 0.104.0):\n"
            "    # a heap of filled garbage bags against the same wall, on its pad\n"
            "    # where the pad has room, clear of every way in, of the paths and\n"
            "    # walks, of what stands and of the markers. After the pads, so the\n"
            "    # heap stands on one rather than shrinking it; before the parking and\n"
            "    # the cover planner, so both see it standing. What stood when the\n"
            "    # pads were laid is what stands now: `_standing_y`.\n"
            "    bags = site_dumpsters.plan_bags(\n"
            "        site_spec, merged, site_streets.roads(site_spec), dumpsters, yards,\n"
            "        list(cover_points.values()), standing=_standing_y,\n"
            "        keep_out=site_furniture.path_corridors(site_spec) + _field_rects,\n"
            "        ground=extent.rect, findings=furniture_findings)\n"
            "    site_spec[\"cover\"].extend(bags)\n"
            "    furniture = furniture + bags\n"
            "    for _p in bags:\n"
            "        print(f\"[lot] LOT_BAGS_PLACED: {_p['name']} at ({_p['at'][0]}, {_p['at'][1]}) \"\n"
            "              f\"yaw {_p['yaw']} beside {_p['dumpster']}, heap {_p['variant']}, \"\n"
            "              + (\"on its pad\" if _p[\"on_pad\"] else \"off its pad\"))\n"
            "    for _p in pylons:\n")
SPECIES_OLD = "    \"dumpster\": (1.83, 1.1, 1.3),\n}\n"
SPECIES_NEW = ("    \"dumpster\": (1.83, 1.1, 1.3),\n"
               "    # THE BAGS BESIDE IT (Zoo 1.93.0), a heap of filled garbage bags\n"
               "    # (`site_dumpsters.plan_bags`). The genome's default: a row of three\n"
               "    # and one on top.\n"
               "    \"trash_bags\": (1.4, 0.8, 0.75),\n"
               "}\n")

#: repo path -> (sha256[:16] of its content with line endings made LF, as read 2026-10-10,
#: [(old, new), ...]). Content, not bytes: git's autocrlf can rewrite a file's endings on a
#: checkout with nothing else changed.
EDITS = {
    "site_dumpsters.py": ("SHA_SD", [(DOC_OLD, DOC_NEW), (CONST_OLD, CONST_NEW),
                                     (FUNC_OLD, "\n\n" + "BAGS_BLOCK" + "def _say(findings, text):\n")]),
    "lot.py": ("SHA_LOT", [(MAT_OLD, MAT_NEW), (CALL_OLD, CALL_NEW)]),
    "site_furniture.py": ("SHA_SF", [(SPECIES_OLD, SPECIES_NEW)]),
}
NEW = {"tests/test_site_trash_bags.py": "test_site_trash_bags.py"}
VERSION_OLD = b"Lot 0.103.0"
CHANGELOG_HEAD = "## 0.103.0 - a parked box truck wears one of Zoo's four fleets\n"


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return "\r\n" if crlf else "\n"


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_OLD, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.104.0.md")
    assert entry.startswith("## 0.104.0 - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    block = _src("bags_block.py.txt")
    assert block.startswith("def plan_bags(") and block.endswith("\n\n\n"), repr(block[-8:])
    writes = {}
    for rel, (sha, pairs) in EDITS.items():
        p = LOT / rel
        raw = p.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        got = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        assert got == PINS[sha], (rel, "is not the file this patch read", got)
        assert "trash_bags" not in text and "plan_bags" not in text, (rel, "already carries the bags")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor count", text.count(old), old[:60])
            text = text.replace(old, new.replace("BAGS_BLOCK", block))
        writes[p] = text.replace("\n", eol).encode("utf-8")
    for rel, name in NEW.items():
        assert not (LOT / rel).exists(), (rel, "already exists")
        writes[LOT / rel] = _src(name).encode("utf-8")
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # every pin and anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).replace("\n", eol).encode("utf-8"))
    (LOT / "VERSION").write_bytes(b"Lot 0.104.0")
    print("Lot 0.103.0 -> 0.104.0" + (" (DRAFT)" if DRAFT else ""))


PINS = {"SHA_SD": "be53b9a163d54cb7", "SHA_LOT": "8494eab0edd2f404", "SHA_SF": "0443f8641c813aa2"}

if __name__ == "__main__":
    main()
